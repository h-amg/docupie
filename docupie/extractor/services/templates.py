import os
import json
from pathlib import Path

# Get the current file's directory
current_dir = Path(__file__).parent
templates_directory = current_dir.parent / 'templates'

def list_templates():
    """
    Lists all available templates.
    Returns:
        list[str]: Array of template names.
    """
    return [
        file.stem  # stem removes the extension
        for file in templates_directory.glob('*.json')
    ]

def get_template(name: str) -> dict:
    """
    Retrieves a specific template.
    Args:
        name (str): The name of the template.
    Returns:
        dict: The template content.
    Raises:
        FileNotFoundError: If the template is not found.
    """
    template_path = templates_directory / f"{name}.json"
    if not template_path.exists():
        raise FileNotFoundError(f'Template "{name}" not found')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Export available templates as a namespace
class Templates:
    list = list_templates
    get = get_template

templates = Templates()