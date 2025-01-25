import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from utils.chroma_v_db import validate_file, process_file, list_files_in_db, ChromaVectorStore, remove_file_from_db, query_vector_db
from pydantic_tool_rag_chroma import handle_questions

app = FastAPI(title="Knowledge Base Manager")

# Initialize vector store at module level
vector_store = ChromaVectorStore()

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount React build directory
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins since we're serving frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/files")
async def list_files():
    try:
        # Get all files from vector database
        files = list_files_in_db(vector_store)
        return JSONResponse(content={"success": True, "files": sorted(files)})
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.post("/upload")
async def upload_file(file: UploadFile):
    try:
        print(f"Received file: {file.filename}")
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save the file
        file_path = os.path.join("data", file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate file
        is_valid, error_message = validate_file(file_path)
        if not is_valid:
            os.remove(file_path)  # Clean up invalid file
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": error_message}
            )
        
        # Process file and store in vector database
        success, chunks = process_file(file_path, vector_store)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": f"File {file.filename} uploaded and processed successfully",
                "chunks": chunks
            })
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error processing file {file.filename}"
                }
            )
            
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error uploading file: {str(e)}"}
        )

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    try:
        if remove_file_from_db(filename, vector_store):
            return JSONResponse(content={
                "success": True,
                "message": f"File {filename} deleted successfully"
            })
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": f"File {filename} not found in database"
                }
            )
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error deleting file: {str(e)}"}
        )

@app.post("/query")
async def query_endpoint(request: Request):
    try:
        data = await request.json()
        query = data.get("query")
        
        if not query:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "No query provided"}
            )
        
        # Debug logging
        print(f"\nProcessing query: {query}")
        
        # Use the global vector_store
        global vector_store
        
        # Check if collection exists
        try:
            collection = vector_store.get_collection()
            if collection.count() == 0:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": "No documents found in the database. Please upload some files first."}
                )
        except Exception as ce:
            print(f"Error accessing collection: {str(ce)}")
            # Reinitialize vector store if there's an issue
            vector_store = ChromaVectorStore()
        
        # Get relevant documents
        raw_response = query_vector_db(query, None, vector_store)
        docs_data = json.loads(raw_response)
        
        if not docs_data.get('success'):
            return JSONResponse(
                status_code=500,
                content=docs_data
            )
        
        # Create context from relevant documents
        context = "\n\n".join([
            f"Document {i+1}:\n{doc['text']}"
            for i, doc in enumerate(docs_data.get('documents', []))
        ])
        
        # Use handle_questions to generate a response
        answer = await handle_questions(
            query=query,
            context=context
        )
        
        # Extract the main answer text from findings
        findings = answer.get('findings', {})
        
        # Keep the structured answer if it's a dictionary
        if isinstance(findings, dict):
            main_answer = findings
        elif isinstance(findings, list):
            # If findings is a list, join all items
            main_answer = "\n".join(map(str, findings))
        else:
            # If findings is a string or other type
            main_answer = str(findings)
        
        # Prepare the response with both the answer and source documents
        response_data = {
            'success': True,
            'query': query,
            'answer': main_answer,
            'reflection': answer.get('reflection', {}),
            'confidence': answer.get('confidence', 0),
            'documents': docs_data.get('documents', [])
        }
        
        # Debug logging
        print(f"Generated response: {response_data}")
        
        # Ensure proper encoding of Chinese characters
        return JSONResponse(
            content=response_data,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except json.JSONDecodeError as je:
        print(f"JSON decode error: {str(je)}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Invalid JSON in request"}
        )
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error processing query: {str(e)}"}
        )

@app.get("/{path:path}", response_class=HTMLResponse)
async def catch_all(path: str):
    # Only serve index.html for non-API routes
    if not path.startswith(("files/", "query", "upload")):
        with open("frontend/build/index.html", "r") as f:
            return f.read()
    else:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Not found"}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
