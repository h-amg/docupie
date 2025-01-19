import os
import random
import shutil
import logging
from datetime import datetime
from typing import List, Dict, Union, Optional
from pathlib import Path
from .utils import (
    convert_file_to_pdf,
    convert_pdf_to_images,
    download_file,
    format_markdown,
    validate_llm_params
)
from .openai import get_completion
from .models import ModelOptions, DocumindArgs, DocumindOutput
logger = logging.getLogger(__name__)

async def documind(
    cleanup: bool = True,
    concurrency: int = 10,
    file_path: str = None,
    llm_params: Dict = None,
    maintain_format: bool = False,
    model: Optional[str] = None,
    openai_api_key: str = "",
    output_dir: Optional[str] = None,
    pages_to_convert_as_images: Union[int, List[int]] = -1,
    temp_dir: str = None
) -> DocumindOutput:
    
    base_url = os.getenv('BASE_URL', 'https://api.openai.com/v1')
    default_model = (
        ModelOptions.LLAVA if base_url != 'https://api.openai.com/v1'
        else ModelOptions.gpt_4o_mini
    ) if model is None else model

    input_token_count = 0
    output_token_count = 0
    prior_page = ""
    aggregated_markdown: List[str] = []
    start_time = datetime.now()

    llm_params = validate_llm_params(llm_params or {})

    # Validators
    if not openai_api_key:
        raise ValueError("Missing OpenAI API key")
    if not file_path:
        raise ValueError("Missing file path")

    # Ensure temp directory exists + create temp folder
    rand = str(random.randint(1000, 9999))
    temp_directory = Path(temp_dir or os.path.expanduser('~/tmp')) / f"documind-file-{rand}"
    os.makedirs(temp_directory, exist_ok=True)

    # Download the PDF. Get file name.
    download_result = download_file(
        file_path=file_path,
        temp_dir=str(temp_directory)
    )
    if not download_result.get('local_path'):
        raise Exception("Failed to save file to local drive")

    extension = download_result['extension']
    local_path = download_result['local_path']

    # Sort the pages_to_convert_as_images list
    if isinstance(pages_to_convert_as_images, list):
        pages_to_convert_as_images.sort()

    # Convert file to PDF if necessary
    if extension != '.png':
        if extension == '.pdf':
            pdf_path = local_path
        else:
            pdf_path = convert_file_to_pdf(
                extension=extension,
                local_path=local_path,
                temp_dir=str(temp_directory)
            )
        # Convert the file to a series of images
        convert_pdf_to_images(
            local_path=pdf_path,
            pages_to_convert=pages_to_convert_as_images,
            temp_dir=str(temp_directory)
        )

    raw_filename = Path(local_path).stem
    file_name = (
        raw_filename.replace(' ', '_')
        .lower()
        [:255]  # Truncate filename to prevent ENAMETOOLONG errors
    )

    # Get list of converted images
    images = [f for f in os.listdir(temp_directory) if f.endswith('.png')]

    async def process_page(image: str) -> Optional[str]:
        nonlocal input_token_count, output_token_count, prior_page
        image_path = os.path.join(temp_directory, image)
        try:
            completion = get_completion(
                api_key=openai_api_key,
                image_path=image_path,
                llm_params=llm_params,
                maintain_format=maintain_format,
                model=default_model,
                prior_page=prior_page
            )
            formatted_markdown = format_markdown(completion.content)
            input_token_count += completion.input_tokens
            output_token_count += completion.output_tokens
            prior_page = formatted_markdown
            return formatted_markdown
        except Exception as error:
            logger.error(f"Failed to process image {image}: {error}")
            raise

    if maintain_format:
        # Process sequentially
        for image in images:
            result = await process_page(image)
            if result:
                aggregated_markdown.append(result)
    else:
        # Process in parallel with concurrency limit
        import asyncio
        from asyncio import Semaphore

        sem = Semaphore(concurrency)
        async def bounded_process_page(image: str, index: int, results: List):
            async with sem:
                result = await process_page(image)
                results[index] = result

        results = [None] * len(images)
        tasks = [
            bounded_process_page(image, i, results)
            for i, image in enumerate(images)
        ]
        await asyncio.gather(*tasks)
        aggregated_markdown.extend(filter(None, results))

    # Write the aggregated markdown to a file
    if output_dir:
        output_path = Path(output_dir) / f"{file_name}.md"
        output_path.write_text('\n\n'.join(aggregated_markdown))

    # Cleanup
    if cleanup:
        shutil.rmtree(temp_directory)

    # Format response
    completion_time = (datetime.now() - start_time).total_seconds() * 1000
    formatted_pages = []
    
    for i, content in enumerate(aggregated_markdown):
        if pages_to_convert_as_images == -1:
            page_number = i + 1
        elif isinstance(pages_to_convert_as_images, list):
            page_number = pages_to_convert_as_images[i]
        else:
            page_number = pages_to_convert_as_images

        formatted_pages.append({
            'content': content,
            'page': page_number,
            'contentLength': len(content)
        })

    return {
        'completionTime': completion_time,
        'fileName': file_name,
        'inputTokens': input_token_count,
        'outputTokens': output_token_count,
        'pages': formatted_pages
    }