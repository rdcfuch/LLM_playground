from pydantic import BaseModel
from typing import Optional, List

class LLMConfig(BaseModel):
    model_name: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None

class AgentRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7

class AgentResponse(BaseModel):
    response: str
    tokens_used: int
    success: bool

class MCPConfig(BaseModel):
    host: str
    port: int
    timeout: Optional[int] = 30

class APIResponse(BaseModel):
    status: str
    data: Optional[AgentResponse] = None
    error: Optional[str] = None