from ..core import Docupie
from .utils import generate_markdown_document
import os
import logging
logger = logging.getLogger(__name__)

async def convert_file(file_path, model):
    try:
        result = await Docupie(
            file_path=file_path,
            model=model,
            openai_api_key=os.environ.get('OPENAI_API_KEY')
        )
        pages = result['pages']
        file_name = result['fileName']
        total_pages = len(pages)

        markdown = await generate_markdown_document(pages)

        return {
            'markdown': markdown,
            'total_pages': total_pages,
            'file_name': file_name
        }
    except Exception as error:
        logger.error('Error running Docupie core: %s', error)
