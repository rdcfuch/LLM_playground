from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import requests
import json
from schemas import ChatMessage, ChatResponse, ModelsResponse, ModelInfo

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

OLLAMA_API_BASE = "http://localhost:11434"

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        response = requests.post(
            f"{OLLAMA_API_BASE}/api/generate",
            json={
                "model": message.model,
                "prompt": message.message,
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json()
        return ChatResponse(response=result["response"], model=message.model)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models", response_model=ModelsResponse)
async def get_models():
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/api/tags")
        response.raise_for_status()
        models = response.json()
        return ModelsResponse(
            models=[ModelInfo(name=model["name"]) for model in models["models"]]
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return FileResponse("static/index.html")

def start():
    """Launched with `python main.py` at root level"""
    print("Starting server at http://localhost:8000")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["./"]
    )

if __name__ == "__main__":
    start()
