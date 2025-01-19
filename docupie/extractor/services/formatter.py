import logging
from ..converter import convert_file
from ..utils import is_pdf_file
from ..utils import convert_to_text
logger = logging.getLogger(__name__)

async def get_markdown(file: str, model: str = None) -> str:
    """
    Extracts markdown content from a PDF.
    
    Args:
        file (str): The PDF file.
        model (str, optional): The LLM model to use.
    
    Returns:
        str: The markdown content.
    
    Raises:
        ValueError: If file is missing or invalid.
    """
    try:
        if not file:
            raise ValueError('File is required.')
        
        if not is_pdf_file(file):
            raise ValueError('File must be a PDF.')

        result = await convert_file(file, model)
        markdown = result.get('markdown')

        if not markdown:
            raise ValueError("Failed to extract markdown.")

        return markdown
    except Exception as error:
        logger.error("Error extracting markdown: %s", error)
        raise

async def get_plain_text(file: str, model: str = None) -> str:
    """
    Extracts plain text from a PDF by converting markdown to text.
    
    Args:
        file (str): The path to the PDF file.
        model (str, optional): The LLM model to use.
    
    Returns:
        str: The plain text content.
    
    Raises:
        Exception: If extraction fails.
    """
    try:
        markdown = await get_markdown(file=file, model=model)
        return convert_to_text(markdown)
    except Exception as error:
        logger.error("Error extracting plain text: %s", error)
        raise

# Formatter dictionary for various formats
formatter = {
    'markdown': get_markdown,
    'plaintext': get_plain_text
}