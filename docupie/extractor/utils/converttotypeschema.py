from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel, create_model
def convert_to_schema(object_def: List[Dict[str, Any]]) -> BaseModel:
    """
    Converts an array of type definitions into a TypedDict schema.
    Args:
        object_def: List of field definitions.
    Returns:
        A Pydantic BaseModel class representing the schema.
    """
    def create_schema(obj: List[Dict[str, Any]]) -> Dict[str, Any]:
        schema = {}
        
        for item in obj:
            python_type = None
            
            match item['type']:
                case 'string':
                    python_type = (str, ...)
                case 'number':
                    python_type = (float, ...)
                case 'boolean':
                    python_type = (bool, ...)
                case 'array':
                    if item.get('children') and len(item['children']) > 0:
                        array_schema = create_schema(item['children'])
                        nested_model = create_model(f"{item['name']}Item", **array_schema)
                        python_type = (List[nested_model], ...)
                    else:
                        raise ValueError(f"Invalid or unsupported 'array' type definition for {item['name']}")
                case 'object':
                    if item.get('children'):
                        nested_schema = create_schema(item['children'])
                        python_type = (create_model(f"{item['name']}Model", **nested_schema), ...)
                    else:
                        raise ValueError(f"Invalid 'object' type definition for {item['name']}")
                case 'enum':
                    if item.get('values') and isinstance(item['values'], list):
                        enum_dict = {val: val for val in item['values']}
                        enum_class = Enum(item['name'], enum_dict)
                        python_type = (enum_class, ...)
                    else:
                        raise ValueError(f"Invalid 'enum' type definition for {item['name']}")
                case _:
                    raise ValueError(f"Unsupported type '{item['type']}' for field {item['name']}")

            # Note: Python typing doesn't have a direct equivalent to Zod's describe()
            # You might want to use docstrings or field metadata if documentation is needed
            schema[item['name']] = python_type

        return schema

    # Create the root model with the generated schema
    schema = create_schema(object_def)
    return create_model('RootModel', **schema)