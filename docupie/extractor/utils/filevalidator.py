import requests
import logging
from urllib.parse import urlparse
logger = logging.getLogger(__name__)

async def is_valid_file(file: str) -> bool:
    """
    Function to check if a file is valid based on its URL or MIME type
    Args:
        file (str): The URL to the file
    Returns:
        bool: True if the file is valid, False otherwise
    """
    allowed_extensions = ['pdf', 'png', 'jpg', 'jpeg', 'txt', 'docx', 'html']
    allowed_mime_types = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'txt': 'text/plain',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'html': 'text/html',
        'octet-stream': 'binary/octet-stream'
    }

    url_path = urlparse(file).path
    
    # Check if file extension is allowed
    if not any(url_path.lower().endswith(f'.{ext}') for ext in allowed_extensions):
        return False

    # Optional: Check the MIME type if query parameters are used
    try:
        response = requests.head(file)
        content_type = response.headers.get('content-type', '')
        return any(content_type.startswith(mime) for mime in allowed_mime_types.values())
    except Exception as error:
        logger.error(f'Error checking MIME type: {error}')
        return False