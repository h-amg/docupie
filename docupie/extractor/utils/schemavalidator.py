from typing import List, Dict, Union, Any

def validate_schema(schema: List[Dict[str, Any]]) -> Dict[str, Union[bool, List[str]]]:
    """
        Validates the schema format to ensure it meets the required structure.
        
        Args:
            schema: The schema to validate.
            
        Returns:
            Dict containing isValid (boolean) and errors (List[str])
    """
    valid_types = ["string", "number", "array", "object", "boolean", "enum"]
    errors = []
    
    if not isinstance(schema, list):
        errors.append("Schema must be an array.")
        return {"isValid": False, "errors": errors}
    
    def validate_field(field: Dict[str, Any], path: str) -> None:
        if "name" not in field or not isinstance(field["name"], str) or not field["name"].strip():
            errors.append(f'"name" is required and should be a non-empty string at {path}')
        
        if "type" not in field or field["type"] not in valid_types:
            errors.append(f'"type" is required and must be one of {", ".join(valid_types)} at {path}')
        
        if "description" not in field or not isinstance(field["description"], str) or not field["description"].strip():
            errors.append(f'"description" is required and should be a non-empty string at {path}')
        
        # Additional checks for arrays
        if field.get("type") == "array":
            if "children" not in field:
                errors.append(f'"children" property is required for arrays at {path}')
            elif not isinstance(field["children"], list) or not field["children"]:
                errors.append(f'"children" must be a non-empty array at {path}')
            else:
                # Recursively validate each child
                for index, child in enumerate(field["children"]):
                    validate_field(child, f"{path}.children[{index}]")
        
        # Additional checks for enum
        if field.get("type") == "enum":
            if "values" not in field or not isinstance(field["values"], list) or not field["values"]:
                errors.append(f'"values" is required and must be a non-empty array for enum at {path}')
            elif not all(isinstance(value, str) for value in field["values"]):
                errors.append(f'"values" for enum at {path} must be an array of strings')
    
    for index, field in enumerate(schema):
        validate_field(field, f"schema[{index}]")
    
    return {
        "isValid": len(errors) == 0,
        "errors": errors
    }