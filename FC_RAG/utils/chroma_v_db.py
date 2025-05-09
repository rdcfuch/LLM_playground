import hashlib
import json
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import traceback
import pdfplumber
from pytesseract import image_to_string
from PIL import Image
import PyPDF2
from io import BytesIO
from typing import List, Dict
import uuid
import unicodedata
import re

# Load environment variables
load_dotenv()

# Constants
VECTOR_DB_DIR = "vector_db"
CHUNK_SIZE = 1000  # characters
CHUNK_OVERLAP = 200  # characters
EMBEDDING_MODEL = "text-embedding-ada-002"

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get absolute path for vector database
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
VECTOR_DB_DIR = os.path.join(PROJECT_DIR, "FC_RAG", "vector_db")

# Create vector database directory if it doesn't exist
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
print(f"Vector database directory: {VECTOR_DB_DIR}")

class ChromaVectorStore:
    def __init__(self):
        # Initialize vector database with persistence
        self.chroma_client = chromadb.PersistentClient(
            path=VECTOR_DB_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                is_persistent=True,
                allow_reset=True,
            )
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="file_embeddings_v2",
            metadata={
                "hnsw:space": "cosine",  # Use cosine similarity
            }
        )
    
    def get_collection(self):
        return self.collection

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
        # Try UTF-8 first, then Chinese encodings
        encodings = ['utf-8', 'utf-8-sig', 'gb18030', 'gbk', 'gb2312', 'big5']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    text = file.read()
                    # Normalize Unicode characters to ensure consistent representation
                    text = unicodedata.normalize('NFKC', text)
                    print(f"\nDebug - Successfully read with {encoding} encoding")
                    print(f"Debug - Extracted text length: {len(text)} characters")
                    print(f"Debug - First 100 chars: {text[:100]}")
                    return text
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not decode file with any known encoding")
    elif file_ext == '.md':
        # Try UTF-8 first, then Chinese encodings
        encodings = ['utf-8', 'utf-8-sig', 'gb18030', 'gbk', 'gb2312', 'big5']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    text = file.read()
                    # Normalize Unicode characters to ensure consistent representation
                    text = unicodedata.normalize('NFKC', text)
                    print(f"\nDebug - Successfully read with {encoding} encoding")
                    print(f"Debug - Extracted text length: {len(text)} characters")
                    print(f"Debug - First 100 chars: {text[:100]}")
                    return text
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not decode file with any known encoding")
    else:
        raise ValueError(f"Unsupported file extension: {file_ext}")


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

    # Normalize text to ensure consistent handling of Chinese characters
    text = unicodedata.normalize('NFKC', text)
    
    # Split text into sentences, preserving Chinese punctuation
    sentence_endings = r'[.!?。！？\n]'
    sentences = []
    current = ""
    
    for char in text:
        current += char
        if re.search(sentence_endings, char):
            sentences.append(current.strip())
            current = ""
    if current:
        sentences.append(current.strip())

    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence_size = len(sentence)
        
        if current_size + sentence_size <= chunk_size:
            current_chunk.append(sentence)
            current_size += sentence_size
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_size = sentence_size
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
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
    """
    Generate embeddings for text chunks using OpenAI's API
    Args:
        text_chunks: List of text chunks to generate embeddings for
    Returns:
        list: List of embeddings or None if error
    """
    if not text_chunks:
        print("Error: No text chunks provided")
        return None
        
    embeddings = []
    try:
        for chunk in text_chunks:
            if not isinstance(chunk, str):
                print(f"Error: Invalid chunk type {type(chunk)}")
                continue
                
            if not chunk.strip():
                print("Warning: Empty chunk, skipping")
                continue
                
            try:
                response = client.embeddings.create(
                    input=chunk,
                    model=EMBEDDING_MODEL,
                )
                embeddings.append(response.data[0].embedding)
            except Exception as e:
                print(f"Error generating embedding for chunk: {str(e)}")
                continue
                
        if not embeddings:
            print("Error: No embeddings were generated")
            return None
            
        return embeddings
        
    except Exception as e:
        print(f"Error in generate_embeddings: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return None


# Store embeddings in the vector database
def store_embeddings_in_db(file_name, text_chunks, embeddings, file_hash, vector_store):
    """Store embeddings in the vector database"""
    try:
        # First, remove any existing entries for this file
        vector_store.get_collection().delete(where={"file_name": file_name})
        
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
            # Normalize Unicode characters for consistent representation
            normalized = unicodedata.normalize('NFKC', chunk)
            encoded_chunks.append(normalized)
        
        # Store the chunks and their embeddings
        vector_store.get_collection().add(
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
def query_vector_db(query_text=None, ctx=None, vector_store=None):
    """
    Query the vector database for relevant documents
    Args:
        query_text: Text to search for
        ctx: RunContext object from pydantic_ai
        vector_store: ChromaVectorStore instance
    Returns:
        str: JSON string with search results
    """
    try:
        # Generate embedding for query
        query_embedding = generate_embeddings([query_text])[0]
        
        # Query the collection
        results = vector_store.get_collection().query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        # Format results
        documents = []
        for i in range(len(results['ids'][0])):
            doc = {
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if 'distances' in results else None
            }
            documents.append(doc)
        
        # Generate a simple answer based on the found documents
        answer = "Here are the relevant documents I found:"
        
        # Ensure proper encoding of response
        response = {
            'success': True,
            'query': query_text,
            'answer': answer,
            'documents': documents
        }
        
        # Use ensure_ascii=False to properly handle Chinese characters
        return json.dumps(response, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Error querying vector database: {str(e)}"
        print(error_msg)
        return json.dumps({
            'success': False,
            'error': error_msg
        }, ensure_ascii=False)


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
def get_file_chunks(file_name: str, vector_store):
    """
    Get all content chunks for a specific file
    Args:
        file_name: Name of the file to get chunks for
        vector_store: ChromaVectorStore instance
    Returns:
        list: List of chunks and their metadata
    """
    try:
        # Query the collection for all chunks of this file
        results = vector_store.get_collection().get(
            where={"file_name": file_name}
        )
        
        if not results or "documents" not in results:
            return []
            
        # Combine documents and metadata
        chunks = []
        for i, (text, metadata) in enumerate(zip(results["documents"], results["metadatas"])):
            chunks.append({
                "id": i + 1,
                "text": text,
                "metadata": metadata
            })
            
        # Sort chunks by index if available
        chunks.sort(key=lambda x: x["metadata"].get("chunk_index", 0))
        return chunks
        
    except Exception as e:
        print(f"Error getting file chunks: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return []

def get_db_contents(vector_store):
    """
    Get all contents stored in the vector database
    Args:
        vector_store: ChromaVectorStore instance
    Returns:
        dict: A dictionary containing all documents and their metadata
    """
    try:
        # Get all items from the collection
        results = vector_store.get_collection().get()
        
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

def list_files_in_db(vector_store):
    """
    List all unique files stored in the vector database
    Args:
        vector_store: ChromaVectorStore instance
    Returns:
        List[str]: List of unique file names
    """
    try:
        # Get all items in collection
        collection_items = vector_store.get_collection().get()
        
        # Get unique file names
        files = set()
        for metadata in collection_items.get("metadatas", []):
            if metadata.get("file_name"):
                files.add(metadata["file_name"])
                
        return sorted(list(files))
        
    except Exception as e:
        print(f"Error listing files in database: {e}")
        return []

def remove_file_from_db(file_name: str, vector_store):
    """
    Remove a file and its embeddings from the vector database
    Args:
        file_name: Name of the file to remove (e.g., 'example.pdf')
        vector_store: ChromaVectorStore instance
    Returns:
        bool: True if file was found and removed, False otherwise
    """
    try:
        # Get all items in collection
        collection_items = vector_store.get_collection().get()
        
        # Find all IDs associated with this file
        file_ids = []
        for i, metadata in enumerate(collection_items.get("metadatas", [])):
            if metadata.get("file_name") == file_name:
                file_ids.append(collection_items["ids"][i])
                
        if not file_ids:
            print(f"No embeddings found for file: {file_name}")
            return False
            
        # Delete the embeddings
        vector_store.get_collection().delete(ids=file_ids)
        print(f"Successfully removed {len(file_ids)} embeddings for file: {file_name}")
        return True
        
    except Exception as e:
        print(f"Error removing file from database: {e}")
        return False

def validate_file(file_path: str):
    """
    Validate if the file has an allowed extension
    Returns: (is_valid: bool, error_message: str)
    """
    try:
        # Check file extension
        allowed_extensions = {'.txt', '.pdf', '.md'}
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in allowed_extensions:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            
        return True, ""
        
    except Exception as e:
        print(f"Error validating file: {str(e)}")
        return False, str(e)

# Main function to process files and store embeddings
def process_file(file_path, vector_store, progress_callback=None):
    """Process a file and store its embeddings in the vector database"""
    try:
        print(f"\nProcessing file: {file_path}")
        
        # Validate the file
        is_valid, error_message = validate_file(file_path)
        if not is_valid:
            print(f"Error: {error_message}")
            return False, None
        
        if not os.path.exists(file_path):
            print(f"Error: File does not exist")
            return False, None
        
        # Extract text from file
        if progress_callback:
            progress_callback("extracting", 0, "Extracting text from file...")
        text = extract_text_from_file(file_path)
        if not text.strip():
            print("Warning: Extracted text is empty")
            return False, None
            
        print(f"\nDebug - Total extracted text length: {len(text)} characters")
        
        # Split text into chunks
        if progress_callback:
            progress_callback("chunking", 0.2, "Splitting text into chunks...")
        text_chunks = split_text(text)
        if not text_chunks:
            print("Warning: No text chunks generated")
            return False, None
            
        print(f"\nDebug - Generated {len(text_chunks)} chunks")
        
        # Generate embeddings
        if progress_callback:
            progress_callback("embedding", 0.4, "Generating embeddings...")
        embeddings = generate_embeddings(text_chunks)
        if not embeddings:
            print("Warning: No embeddings generated")
            return False, None
            
        print(f"\nDebug - Generated {len(embeddings)} embeddings")
        
        # Compute file hash
        if progress_callback:
            progress_callback("hashing", 0.6, "Computing file hash...")
        file_hash = compute_file_hash(file_path)
        
        # Store in database
        if progress_callback:
            progress_callback("storing", 0.8, "Storing in database...")
        file_name = os.path.basename(file_path)
        store_embeddings_in_db(file_name, text_chunks, embeddings, file_hash, vector_store)
        
        # Get and return the stored chunks
        if progress_callback:
            progress_callback("retrieving", 0.9, "Retrieving stored chunks...")
        chunks = get_file_chunks(file_name, vector_store)
        print(f"\nDebug - Retrieved {len(chunks)} chunks from database")
        return True, chunks
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False, None

def handle_view_contents(vector_store):
    """Handle viewing the contents of the vector database"""
    while True:
        print("\n=== Vector Database Contents ===")
        
        contents = get_db_contents(vector_store)
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
    vector_store = ChromaVectorStore()
    file_paths = ["example.pdf", "example.txt", "example.md"]  # Replace with paths to your files
    for file_path in file_paths:
        process_file(file_path, vector_store)

    # Query example
    query_result = query_vector_db("Is there any termite?", vector_store=vector_store)
    print("Query Results:", json.dumps(query_result, indent=2))
    display_results(json.loads(query_result))
    # if query_result and 'documents' in query_result:
    #     for document in query_result['documents']:
    #         print(document)
    #         print("=======")
    # else:
    #     print("No results found.")
