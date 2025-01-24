from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse
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

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def get_upload_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Knowledge Base Manager</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            .upload-section {
                margin-bottom: 20px;
                padding: 20px;
                border: 2px dashed #ccc;
                border-radius: 4px;
                text-align: center;
            }
            .file-list {
                margin-top: 20px;
            }
            .file-list h2 {
                color: #444;
            }
            #fileList {
                list-style: none;
                padding: 0;
            }
            #fileList li {
                padding: 10px;
                background-color: #f8f9fa;
                margin-bottom: 5px;
                border-radius: 4px;
            }
            .status {
                margin-top: 10px;
                padding: 10px;
                border-radius: 4px;
            }
            .success {
                background-color: #d4edda;
                color: #155724;
            }
            .error {
                background-color: #f8d7da;
                color: #721c24;
            }
            button {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
            input[type="file"] {
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Knowledge Base Manager</h1>
            
            <div class="upload-section">
                <h2>Upload File</h2>
                <input type="file" id="fileInput" accept=".txt,.pdf">
                <button onclick="uploadFile()">Upload</button>
                <div id="status"></div>
            </div>
            
            <div class="file-list">
                <h2>Files in Knowledge Base</h2>
                <ul id="fileList"></ul>
            </div>
        </div>

        <script>
            // Load file list on page load
            window.onload = updateFileList;

            function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const statusDiv = document.getElementById('status');
                
                if (!fileInput.files.length) {
                    showStatus('Please select a file first', false);
                    return;
                }

                const file = fileInput.files[0];
                const formData = new FormData();
                formData.append('file', file);

                statusDiv.innerHTML = 'Uploading...';
                
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showStatus(data.message, true);
                        updateFileList();
                        fileInput.value = ''; // Clear the file input
                    } else {
                        showStatus(data.message, false);
                    }
                })
                .catch(error => {
                    showStatus('Error uploading file: ' + error, false);
                });
            }

            function showStatus(message, isSuccess) {
                const statusDiv = document.getElementById('status');
                statusDiv.className = 'status ' + (isSuccess ? 'success' : 'error');
                statusDiv.textContent = message;
            }

            function updateFileList() {
                fetch('/files')
                .then(response => response.json())
                .then(data => {
                    const fileList = document.getElementById('fileList');
                    fileList.innerHTML = '';
                    data.files.forEach(file => {
                        const li = document.createElement('li');
                        li.textContent = file;
                        fileList.appendChild(li);
                    });
                })
                .catch(error => {
                    console.error('Error fetching file list:', error);
                });
            }
        </script>
    </body>
    </html>
    """

@app.post("/upload")
async def upload_file(file: UploadFile):
    try:
        print(f"Received file: {file.filename}")
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save the file
        file_path = os.path.join("data", file.filename)
        
        # Validate file extension first
        is_valid, error_message = validate_file(file_path)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=error_message
            )
        
        # Check if file already exists
        if os.path.exists(file_path):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} already exists"
            )
        
        # Save uploaded file
        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Process file and store in vector database
        try:
            chunks = process_file(file_path, vector_store)
            if not chunks:
                raise Exception("Failed to process file and store in vector database")
                
            # Get chunk information
            chunk_info = []
            for i, chunk in enumerate(chunks):
                chunk_info.append({
                    "id": i + 1,
                    "text": chunk.get("text", ""),
                    "metadata": chunk.get("metadata", {})
                })
            
            return {
                "success": True,
                "message": f"File {file.filename} uploaded and processed successfully",
                "chunks": chunk_info
            }
            
        except Exception as e:
            # Clean up the saved file if processing fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process file: {str(e)}"
            )
        
    except HTTPException as he:
        # Clean up the file if it was saved
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise he
    except Exception as e:
        # Clean up the file if it was saved
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        print(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

@app.get("/files")
async def list_files():
    try:
        # Get all files from vector database
        files = list_files_in_db(vector_store)
        return {"success": True, "files": sorted(files)}
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{filename:path}")
async def delete_file(filename: str):
    try:
        # Get the full file path
        file_path = os.path.join("data", filename)
        
        # Remove from vector database
        if not remove_file_from_db(filename, vector_store):
            raise HTTPException(status_code=404, detail="File not found in vector database")
        
        # Also remove the file from filesystem if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {"success": True, "message": f"File {filename} deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@app.post("/query")
async def query_endpoint(request: Request):
    try:
        data = await request.json()
        query_text = data.get("query", "")
        context = data.get("context", "")  # Optional context
        
        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is required")
            
        # Use handle_questions for better responses
        response = await handle_questions(query_text, context)
        print("=== got response: =======")
        print(response)
        
        # If there was an error, return it with a 500 status code
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
            
        return response
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
