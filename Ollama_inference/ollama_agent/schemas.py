from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    message: str
    model: str = "deepseek-r1:32b"

class ChatResponse(BaseModel):
    response: str
    model: str

class ModelInfo(BaseModel):
    name: str
    description: Optional[str] = None

class ModelsResponse(BaseModel):
    models: List[ModelInfo]
