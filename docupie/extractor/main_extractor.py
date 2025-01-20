from openai import AsyncOpenAI
import os
import logging
from .utils import autogenerate_schema
from .utils import convert_to_schema
from .converter import convert_file
logger = logging.getLogger(__name__)

openai = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def extract_data(pdf_file_path, schema_definition, model, auto_schema):
    prompt = """
    You are an expert in structured data extraction. Your task is to extract information from unstructured content and transform it into the specified structure. Follow these rules strictly:

    1. Handle Missing or Undetermined Data:
    - If any field's information is missing, unknown, or cannot be determined, return its value as null.
    - **Do not use substitutes such as "unknown," "missing," or any other placeholder for missing or unknown data. The value **must** always be explicitly null.
    """

    try:
        # Convert PDF to markdown
        result = await convert_file(pdf_file_path, model)
        # raise exception if result is None
        if result is None:
            raise Exception("Failed to convert PDF to markdown.")
        markdown = result["markdown"]
        total_pages = result["total_pages"]
        file_name = result["file_name"]
        # Determine which schema to use
        final_schema = schema_definition
        if auto_schema:
            final_schema = await autogenerate_schema(markdown)
            
            if not final_schema:
                raise Exception("Failed to auto-generate schema.")

        # Convert the schema (whether generated or passed) to pydantic
        dynamic_pydantic_schema = convert_to_schema(final_schema)

        completion = await openai.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": markdown},
            ],
            response_format=dynamic_pydantic_schema
        )

        event = completion.choices[0].message.parsed

        return {
            "event": event,
            "total_pages": total_pages,
            "file_name": file_name
        }
    except Exception as error:
        logger.error(f"Error running OpenAI API call: {error}")
        raise error