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
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuration
EMBEDDING_MODEL = "text-embedding-ada-002"
CHUNK_SIZE = 500  # Reduced chunk size for better handling
CHUNK_OVERLAP = 100  # Reduced overlap but maintained proportion

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
    path=VECTOR_DB_DIR,
    settings=Settings(
        anonymized_telemetry=False,
        is_persistent=True,
        allow_reset=True,
    )
)

# Get or create collection with proper encoding settings
collection = chroma_client.get_or_create_collection(
    name="file_embeddings_v2",
    metadata={
        "hnsw:space": "cosine",  # Use cosine similarity
        "encoding": "utf-8"  # Explicitly set UTF-8 encoding
    }
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
    """Extract text from PDF or text file with proper encoding handling"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext == '.txt':
        encodings = ['utf-8', 'gb18030', 'gbk', 'gb2312', 'big5']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    text = file.read()
                    # Verify the text is readable Chinese
                    if any('\u4e00' <= char <= '\u9fff' for char in text):
                        print(f"\nDebug - Successfully read with {encoding} encoding")
                        print(f"Debug - Extracted text length: {len(text)} characters")
                        print(f"Debug - First 100 chars: {text[:100]}")
                        return text
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not decode file with any known Chinese encoding")
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")


# Split text into chunks
def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Split text into overlapping chunks of approximately equal size.
    Args:
        text: Text to split
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks
    Returns:
        list: List of text chunks
    """
    if not text:
        return []
        
    # Clean the text
    text = text.strip().replace('\n\n', '。').replace('\n', '。')
    print(f"\nDebug - Text length after cleaning: {len(text)} characters")
    
    # If text is shorter than chunk_size, return it as a single chunk
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        # Get a chunk of size chunk_size or until the end of text
        end = min(start + chunk_size, text_len)
        
        # If we're not at the end of the text, try to find a good break point
        if end < text_len:
            # Look for the last occurrence of a sentence-ending punctuation
            for punct in ['。', '！', '？', '. ', '! ', '? ']:
                last_punct = text[start:end].rfind(punct)
                if last_punct != -1:
                    end = start + last_punct + len(punct)
                    break
        
        # Add the chunk
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
            print(f"\nDebug - Added chunk {len(chunks)}, length: {len(chunk)} characters")
            print(f"Debug - Chunk start: {chunk[:50]}...")
            print(f"Debug - Chunk end: ...{chunk[-50:]}")
        
        # Move the start pointer, accounting for overlap
        start = end - overlap if end < text_len else text_len
    
    # Post-process: ensure no duplicate chunks and no empty chunks
    chunks = [chunk for chunk in chunks if chunk.strip()]
    print(f"\nDebug - Final number of chunks: {len(chunks)}")
    
    # Verify we haven't lost any text
    total_chars = sum(len(chunk) for chunk in chunks)
    print(f"Debug - Total characters in chunks: {total_chars}")
    print(f"Debug - Original text length: {len(text)}")
    
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
    try:
        # First, remove any existing entries for this file
        collection.delete(where={"file_name": file_name})
        
        # Prepare the data
        ids = [str(uuid.uuid4()) for _ in range(len(text_chunks))]
        metadatas = [
            {
                "file_name": file_name,
                "file_hash": file_hash,
                "chunk_index": i,
                "total_chunks": len(text_chunks)
            }
            for i in range(len(text_chunks))
        ]
        
        # Ensure text chunks are properly encoded
        encoded_chunks = []
        for chunk in text_chunks:
            # Normalize the text to ensure consistent encoding
            normalized = chunk.encode('utf-8').decode('utf-8')
            encoded_chunks.append(normalized)
        
        # Store the chunks and their embeddings
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=encoded_chunks,
            metadatas=metadatas
        )
        
        print(f"\nDebug - Stored {len(encoded_chunks)} chunks for {file_name}")
        print(f"Debug - First chunk preview: {encoded_chunks[0][:100]}")
        
        return True
    except Exception as e:
        print(f"Error storing embeddings: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False


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

# Display search results
def display_results(results: Dict):
    """Display search results in a readable format"""
    if not results:
        print("\nNo results found")
        return
        
    print("\nSearch Results:\n")
    
    for i, (doc, meta, dist) in enumerate(zip(
        results["results"]["documents"],
        results["results"]["metadata"],
        results["results"]["distances"]
    ), 1):
        print(f"\n=== Result {i} (Relevance: {(1-dist)*100:.1f}%) ===\n")
        print(f"From chunk {meta['chunk_index']+1} of {meta['total_chunks']}")
        print("-" * 80)
        print(doc)
        print("-" * 80)
    
    print("\nEnd of results")
    input("\nPress Enter to continue...")

# Display content chunks
def display_chunks(chunks):
    """Display the content chunks in a readable format"""
    if not chunks:
        print("\nNo chunks found")
        return
    
    print("\nContent Chunks:\n")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n=== Chunk {i} ===")
        print("-" * 80)
        
        # Handle both list and dictionary formats
        if isinstance(chunk, dict):
            # Print metadata if available
            if 'metadata' in chunk:
                print("Metadata:")
                for key, value in chunk['metadata'].items():
                    print(f"{key}: {value}")
                print("\nContent:")
            
            # Get content from either 'document' or 'content' key
            content = chunk.get('document', chunk.get('content', ''))
            print(content)
        else:
            print(chunk)
        
        print("-" * 80)
    
    input("\nPress Enter to continue...")

# Get related content chunks
def get_file_chunks(file_name: str):
    """
    Get all content chunks for a specific file
    Args:
        file_name: Name of the file to get chunks for
    Returns:
        list: List of chunks and their metadata
    """
    try:
        # Query the collection for all chunks of this file
        results = collection.get(
            where={"file_name": file_name}
        )
        
        if not results or "documents" not in results:
            return []
            
        # Sort chunks by index
        chunks_with_index = [
            (chunk, meta.get("chunk_index", 0))
            for chunk, meta in zip(results["documents"], results["metadatas"])
        ]
        chunks_with_index.sort(key=lambda x: x[1])  # Sort by chunk_index
        
        # Return just the chunks in order
        return [chunk for chunk, _ in chunks_with_index]
        
    except Exception as e:
        print(f"Error getting file chunks: {str(e)}")
        return []

def get_db_contents():
    """
    Get all contents stored in the vector database
    Returns:
        dict: A dictionary containing all documents and their metadata
    """
    try:
        # Get all items from the collection
        results = collection.get()
        
        if not results or "documents" not in results:
            return {
                "total_documents": 0,
                "documents": []
            }
            
        # Get the documents and their metadata
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        
        # Return the documents directly
        return {
            "total_documents": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        print(f"Error getting database contents: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

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

def validate_file(file_path: str) -> tuple[bool, str]:
    """
    Validate if the file exists and has an allowed extension
    Returns: (is_valid: bool, error_message: str)
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
        
    # Get file extension (convert to lowercase)
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Define allowed extensions
    allowed_extensions = {'.txt', '.pdf'}
    
    if ext not in allowed_extensions:
        return False, f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, ""

# Main function to process files and store embeddings
def process_file(file_path):
    """Process a file and store its embeddings in the vector database"""
    try:
        print(f"\nProcessing file: {file_path}")
        
        # Validate the file
        is_valid, error_message = validate_file(file_path)
        if not is_valid:
            print(f"Error: {error_message}")
            return None
        
        # Extract text from file
        text = extract_text_from_file(file_path)
        if not text.strip():
            print("Warning: Extracted text is empty")
            return None
            
        print(f"\nDebug - Total extracted text length: {len(text)} characters")
        
        # Split text into chunks
        text_chunks = split_text(text)
        if not text_chunks:
            print("Warning: No text chunks generated")
            return None
            
        print(f"\nDebug - Generated {len(text_chunks)} chunks")
        
        # Generate embeddings
        embeddings = generate_embeddings(text_chunks)
        if not embeddings:
            print("Warning: No embeddings generated")
            return None
            
        print(f"\nDebug - Generated {len(embeddings)} embeddings")
        
        # Compute file hash
        file_hash = compute_file_hash(file_path)
        
        # Store in database
        file_name = os.path.basename(file_path)
        store_embeddings_in_db(file_name, text_chunks, embeddings, file_hash)
        
        # Get and return the stored chunks
        chunks = get_file_chunks(file_name)
        print(f"\nDebug - Retrieved {len(chunks)} chunks from database")
        return chunks
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

def handle_view_contents():
    """Handle viewing the contents of the vector database"""
    while True:
        print("\n=== Vector Database Contents ===")
        
        contents = get_db_contents()
        if not contents:
            print("\nNo contents found in database or error occurred")
            input("\nPress Enter to return to main menu...")
            return
        
        print(f"\nTotal Documents: {contents['total_documents']}")
        
        if contents['documents']:
            print("\nOptions:")
            print("1. View document list")
            print("2. View document details")
            print("3. Return to main menu")
            
            choice = input("\nSelect an option (1-3): ")
            
            if choice == "1":
                print("\nDocument List:")
                for i, doc in enumerate(contents['documents'], 1):
                    file_name = doc['metadata'].get('file_name', 'Unknown')
                    print(f"{i}. {file_name}")
                input("\nPress Enter to continue...")
                
            elif choice == "2":
                print("\nEnter the number of the document to view details (1-{len(contents['documents'])})")
                try:
                    doc_num = int(input()) - 1
                    if 0 <= doc_num < len(contents['documents']):
                        doc = contents['documents'][doc_num]
                        print("\nDocument Details:")
                        print(f"ID: {doc['id']}")
                        print(f"File Name: {doc['metadata'].get('file_name', 'Unknown')}")
                        print(f"Hash: {doc['metadata'].get('file_hash', 'Unknown')}")
                        print("\nContent Preview (first 200 characters):")
                        print(doc['text'][:200] + "..." if len(doc['text']) > 200 else doc['text'])
                    else:
                        print("\nInvalid document number")
                except ValueError:
                    print("\nInvalid input")
                input("\nPress Enter to continue...")
                
            elif choice == "3":
                return
            else:
                print("\nInvalid option")
                input("\nPress Enter to continue...")
        else:
            print("\nNo documents found in the database")
            input("\nPress Enter to return to main menu...")

# Example usage
if __name__ == "__main__":
    file_paths = ["example.pdf", "example.txt"]  # Replace with paths to your files
    for file_path in file_paths:
        process_file(file_path)

    # Query example
    query_result = query_vector_db("Is there any termite?")
    print("Query Results:", json.dumps(query_result, indent=2))
    display_results(json.loads(query_result))
    # if query_result and 'documents' in query_result:
    #     for document in query_result['documents']:
    #         print(document)
    #         print("=======")
    # else:
    #     print("No results found.")
