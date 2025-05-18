# kg_api_server.py
# API server to extract and visualize a knowledge graph from text.

import asyncio
import os
import re
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from utils.cypher_to_html import visualize_from_cypher_to_html
from utils.neo4j_utils import export_to_neo4j_cypher

# -----------------------------
# Configuration & Initialization
# -----------------------------

# Set your OpenAI API key (ensure this is kept secure in production)
# It's better to load this from environment variables or a config file in a real application
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Initialize the LLM
llm = ChatOpenAI(model='gpt-4o')

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Graph API",
    description="An API to generate knowledge graphs from text and visualize them.",
    version="0.1.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)



class TextRequest(BaseModel):
    text: str
    # Optional: Define allowed node types for the knowledge graph
    # allowed_nodes: list[str] = ["Security", "loans", "assets", "Property Types"]

# -----------------------------
# Neo4j Export Function (Adapted from kg_test.py)
# -----------------------------

# Remove the original export_to_neo4j_cypher function from this file

# -----------------------------
# HTML Visualization from Cypher Function (Adapted from kg_test.py)
# -----------------------------

# Remove the original visualize_from_cypher_to_html function from this file

# -----------------------------
# API Endpoint
# -----------------------------

@app.post("/generate-graph/")
async def generate_graph(request: TextRequest):
    """
    Accepts a text paragraph, processes it to generate a knowledge graph,
    saves it in Cypher format, and generates an HTML visualization.
    """
    print("[DEBUG] Incoming request data:", request)
    documents = [Document(page_content=request.text)]
    
    graph_transformer = LLMGraphTransformer(llm=llm)

    try:
        graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)
    except Exception as e:
        print(f"[DEBUG] Error converting to graph documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error during graph conversion: {e}")

    if not graph_documents:
        print("[DEBUG] No graph documents generated from input text.")
        raise HTTPException(status_code=400, detail="Could not generate graph from the provided text.")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    cypher_file_path = os.path.join(base_dir, "knowledge_graph_neo4j.cypher")
    html_output_path = os.path.join(base_dir, "frontend", "public", "graph_from_api.html")

    export_to_neo4j_cypher(graph_documents, file_path=cypher_file_path)
    visualize_from_cypher_to_html(cypher_file_path, output_html_path=html_output_path)
    html_source = None
    try:
        with open(html_output_path, "r", encoding="utf-8") as f:
            html_source = f.read()
    except Exception as e:
        print(f"[DEBUG] Error reading HTML file: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading HTML file: {e}")

    return {
        "cypher_file": cypher_file_path,
        "html_visualization": html_output_path,
        "html_source": html_source
    }

# -----------------------------
# Serve HTML Visualization File
# -----------------------------

@app.get("/graph-visualization")
async def get_graph_visualization():
    """
    Serves the generated HTML knowledge graph visualization file.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_output_path = os.path.join(base_dir, "graph_from_api.html")
    if not os.path.exists(html_output_path):
        raise HTTPException(status_code=404, detail="Visualization HTML file not found.")
    return FileResponse(html_output_path, media_type="text/html")

# Entry Point for Uvicorn
# -----------------------------

if __name__ == "__main__":
    # Ensure the script is run from the directory where it's located for relative paths to work as expected.
    # Or use absolute paths for file outputs.
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # Example usage with curl:
    # curl -X POST "http://localhost:8000/generate-graph/" \
    # -H "Content-Type: application/json" \
    # -d '{"text": "Marie Curie was a physicist. Her husband Pierre Curie was also a physicist."}'