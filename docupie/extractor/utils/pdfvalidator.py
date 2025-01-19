from urllib.parse import urlparse
import requests
import logging
import re
logger = logging.getLogger(__name__)

def is_pdf_file(file: str) -> bool:
    """
    Function to check if a file is a PDF based on its URL or MIME type
    Args:
        file (str): The URL to the file
    Returns:
        bool: True if the file is a PDF, false otherwise
    """
    url_path = urlparse(file).path
    pdf_extension_regex = r'\.pdf$'
    
    # Check if file ends with .pdf
    if re.search(pdf_extension_regex, url_path, re.IGNORECASE):
        return True
    
    # Optional: Check the MIME type if query parameters are used
    try:
        response = requests.head(file)
        content_type = response.headers.get('content-type')
        return content_type == 'application/pdf'
    except Exception as error:
        logger.error(f'Error checking MIME type: {error}')
        return False