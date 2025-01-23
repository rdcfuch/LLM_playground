import hashlib
import json
import os
import uuid
from dotenv import load_dotenv
import pdfplumber
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from pytesseract import image_to_string
from PIL import Image
import PyPDF2
from io import BytesIO
from typing import List

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuration
EMBEDDING_MODEL = "text-embedding-ada-002"
CHUNK_SIZE = 200

# Get absolute path for vector database
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
VECTOR_DB_DIR = os.path.join(PROJECT_DIR, "FC_RAG", "vector_db")

# Create vector database directory if it doesn't exist
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
print(f"Vector database directory: {VECTOR_DB_DIR}")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize vector database with persistence
chroma_client = chromadb.PersistentClient(
    path=VECTOR_DB_DIR
)

# Get or create collection
collection = chroma_client.get_or_create_collection(
    name="file_embeddings_v2",
    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
)


# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text


# OCR for scanned PDFs
def extract_text_via_ocr(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            pdf = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                img = Image.open(BytesIO(page.extract_image()['data']))
                text += image_to_string(img)
    except Exception as e:
        print(f"Error in OCR: {e}")
    return text


# Extract text from file
def extract_text_from_file(file_path):
    """Extract text from PDF or text file"""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file: {e}")
            return ""
    else:
        print(f"Unsupported file type: {file_path}")
        return ""


# Split text into chunks
def split_text(text, chunk_size=CHUNK_SIZE):
    chunks = []
    words = text.split()
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks


# Generate a unique hash for the file content
def compute_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# Generate vector embeddings
def generate_embeddings(text_chunks):
    embeddings = []
    try:
        for chunk in text_chunks:
            response = client.embeddings.create(
                input=chunk,
                model=EMBEDDING_MODEL,
            )
            embeddings.append(response.data[0].embedding)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
    return embeddings


# Store embeddings in the vector database
def store_embeddings_in_db(file_name, text_chunks, embeddings, file_hash):
    """Store embeddings in the vector database"""
    print(f"\nDebug - Storing embeddings:")
    print(f"File name: {file_name}")
    print(f"Number of chunks: {len(text_chunks)}")
    print(f"Number of embeddings: {len(embeddings)}")
    print(f"File hash: {file_hash}")
    
    # Check if the file hash already exists in metadata
    existing_ids = [
        metadata["chunk_id"]
        for metadata in collection.get()["metadatas"]
        if metadata.get("file_hash") == file_hash
    ]
    if existing_ids:
        print(f"Embeddings for {file_name} already exist in the database.")
        return

    ids = [str(uuid.uuid4()) for _ in range(len(text_chunks))]
    metadatas = [{"file_name": file_name, "chunk_id": i, "file_hash": file_hash} for i in range(len(text_chunks))]
    
    print(f"\nDebug - Adding to collection:")
    print(f"Collection name: {collection.name}")
    print(f"Number of IDs: {len(ids)}")
    print(f"Sample text chunk: {text_chunks[0][:100]}...")
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=text_chunks,
    )
    print(f"Embeddings for {file_name} stored successfully!")


