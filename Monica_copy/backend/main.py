from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os
import httpx
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    content: str
    role: str = "user"

@app.get("/")
async def root():
    return {"message": "Welcome to Monica API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Initialize API clients
gpt_client = None
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    print(f"openai api key: {openai_api_key}")
    
    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables")
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    print(f"API Key (first 8 chars): {openai_api_key[:8]}...")
    
    gpt_client = OpenAI(
        api_key=openai_api_key,
        http_client=httpx.Client(timeout=httpx.Timeout(60.0))
    )
    
    # Test the client with a simple request
    test_response = gpt_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "system", "content": "Hello"}]
    )
    print("GPT-4 client test successful!")
    logger.info("GPT-4 client initialized and tested successfully")
    
except Exception as e:
    error_message = str(e)
    print(f"Error initializing GPT-4 client: {error_message}")
    print(f"Error type: {type(e).__name__}")
    print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
    logger.error(f"Error initializing GPT-4 client: {str(e)}")
    gpt_client = None

try:
    kimi_api_key = os.getenv("KIMI_API_KEY")
    kimi_base_url = os.getenv("KIMI_BASE_URL")
    if not kimi_api_key or not kimi_base_url:
        raise ValueError("KIMI credentials not found in environment variables")
    
    kimi_client = OpenAI(
        api_key=kimi_api_key,
        base_url=kimi_base_url,
        http_client=httpx.Client(
            base_url=kimi_base_url,
            timeout=httpx.Timeout(60.0)
        )
    )
    logger.info("KIMI client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing KIMI client: {str(e)}")
    kimi_client = None

@app.post("/chat/gpt4o")
async def chat_gpt(message: Message):
    try:
        if not gpt_client:
            raise HTTPException(status_code=503, detail="GPT-4o service not available")

        logger.debug(f"Received GPT-4o request with content: {message.content}")
        print(f"Received GPT-4o request with content: {message.content}")
        print(f"Using base URL: {gpt_client.base_url}")
        print(f"API Key (first 8 chars): {gpt_client.api_key[:8]}...")
        
        try:
            print("Attempting to use GPT-4...")
            messages = [
                {"role": "system", "content": "You are Monica, a helpful and friendly AI assistant. You provide clear, concise, and accurate responses."},
                {"role": "user", "content": message.content}
            ]
            print(f"Messages to send: {messages}")
            
            chat_completion = gpt_client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            
            print(f"Raw API response: {chat_completion}")
            response_content = chat_completion.choices[0].message.content
            logger.debug(f"GPT-4 response: {response_content}")
            print(f"GPT-4 response: {response_content}")
            
            return JSONResponse(content={"content": response_content, "type": "text"})
            
        except OpenAIError as e:
            error_message = str(e)
            print(f"GPT-4 API Error: {error_message}")
            print(f"Error type: {type(e).__name__}")
            print(f"Full error object: {e.__dict__}")
            
            if "Rate limit" in error_message:
                detail = "Rate limit exceeded. Please try again in a moment."
            elif "Incorrect API key" in error_message or "invalid_api_key" in error_message:
                detail = "Invalid API key. Please check your API key configuration."
            elif "model" in error_message.lower():
                detail = "Error with GPT-4 model. Please check if the model name is correct."
            else:
                detail = f"GPT-4 API Error: {error_message}"
            
            logger.error(f"GPT-4 API Error: {error_message}")
            return JSONResponse(
                status_code=500,
                content={"detail": detail}
            )
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
        logger.error(f"GPT-4 Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@app.post("/chat/kimi")
async def chat_kimi(message: Message):
    try:
        if not kimi_client:
            raise HTTPException(status_code=503, detail="KIMI service not available")

        logger.debug(f"Received KIMI request with content: {message.content}")
        
        try:
            chat_completion = kimi_client.chat.completions.create(
                model=os.getenv("KIMI_MODEL", "moonshot-v1-8k"),
                messages=[
                    {"role": "system", "content": "You are Monica, a helpful and friendly AI assistant. You provide clear, concise, and accurate responses."},
                    {"role": "user", "content": message.content}
                ]
            )
            
            response_content = chat_completion.choices[0].message.content
            logger.debug(f"KIMI response: {response_content}")
            
            return JSONResponse(content={"content": response_content, "type": "text"})
            
        except OpenAIError as e:
            logger.error(f"KIMI API Error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"KIMI API Error: {str(e)}"}
            )
            
    except Exception as e:
        logger.error(f"KIMI Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@app.post("/generate/{type}")
async def generate(type: str, prompt: str):
    """
    Generate different types of content based on the type parameter:
    - document
    - mindmap
    - art
    - calendar
    """
    try:
        response = f"Generated {type} for prompt: {prompt}"
        return {"content": response, "type": type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
