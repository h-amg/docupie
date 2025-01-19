from ..main_extractor import extract_data
from ..utils import is_valid_file
from ..utils import validate_schema
from .templates import get_template
from typing import Optional, Dict, Any
import logging
logger = logging.getLogger(__name__)

async def extract(
    file: str,
    schema: Optional[Dict] = None,
    template: Optional[str] = None,
    model: Optional[str] = None,
    auto_schema: bool = False
) -> Dict[str, Any]:
    """
    Extracts data from a document based on a provided schema.
    
    Args:
        file: The file path to the document.
        schema: The schema definition for data extraction.
        template: Name of a pre-defined template.
        model: The llm model to use if a base url is set.
        auto_schema: Option to auto-generate the schema.
    
    Returns:
        Dict containing extraction results including pages, extracted data, and file name.
    
    Raises:
        ValueError: If input validation fails or processing errors occur.
    """
    try:
        if not file:
            raise ValueError("File is required.")

        if not await is_valid_file(file):
            raise ValueError("File must be a valid format: PDF, PNG, JPG, TXT, DOCX, or HTML.")

        final_schema = None
        if template:
            final_schema = get_template(template)  # Use pre-defined template
        elif schema:
            is_valid, errors = validate_schema(schema)
            if not is_valid:
                raise ValueError(f"Invalid schema format: {', '.join(errors)}")
            final_schema = schema  # Use custom schema
        elif not auto_schema:
            # If neither schema nor template is provided and auto_schema is not enabled, throw an error
            raise ValueError("You must provide a schema, template, or enable auto_schema.")

        result = await extract_data(file, final_schema, model, auto_schema)

        return {
            "success": True,
            "pages": result['total_pages'],
            "data": result['event'],
            "fileName": result['file_name']
        }
    except Exception as error:
        logger.error("Error processing document: %s", error)
        raise ValueError(f"Failed to process document: {str(error)}")