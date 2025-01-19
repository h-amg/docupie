import base64
from typing import List, Dict, Any, Optional
import requests
import os
from .models import CompletionResponse
from .utils import convert_keys_to_snake_case, encode_image_to_base64
import logging
logger = logging.getLogger(__name__)

def get_completion(
    api_key: str,
    image_path: str,
    llm_params: Dict[str, float],
    maintain_format: bool,
    model: str,
    prior_page: str
) -> CompletionResponse:
    
    valid_models_for_custom_base_url = [
        "llava",
        "llama3.2-vision",
    ]
    valid_models_for_openai = ["gpt-4o", "gpt-4o-mini"]
    base_url = os.getenv("BASE_URL", "https://api.openai.com/v1")

    if base_url != "https://api.openai.com/v1":
        if model not in valid_models_for_custom_base_url:
            raise ValueError(
                f'Invalid model "{model}" for custom base URL. Valid options are: {", ".join(valid_models_for_custom_base_url)}.'
            )
    else:
        if model not in valid_models_for_openai:
            raise ValueError(
                f'Invalid model "{model}" for OpenAI. Valid options are: {", ".join(valid_models_for_openai)}.'
            )

    system_prompt = """
    Convert the following image/document  to markdown. 
    Return only the markdown with no explanation text. Do not include deliminators like '''markdown.
    You must include all information on the page. Do not exclude headers, footers, or subtext.
    """

    # Default system message
    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    # If content has already been generated, add it to context.
    # This helps maintain the same format across pages
    if maintain_format and prior_page and len(prior_page):
        messages.append({
            "role": "system",
            "content": f'Markdown must maintain consistent formatting with the following page: \n\n """{prior_page}"""'
        })

    # Add Image to request
    base64_image = encode_image_to_base64(image_path)
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            }
        ]
    })

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            json={
                "messages": messages,
                "model": model,
                **(convert_keys_to_snake_case(llm_params) if llm_params else {})
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        data = response.json()

        return CompletionResponse(
            content=data["choices"][0]["message"]["content"],
            input_tokens=data["usage"]["prompt_tokens"],
            output_tokens=data["usage"]["completion_tokens"]
        )
    except Exception as err:
        logger.error("Error in OpenAI completion: %s", str(err))
        raise