# Query the vector database
def query_vector_db(query_text=None, ctx=None):
    """
    Query the vector database for relevant documents
    Args:
        query_text: Text to search for
        ctx: RunContext object from pydantic_ai
    Returns:
        str: JSON string with search results
    """
    try:
        # Extract query from context if available
        if isinstance(query_text, dict) and 'query' in query_text:
            query_text = query_text['query']
        elif isinstance(query_text, str):
            query_text = query_text
        else:
            query_text = "termite inspection report"
            
        print(f"\nDebug - Query text: {query_text}")
            
        if not query_text:
            return json.dumps({"results": [], "query": ""})
            
        # Get embedding for the query
        query_response = client.embeddings.create(
            input=query_text,
            model=EMBEDDING_MODEL,
        )
        query_embedding = query_response.data[0].embedding
        print(f"Debug - Generated query embedding of size: {len(query_embedding)}")
        
        # Get collection info
        collection_items = collection.get()
        print(f"\nDebug - Collection info:")
        print(f"Number of items: {len(collection_items.get('ids', []))}")
        print(f"Available metadata: {collection_items.get('metadatas', [])}")
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )
        
        print(f"\nDebug - Raw query results:")
        print(json.dumps(results, indent=2))
        
        # Format results as simple types for JSON serialization
        formatted_results = {
            "documents": list(map(str, results["documents"][0])) if results["documents"] else [],
            "metadata": [dict(m) for m in results["metadatas"][0]] if results["metadatas"] else [],
            "distances": [float(d) for d in results["distances"][0]] if results["distances"] else []
        }
        
        # Return JSON string
        return json.dumps({
            "results": formatted_results,
            "query": query_text
        })
        
    except Exception as e:
        print(f"Error querying vector database: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return json.dumps({"results": {"documents": [], "metadata": [], "distances": []}, "query": str(query_text)})

# Main function to process files and store embeddings
def process_file(file_path):
    """Process a file and store its embeddings in the vector database"""
    try:
        print(f"\nDebug - Processing file: {file_path}")
        
        # Extract text from the file
        text = extract_text_from_file(file_path)
        print(f"Extracted text length: {len(text)}")
        if not text:
            print(f"No text could be extracted from {file_path}")
            return False
            
        # Generate a unique hash for the file content
        file_hash = compute_file_hash(file_path)
        print(f"Generated file hash: {file_hash}")
        
        # Split text into chunks
        text_chunks = split_text(text)
        print(f"Generated {len(text_chunks)} text chunks")
        if not text_chunks:
            print(f"No text chunks generated from {file_path}")
            return False
            
        # Generate embeddings
        embeddings = generate_embeddings(text_chunks)
        print(f"Generated {len(embeddings)} embeddings")
        if not embeddings:
            print(f"Failed to generate embeddings for {file_path}")
            return False
            
        # Store in vector database
        store_embeddings_in_db(os.path.basename(file_path), text_chunks, embeddings, file_hash)
        print(f"Successfully processed {file_path}")
        return True
        
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False


def remove_file_from_db(file_name: str) -> bool:
    """
    Remove a file and its embeddings from the vector database
    Args:
        file_name: Name of the file to remove (e.g., 'example.pdf')
    Returns:
        bool: True if file was found and removed, False otherwise
    """
    try:
        # Get all items in collection
        collection_items = collection.get()
        
        # Find all IDs associated with this file
        file_ids = []
        for i, metadata in enumerate(collection_items.get("metadatas", [])):
            if metadata.get("file_name") == file_name:
                file_ids.append(collection_items["ids"][i])
                
        if not file_ids:
            print(f"No embeddings found for file: {file_name}")
            return False
            
        # Delete the embeddings
        collection.delete(ids=file_ids)
        print(f"Successfully removed {len(file_ids)} embeddings for file: {file_name}")
        return True
        
    except Exception as e:
        print(f"Error removing file from database: {e}")
        return False

def list_files_in_db() -> List[str]:
    """
    List all unique files stored in the vector database
    Returns:
        List[str]: List of unique file names
    """
    try:
        # Get all items in collection
        collection_items = collection.get()
        
        # Get unique file names
        files = set()
        for metadata in collection_items.get("metadatas", []):
            if metadata.get("file_name"):
                files.add(metadata["file_name"])
                
        return sorted(list(files))
        
    except Exception as e:
        print(f"Error listing files in database: {e}")
        return []

# Example usage
if __name__ == "__main__":
    file_paths = ["example.pdf", "example.txt"]  # Replace with paths to your files
    for file_path in file_paths:
        process_file(file_path)

    # Query example
    query_result = query_vector_db("Is there any termite?")
    print("Query Results:", json.dumps(query_result, indent=2))
    # if query_result and 'documents' in query_result:
    #     for document in query_result['documents']:
    #         print(document)
    #         print("=======")
    # else:
    #     print("No results found.")
