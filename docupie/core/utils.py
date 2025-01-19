import base64
import io
import mimetypes
import os
import re
import urllib.parse
from pathlib import Path
from typing import Dict, Union, List, Optional, Any

import pdf2image 
import pytesseract 
import requests
from PIL import Image
from spire.doc import *
from spire.doc.common import *
import logging
logger = logging.getLogger(__name__)

# Default LLM parameters
DEFAULT_LLM_PARAMS = {
    "frequency_penalty": 0,
    "max_tokens": 2000,
    "presence_penalty": 0,
    "temperature": 0,
    "top_p": 1,
}

def validate_llm_params(params: Dict[str, float]) -> Dict[str, float]:
    valid_keys = DEFAULT_LLM_PARAMS.keys()
    
    for key, value in params.items():
        if key not in valid_keys:
            raise ValueError(f"Invalid LLM parameter: {key}")
        if not isinstance(value, (int, float)):
            raise ValueError(f"Value for '{key}' must be a number")
    
    return {**DEFAULT_LLM_PARAMS, **params}

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def format_markdown(text: str) -> str:
    formatted_markdown = text.strip()
    loop_count = 0
    max_loops = 3

    while formatted_markdown.startswith("```markdown") and loop_count < max_loops:
        if formatted_markdown.endswith("```"):
            pattern = r"^```markdown\n([\s\S]*?)\n```$"
            match = re.match(pattern, formatted_markdown)
            
            if match:
                formatted_markdown = match.group(1).strip()
                loop_count += 1
            else:
                break
        else:
            break

    return formatted_markdown

def is_valid_url(string: str) -> bool:
    try:
        result = urllib.parse.urlparse(string)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except ValueError:
        return False

def download_file(file_path: str, temp_dir: str) -> Dict[str, str]:
    base_filename = os.path.basename(file_path.split('?')[0])
    local_path = os.path.join(temp_dir, base_filename)
    
    if is_valid_url(file_path):
        response = requests.get(file_path, stream=True)
        response.raise_for_status()
        
        mimetype = response.headers.get('content-type')
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        import shutil
        shutil.copy2(file_path, local_path)
        mimetype = mimetypes.guess_type(local_path)[0]

    if not mimetype:
        mimetype = mimetypes.guess_type(local_path)[0]

    extension = mimetypes.guess_extension(mimetype) if mimetype else ''
    if not extension:
        if mimetype == 'binary/octet-stream':
            # return the extension of the file path if the mimetype is binary/octet-stream
            extension = Path(local_path).suffix
            if not extension:
                raise ValueError("File extension missing")
        else:
            raise ValueError("File extension missing")

    return {"extension": extension, "local_path": local_path}

def get_text_from_image(buffer: bytes) -> Dict[str, float]:
    try:
        image = Image.open(io.BytesIO(buffer))
        width, height = image.size
        
        # Crop to 150px wide column in center
        crop_width = 150
        left = max(0, (width - crop_width) // 2)
        cropped_image = image.crop((left, 0, left + crop_width, height))
        
        # Get confidence score from Tesseract
        data = pytesseract.image_to_data(cropped_image, output_type=pytesseract.Output.DICT)
        confidences = [float(conf) for conf in data['conf'] if conf != '-1']
        confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {"confidence": confidence}
    except Exception as e:
        logger.error(f"Error during OCR: {e}")
        return {"confidence": 0}

def correct_image_orientation(buffer: bytes) -> bytes:
    image = Image.open(io.BytesIO(buffer))
    rotations = [0, 90, 180, 270]
    
    results = []
    for rotation in rotations:
        rotated = image.rotate(rotation, expand=True)
        buffer_io = io.BytesIO()
        rotated.save(buffer_io, format='PNG')
        confidence = get_text_from_image(buffer_io.getvalue())['confidence']
        results.append({"rotation": rotation, "confidence": confidence})
    
    best_result = max(results, key=lambda x: x['confidence'])
    
    if best_result['rotation'] != 0:
        logger.info(f"Reorienting image {best_result['rotation']} degrees "
                   f"(Confidence: {best_result['confidence']}%).")
        
    corrected = image.rotate(best_result['rotation'], expand=True)
    buffer_io = io.BytesIO()
    corrected.save(buffer_io, format='PNG')
    return buffer_io.getvalue()

def convert_pdf_to_images(local_path: str, 
                         pages_to_convert: Union[int, List[int]], 
                         temp_dir: str) -> List[Dict]:
    try:
        # Convert pages to list if single integer
        if isinstance(pages_to_convert, int):
            pages_to_convert = [pages_to_convert]

        images = pdf2image.convert_from_path(
            local_path,
            dpi=300,
            first_page=abs(min(pages_to_convert)),
            last_page=abs(max(pages_to_convert))
        )

        results = []
        base_filename = Path(local_path).stem
        
        for i, image in enumerate(images, start=min(pages_to_convert)):
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Correct orientation
            corrected_buffer = correct_image_orientation(img_byte_arr)
            
            # Save the image
            padded_page = str(i).zfill(5)
            image_path = os.path.join(temp_dir, f"{base_filename}_page_{padded_page}.png")
            with open(image_path, 'wb') as f:
                f.write(corrected_buffer)
            
            results.append({"page": i, "path": image_path})
            
        return results
    except Exception as e:
        logger.error(f"Error during PDF conversion: {e}")
        raise

def convert_file_to_pdf(extension: str, local_path: str, temp_dir: str) -> str:
    output_filename = Path(local_path).stem + ".pdf"
    output_path = os.path.join(temp_dir, output_filename)
    
    try:
        if extension.lower() in ('.doc', '.docx'):
            # Create a Document object
            document = Document()
            # Load a Word DOCX file
            document.LoadFromFile(local_path)
            # Save the file to a PDF file
            document.SaveToFile(output_path, FileFormat.PDF)
            document.Close()
            return output_path
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
    except Exception as e:
        logger.error(f"Error converting {extension} to .pdf: {e}")
        raise

def camel_to_snake_case(text: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

def convert_keys_to_snake_case(obj: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(obj, dict):
        return obj or {}
    
    return {camel_to_snake_case(key): value for key, value in obj.items()}