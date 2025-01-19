import logging
logger = logging.getLogger(__name__)

async def generate_markdown_document(pages):
    try:
        # Combine all markdown pages into a single string
        markdown_content = "\n\n---\n\n".join(page["content"] for page in pages)
        
        # Return the combined markdown string directly
        return markdown_content
    except Exception as error:
        logger.error(f'Error generating markdown: {error}')
        raise error