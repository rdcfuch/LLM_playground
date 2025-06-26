from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import yaml

# Load MCP configuration
with open("config/mcp_config.yaml", "r") as file:
    mcp_config = yaml.safe_load(file)

app = FastAPI()

class RequestModel(BaseModel):
    prompt: str
    model: str

class ResponseModel(BaseModel):
    response: str

@app.post("/generate", response_model=ResponseModel)
async def generate_response(request: RequestModel):
    # Here you would integrate with the LLM model based on the request
    # For now, we will return a mock response
    return ResponseModel(response=f"Generated response for prompt: {request.prompt} using model: {request.model}")

if __name__ == "__main__":
    uvicorn.run(app, host=mcp_config['host'], port=mcp_config['port'])