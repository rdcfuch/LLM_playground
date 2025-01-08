from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os
import httpx
import logging
import json
from rag_utils import RAGManager
import PyPDF2
from io import BytesIO
import docx
import chardet
import datetime
import re

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG level to see all messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler('app.log')  # Also save to file
    ]
)

# Set debug level for specific loggers
logging.getLogger('rag_utils').setLevel(logging.DEBUG)
logging.getLogger('vector_store').setLevel(logging.DEBUG)
logging.getLogger('ollama_embeddings').setLevel(logging.DEBUG)

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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["X-Progress"]
)

class Message(BaseModel):
    content: str
    role: str = "gpt4"

class KnowledgeBase(BaseModel):
    texts: List[str]
    metadata: Optional[List[Dict]] = None

@app.get("/")
async def root():
    return {"message": "Welcome to Monica API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Initialize API clients
gpt_client = None
kimi_client = None
deepseek_client = None
rag_manager = RAGManager()

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

try:
    deepseek_api_key = os.getenv("DeepSeek_API_KEY")
    deepseek_base_url = os.getenv("DeepSeek_BASE_URL")
    if not deepseek_api_key or not deepseek_base_url:
        raise ValueError("DeepSeek credentials not found in environment variables")
    
    deepseek_client = OpenAI(
        api_key=deepseek_api_key,
        base_url=deepseek_base_url,
        http_client=httpx.Client(
            base_url=deepseek_base_url,
            timeout=httpx.Timeout(60.0)
        )
    )
    logger.info("DeepSeek client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing DeepSeek client: {str(e)}")
    deepseek_client = None

# Global variables to store chat history for each model and service
chat_histories = {
    "kimi": {
        "chat": [],
        "translate": []
    },
    "gpt4o": {
        "chat": [],
        "translate": []
    },
    "deepseek": {
        "chat": [],
        "translate": []
    }
}

def get_messages_for_service(model: str, service: str) -> list:
    return chat_histories[model][service]

def get_system_prompt_for_service(model: str, service: str) -> str:
    if service == "translate":
        if model == "kimi":
            return "你是 Kimi，由 Moonshot AI 提供的人工智能助手。现在你是一个专业的翻译，请将文本翻译成目标语言。只返回翻译结果，不要包含任何解释、标签或引号。Moonshot AI 为专有名词，不可翻译成其他语言。"
        else:
            return "You are a professional translator. Translate the text to the target language. Return ONLY the translation, no explanations, labels, or quotes."
    else:  # chat service
        if model == "kimi":
            return "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"
        elif model == "deepseek":
            return "You are DeepSeek, an AI assistant. You excel at providing helpful, accurate, and safe responses in both English and Chinese. You will decline to answer any questions related to terrorism, discrimination, or inappropriate content."
        else:  # gpt4
            return "You are GPT-4, an AI assistant. You excel at providing helpful, accurate, and safe responses in both English and Chinese. You will decline to answer any questions related to terrorism, discrimination, or inappropriate content."

@app.post("/chat/gpt4o")
async def chat_gpt(message: Message):
    try:
        if not gpt_client:
            raise HTTPException(status_code=503, detail="GPT-4 service not available")

        messages = get_messages_for_service("gpt4o", "chat")
        
        # Initialize with system prompt if this is a new conversation
        if not messages:
            messages.append({
                "role": "system",
                "content": get_system_prompt_for_service("gpt4o", "chat")
            })
        
        # Add user message to history
        messages.append({
            "role": "user",
            "content": message.content
        })

        try:
            chat_completion = gpt_client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            
            response_content = chat_completion.choices[0].message.content
            
            # Add assistant's response to history
            messages.append({
                "role": "assistant",
                "content": response_content
            })
            
            return JSONResponse(content={
                "content": response_content,
                "type": "text"
            })
            
        except OpenAIError as e:
            error_message = str(e)
            print(f"GPT-4 API Error: {error_message}")
            print(f"Error type: {type(e).__name__}")
            print(f"Full error object: {e.__dict__}")
            
            if "Rate limit" in error_message:
                detail = "Rate limit exceeded. Please try again in a moment."
            elif "Incorrect API key" in error_message:
                detail = "Invalid API key. Please check your API key configuration."
            else:
                detail = f"GPT-4 API Error: {error_message}"
            
            logger.error(f"GPT-4 API Error: {error_message}")
            return JSONResponse(
                status_code=500,
                content={"detail": detail}
            )
            
    except Exception as e:
        print(f"Unexpected error in GPT-4 chat: {str(e)}")
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

        messages = get_messages_for_service("kimi", "chat")
        
        # Initialize with system prompt if this is a new conversation
        if not messages:
            messages.append({
                "role": "system",
                "content": get_system_prompt_for_service("kimi", "chat")
            })
        
        # Add user message to history
        messages.append({
            "role": "user",
            "content": message.content
        })

        try:
            chat_completion = kimi_client.chat.completions.create(
                model=os.getenv("KIMI_MODEL", "moonshot-v1-8k"),
                messages=messages
            )
            
            response_content = chat_completion.choices[0].message.content
            
            # Add assistant's response to history
            messages.append({
                "role": "assistant",
                "content": response_content
            })
            
            return JSONResponse(content={
                "content": response_content,
                "type": "text"
            })
            
        except OpenAIError as e:
            error_message = str(e)
            print(f"KIMI API Error: {error_message}")
            print(f"Error type: {type(e).__name__}")
            print(f"Full error object: {e.__dict__}")
            
            if "Rate limit" in error_message:
                detail = "Rate limit exceeded. Please try again in a moment."
            elif "Incorrect API key" in error_message:
                detail = "Invalid API key. Please check your API key configuration."
            else:
                detail = f"KIMI API Error: {error_message}"
            
            logger.error(f"KIMI API Error: {error_message}")
            return JSONResponse(
                status_code=500,
                content={"detail": detail}
            )
            
    except Exception as e:
        print(f"Unexpected error in KIMI chat: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
        logger.error(f"KIMI Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@app.post("/chat/deepseek")
async def chat_deepseek(message: Message):
    try:
        if not deepseek_client:
            raise HTTPException(status_code=503, detail="Deepseek service not available")

        messages = get_messages_for_service("deepseek", "chat")
        
        # Initialize with system prompt if this is a new conversation
        if not messages:
            messages.append({
                "role": "system",
                "content": get_system_prompt_for_service("deepseek", "chat")
            })
        
        # Add user message to history
        messages.append({
            "role": "user",
            "content": message.content
        })

        try:
            chat_completion = deepseek_client.chat.completions.create(
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                messages=messages,
                temperature=0.7
            )
            
            response_content = chat_completion.choices[0].message.content
            
            # Add assistant's response to history
            messages.append({
                "role": "assistant",
                "content": response_content
            })
            
            return JSONResponse(content={
                "content": response_content,
                "type": "text"
            })
            
        except OpenAIError as e:
            error_message = str(e)
            print(f"Deepseek API Error: {error_message}")
            print(f"Error type: {type(e).__name__}")
            print(f"Full error object: {e.__dict__}")
            
            if "Rate limit" in error_message:
                detail = "Rate limit exceeded. Please try again in a moment."
            elif "Incorrect API key" in error_message:
                detail = "Invalid API key. Please check your API key configuration."
            else:
                detail = f"Deepseek API Error: {error_message}"
            
            logger.error(f"Deepseek API Error: {error_message}")
            return JSONResponse(
                status_code=500,
                content={"detail": detail}
            )
            
    except Exception as e:
        print(f"Unexpected error in Deepseek chat: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
        logger.error(f"Deepseek Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@app.post("/chat/translate")
async def translate_text(message: Message):
    try:
        # Check which model to use based on the role field
        if message.role == "kimi":
            if not kimi_client:
                raise HTTPException(status_code=503, detail="KIMI translation service not available")
            client = kimi_client
            model_name = os.getenv("KIMI_MODEL", "moonshot-v1-8k")
        elif message.role == "deepseek":
            if not deepseek_client:
                raise HTTPException(status_code=503, detail="Deepseek translation service not available")
            client = deepseek_client
            model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        else:
            if not gpt_client:
                raise HTTPException(status_code=503, detail="GPT-4 translation service not available")
            client = gpt_client
            model_name = "gpt-4"

        logger.debug(f"Received translation request with content: {message.content}")
        print(f"Received translation request with content: {message.content}")
        print(f"Using model: {model_name}")

        # Get the appropriate message history
        messages = get_messages_for_service(message.role, "translate")

        # Detect language and create appropriate prompt
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in message.content)
        target_lang = "English" if is_chinese else "Chinese"
        
        try:
            # If messages is empty, add the system prompt
            if not messages:
                system_prompt = get_system_prompt_for_service(message.role, "translate")
                messages.append({"role": "system", "content": system_prompt})

            # Add user's message to history
            messages.append({"role": "user", "content": message.content})
            
            print(f"Translation request with history: {messages}")
            
            if message.role == "deepseek":
                # Deepseek specific handling
                chat_completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.3  # Lower temperature for more accurate translations
                )
            else:
                # Default handling for KIMI and GPT-4
                chat_completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages
                )
            
            response_content = chat_completion.choices[0].message.content.strip()
            # Clean up any prefixes like "Translation:" or "Translation (X → Y):"
            response_content = re.sub(r'^Translation.*?:', '', response_content, flags=re.IGNORECASE).strip()
            # Remove any remaining text that looks like a prefix with arrows or colons
            response_content = re.sub(r'^.*?[→:]\s*', '', response_content).strip()
            
            # Add assistant's response to history
            messages.append({"role": "assistant", "content": response_content})
            
            logger.debug(f"Translation response: {response_content}")
            print(f"Translation response: {response_content}")
            
            return JSONResponse(content={
                "content": response_content,
                "type": "text"
            })
            
        except OpenAIError as e:
            error_message = str(e)
            print(f"Translation API Error: {error_message}")
            print(f"Error type: {type(e).__name__}")
            print(f"Full error object: {e.__dict__}")
            
            if "Rate limit" in error_message:
                detail = "Rate limit exceeded. Please try again in a moment."
            elif "Incorrect API key" in error_message:
                detail = "Invalid API key. Please check your API key configuration."
            else:
                detail = f"Translation API Error: {error_message}"
            
            logger.error(f"Translation API Error: {error_message}")
            return JSONResponse(
                status_code=500,
                content={"detail": detail}
            )
            
    except Exception as e:
        print(f"Unexpected error in translation: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
        logger.error(f"Translation Error: {str(e)}")
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

@app.get("/knowledge/files")
async def list_knowledge_files():
    """List all files in the knowledge base."""
    try:
        files = rag_manager.list_files()
        return JSONResponse(content={"files": files})
    except Exception as e:
        logger.error(f"Error listing knowledge base files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.delete("/knowledge/files/{file_id}")
async def delete_knowledge_file(file_id: str):
    """Delete a file from the knowledge base."""
    try:
        logger.info(f"Attempting to delete file with ID: {file_id}")
        if rag_manager.delete_file(file_id):
            logger.info(f"Successfully deleted file with ID: {file_id}")
            return JSONResponse(
                content={"message": f"File {file_id} deleted successfully"},
                headers={
                    'X-Progress': '100',
                    'X-Progress-Text': 'Batches: 100%|#####| Complete'
                }
            )
        else:
            logger.warning(f"File not found with ID: {file_id}")
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@app.post("/knowledge/add")
async def add_knowledge(knowledge: KnowledgeBase):
    """Add new documents to the knowledge base."""
    try:
        rag_manager.add_knowledge(knowledge.texts, knowledge.metadata)
        return JSONResponse(content={"message": "Knowledge added successfully"})
    except Exception as e:
        logger.error(f"Error adding knowledge: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error adding knowledge: {str(e)}"}
        )

@app.post("/knowledge/query")
async def query_knowledge(message: Message):
    """Query the knowledge base and get a response using RAG."""
    try:
        if not message.content:
            return JSONResponse(
                status_code=400,
                content={"error": "Please provide a question to search the knowledge base."}
            )
            
        try:
            # Check if knowledge base is enabled
            if not rag_manager.has_knowledge():
                return JSONResponse(
                    status_code=400,
                    content={"error": "Cannot enable knowledge base: No files available. Please upload files first."}
                )
                
            # Get response from RAG
            response = rag_manager.generate_response(message.content)
            
            return JSONResponse(content={
                "content": response,
                "type": "text"
            })
            
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={"error": str(e)}
            )
            
    except Exception as e:
        logger.error(f"Error querying knowledge base: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error querying knowledge base: {str(e)}"}
        )

@app.post("/knowledge/clear")
async def clear_knowledge():
    """Clear all documents from the knowledge base."""
    try:
        rag_manager.clear_knowledge()
        return JSONResponse(content={"message": "Knowledge base cleared successfully"})
    except Exception as e:
        logger.error(f"Error clearing knowledge base: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error clearing knowledge base: {str(e)}"}
        )

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file bytes."""
    pdf_file = BytesIO(file_bytes)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_bytes):
    """Extract text from DOCX file bytes."""
    doc = docx.Document(BytesIO(file_bytes))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_txt(file_bytes):
    """Extract text from TXT file bytes with encoding detection."""
    result = chardet.detect(file_bytes)
    encoding = result['encoding'] or 'utf-8'
    return file_bytes.decode(encoding)

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload multiple files and add their contents to the knowledge base."""
    try:
        results = []
        for file in files:
            logger.info(f"Processing file: {file.filename}")
            content = await file.read()
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            # Extract text based on file type
            try:
                if file_ext == '.pdf':
                    text = extract_text_from_pdf(content)
                elif file_ext == '.docx':
                    text = extract_text_from_docx(content)
                elif file_ext == '.txt':
                    text = extract_text_from_txt(content)
                else:
                    logger.warning(f"Skipping unsupported file type: {file_ext} for file: {file.filename}")
                    continue
                    
                if not text.strip():
                    logger.warning(f"No text content extracted from file: {file.filename}")
                    continue
                    
                logger.info(f"Successfully extracted text from {file.filename}")
                
            except Exception as e:
                logger.error(f"Error extracting text from {file.filename}: {str(e)}")
                continue
                
            # Create metadata for the file
            metadata = {
                'source': file.filename,
                'type': file_ext[1:],  # Remove the dot
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            try:
                # Add to knowledge base with metadata
                file_id = rag_manager.add_knowledge(
                    [text],  # Pass as a single document
                    [metadata]  # Pass metadata for the document
                )
                
                logger.info(f"Successfully added {file.filename} to knowledge base with ID: {file_id}")
                
                results.append({
                    "filename": file.filename,
                    "file_id": file_id,
                    "type": file_ext[1:],
                    "timestamp": metadata['timestamp']
                })
                
            except Exception as e:
                logger.error(f"Error adding {file.filename} to knowledge base: {str(e)}")
                continue
        
        if not results:
            return JSONResponse(
                status_code=400,
                content={"message": "No files were successfully processed"}
            )
            
        return JSONResponse(content={
            "message": f"Successfully uploaded {len(results)} files",
            "files": results
        })
        
    except Exception as e:
        logger.error(f"Error in upload_files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading files: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
