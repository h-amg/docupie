from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel

class ModelOptions(str, Enum):
    gpt_4o = "gpt-4o"
    gpt_4o_mini = "gpt-4o-mini"
    llava = "llava"
    llama3_2_vision = "llama3.2-vision"

class LLMParams(BaseModel):
    frequency_penalty: Optional[float] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None

class DocumindArgs(BaseModel):
    cleanup: Optional[bool] = None
    concurrency: Optional[int] = None
    file_path: str
    llm_params: Optional[LLMParams] = None
    maintain_format: Optional[bool] = None
    model: Optional[ModelOptions] = None
    openai_api_key: Optional[str] = None
    output_dir: Optional[str] = None
    pages_to_convert_as_images: Optional[Union[int, List[int]]] = None
    temp_dir: Optional[str] = None

class Page(BaseModel):
    content: str
    content_length: int
    page: int

class DocumindOutput(BaseModel):
    completion_time: float
    file_name: str
    input_tokens: int
    output_tokens: int
    pages: List[Page]

class CompletionResponse(BaseModel):
    content: str
    input_tokens: int
    output_tokens: int

class CompletionArgs(BaseModel):
    api_key: str
    image_path: str
    llm_params: Optional[LLMParams] = None
    maintain_format: bool
    model: ModelOptions
    prior_page: str
