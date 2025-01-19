import logging
from openai import AsyncOpenAI
from typing import List, Dict, Any
import os
from pydantic import BaseModel
from enum import Enum
from typing import Optional
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_schema_fields(fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
        Recursively cleans schema fields by removing empty 'children' arrays.
        
        Args:
            fields: The schema fields to clean.
        
        Returns:
            Cleaned schema fields.
    """
    cleaned_fields = []
    for field in fields:
        field_copy = field.copy()
        if "children" in field_copy and not field_copy["children"]:
            # Remove empty children arrays
            del field_copy["children"]
        elif "children" in field_copy:
            # Recursively clean nested children
            field_copy["children"] = clean_schema_fields(field_copy["children"])
        cleaned_fields.append(field_copy)
    return cleaned_fields

# Define schema using Pydantic
class SchemaFieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    ARRAY = "array"
    OBJECT = "object"

class SchemaField(BaseModel):
    name: str
    type: SchemaFieldType
    description: Optional[str] = None
    children: Optional[List['SchemaField']] = None

class Schema(BaseModel):
    fields: List[SchemaField]

async def autogenerate_schema(markdown: str) -> List[Dict[str, Any]]:
    """
        Generates an auto schema from markdown content.
        
        Args:
            markdown: The markdown content to generate the schema from.
        
        Returns:
            The auto-generated schema.
        
        Raises:
            Exception: If schema generation fails.
    """
    prompt = f"""
        Read the following markdown content and generate a schema of useful structured data that can be extracted from it. Follow these rules strictly:
        - The `children` field **must only be present if the `type` is `object` or `array`. It should never exist for other types.
        - `description` fields should be concise, no longer than one sentence.
        \"\"\"{markdown}\"\"\"
    """

    try:
        # Call OpenAI to generate schema
        completion = await openai.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",  # Use the appropriate model
            messages=[{"role": "user", "content": prompt}],
            response_format=Schema
        )

        # Parse and clean the schema
        event = completion.choices[0].message.parsed
        cleaned_fields = clean_schema_fields(event.fields)

        return cleaned_fields

    except Exception as error:
        logger.error(f"Error auto generating schema: {error}")
        raise