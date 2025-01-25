import hashlib
import json
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import traceback
import pdfplumber
from pytesseract import image_to_string
from PIL import Image
import PyPDF2
from io import BytesIO
from typing import List, Dict
from tqdm import tqdm

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Constants
CHUNK_SIZE = 1000  # characters
CHUNK_OVERLAP = 200  # characters
INDEX_NAME = "file-embeddings"
EMBEDDING_MODEL = "multilingual-e5-large"

class PineconeVectorStore:
    def __init__(self):
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        self.pc = Pinecone(api_key=api_key)

        # Create index if it doesn't exist
        if INDEX_NAME not in [index.name for index in self.pc.list_indexes()]:
            self.pc.create_index(
                name=INDEX_NAME,
                dimension=1024,  # dimension for multilingual-e5-large
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        
        # Get the index
        self.index = self.pc.Index(INDEX_NAME)

    def get_index(self):
        return self.index

# Reuse the same text extraction functions
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text

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

def extract_text_from_file(file_path):
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext == '.txt':
        encodings = ['utf-8', 'gb18030', 'gbk', 'gb2312', 'big5']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    text = file.read()
                    if any('\u4e00' <= char <= '\u9fff' for char in text):
                        return text
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error reading file: {e}")
                break
    return ""

def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # Adjust chunk end to not split words
        if end < text_length:
            while end < text_length and text[end].isalnum():
                end += 1
            while end > start and not text[end-1].isspace():
                end -= 1
        
        # Get chunk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position for next chunk
        start = end - overlap
        
        # Ensure we make progress
        if start >= text_length:
            break
        if start < 0:
            start = 0
    
    return chunks

def compute_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def generate_embeddings(text_chunks, pc):
    try:
        embeddings = pc.inference.embed(
            model=EMBEDDING_MODEL,
            inputs=text_chunks,
            parameters={
                "input_type": "passage"
            }
        )
        return [e['values'] for e in embeddings]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        traceback.print_exc()
        return None

def store_embeddings_in_db(file_name, text_chunks, embeddings, file_hash, vector_store):
    try:
        # Prepare vectors for Pinecone
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
            vector = {
                'id': f"{file_hash}_{i}",
                'values': embedding,
                'metadata': {
                    'file_name': file_name,
                    'chunk_index': i,
                    'content': chunk,
                    'file_hash': file_hash
                }
            }
            vectors.append(vector)
        
        # Upsert vectors in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            vector_store.get_index().upsert(vectors=batch)
        
        return True
    except Exception as e:
        print(f"Error storing embeddings: {e}")
        traceback.print_exc()
        return False

def query_vector_db(query_text=None, ctx=None, vector_store=None):
    try:
        if not query_text or not vector_store:
            return json.dumps({"error": "Missing query text or vector store"})
        
        # Generate query embedding
        query_embedding = vector_store.pc.inference.embed(
            model=EMBEDDING_MODEL,
            inputs=[query_text],
            parameters={
                "input_type": "query"
            }
        )
        
        # Query Pinecone
        results = vector_store.get_index().query(
            vector=query_embedding[0]['values'],
            top_k=5,
            include_values=False,
            include_metadata=True
        )
        
        # Format results
        formatted_results = {
            "query": query_text,
            "results": []
        }
        
        for match in results.matches:
            formatted_results["results"].append({
                "file_name": match.metadata["file_name"],
                "content": match.metadata["content"],
                "score": match.score
            })
        
        return json.dumps(formatted_results, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error querying vector database: {e}")
        traceback.print_exc()
        return json.dumps({"error": str(e)})

def display_results(results: Dict):
    if isinstance(results, str):
        results = json.loads(results)
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return
    
    print(f"\nQuery: {results['query']}")
    print("\nResults:")
    for i, result in enumerate(results["results"], 1):
        print(f"\n{i}. File: {result['file_name']}")
        print(f"   Score: {result['score']:.4f}")
        print(f"   Content: {result['content'][:200]}...")

def get_file_chunks(file_name: str, vector_store):
    try:
        # Query Pinecone for all chunks of the file
        results = vector_store.get_index().query(
            vector=[0] * 1024,  # Dummy vector for multilingual-e5-large dimension
            filter={"file_name": file_name},
            include_metadata=True,
            top_k=10000  # Large number to get all chunks
        )
        
        chunks = []
        for match in results.matches:
            chunks.append({
                "content": match.metadata["content"],
                "chunk_index": match.metadata["chunk_index"]
            })
        
        # Sort chunks by index
        chunks.sort(key=lambda x: x["chunk_index"])
        return chunks
    except Exception as e:
        print(f"Error getting file chunks: {e}")
        return []

def get_db_contents(vector_store):
    try:
        # Get index stats
        stats = vector_store.get_index().describe_index_stats()
        
        # Query for all vectors
        results = vector_store.get_index().query(
            vector=[0] * 1024,  # Dummy vector for multilingual-e5-large dimension
            top_k=stats.total_vector_count,
            include_metadata=True
        )
        
        contents = {}
        for match in results.matches:
            file_name = match.metadata["file_name"]
            if file_name not in contents:
                contents[file_name] = {
                    "chunks": [],
                    "file_hash": match.metadata["file_hash"]
                }
            contents[file_name]["chunks"].append({
                "content": match.metadata["content"],
                "chunk_index": match.metadata["chunk_index"]
            })
        
        return contents
    except Exception as e:
        print(f"Error getting database contents: {e}")
        return {}

def list_files_in_db(vector_store):
    try:
        contents = get_db_contents(vector_store)
        return list(contents.keys())
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def remove_file_from_db(file_name: str, vector_store):
    try:
        # Get file chunks to find their IDs
        chunks = get_file_chunks(file_name, vector_store)
        if not chunks:
            return False
        
        # Delete vectors by file name filter
        vector_store.get_index().delete(
            filter={"file_name": file_name}
        )
        
        return True
    except Exception as e:
        print(f"Error removing file: {e}")
        return False

def validate_file(file_path: str):
    allowed_extensions = {'.txt', '.pdf'}
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    if file_ext not in allowed_extensions:
        return False, f"Unsupported file type: {file_ext}"
    
    return True, ""

def process_file(file_path, vector_store):
    # Validate file
    is_valid, error_message = validate_file(file_path)
    if not is_valid:
        print(error_message)
        return False
    
    try:
        file_name = os.path.basename(file_path)
        print(f"\nProcessing {file_name}...")
        
        # Extract text
        text = extract_text_from_file(file_path)
        if not text:
            print("No text could be extracted from the file")
            return False
        
        # Split text into chunks
        text_chunks = split_text(text)
        if not text_chunks:
            print("No chunks were generated from the text")
            return False
        
        # Generate embeddings
        embeddings = generate_embeddings(text_chunks, vector_store.pc)
        if not embeddings:
            print("Failed to generate embeddings")
            return False
        
        # Compute file hash
        file_hash = compute_file_hash(file_path)
        
        # Store in vector database
        success = store_embeddings_in_db(file_name, text_chunks, embeddings, file_hash, vector_store)
        
        if success:
            print(f"Successfully processed {file_name}")
            return True
        else:
            print(f"Failed to store embeddings for {file_name}")
            return False
            
    except Exception as e:
        print(f"Error processing file: {e}")
        traceback.print_exc()
        return False

def handle_view_contents(vector_store):
    try:
        contents = get_db_contents(vector_store)
        if not contents:
            print("No documents found in the vector database")
            return
        
        print("\nDocuments in the vector database:")
        for file_name, data in contents.items():
            print(f"\nFile: {file_name}")
            print(f"Hash: {data['file_hash']}")
            print(f"Number of chunks: {len(data['chunks'])}")
            
            # Display first chunk as preview
            if data['chunks']:
                print("\nFirst chunk preview:")
                print(data['chunks'][0]['content'][:200] + "...")
    
    except Exception as e:
        print(f"Error viewing contents: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    vector_store = PineconeVectorStore()
    
    # Example usage
    process_file("/Users/fcfu/PycharmProjects/LLM_playground/FC_RAG/data/项链.txt", vector_store)
    query_results = query_vector_db("谁的项链", None, vector_store)
    display_results(query_results)
