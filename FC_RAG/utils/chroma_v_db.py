import hashlib
import json
import os
import uuid
from dotenv import load_dotenv
import pdfplumber
import openai
import chromadb
from chromadb.config import Settings
from pytesseract import image_to_string
from PIL import Image
import PyPDF2
from io import BytesIO

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuration
EMBEDDING_MODEL = "text-embedding-ada-002"  # Adjust model version if necessary
CHUNK_SIZE = 200  # Adjust chunk size for splitting text
VECTOR_DB_DIR = "vector_db"  # Directory for Chroma DB

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Initialize vector database
chroma_client = chromadb.Client(
    Settings(
        persist_directory=VECTOR_DB_DIR  # Directory for Chroma DB persistence
    )
)
collection = chroma_client.get_or_create_collection(name="pdf_embeddings")


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


# Split text into chunks
def split_text(text, chunk_size=CHUNK_SIZE):
    chunks = []
    words = text.split()
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks


# Generate a unique hash for the PDF content
def compute_pdf_hash(pdf_path):
    hash_md5 = hashlib.md5()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# Generate vector embeddings
def generate_embeddings(text_chunks):
    embeddings = []
    try:
        for chunk in text_chunks:
            response = openai.Embedding.create(
                input=chunk,
                model=EMBEDDING_MODEL,
            )
            embeddings.append(response['data'][0]['embedding'])
    except Exception as e:
        print(f"Error generating embeddings: {e}")
    return embeddings


# Store embeddings in the vector database
def store_embeddings_in_db(pdf_name, text_chunks, embeddings, pdf_hash):
    # Check if the PDF hash already exists in metadata
    existing_ids = [
        metadata["chunk_id"]
        for metadata in collection.get()["metadatas"]
        if metadata.get("pdf_hash") == pdf_hash
    ]
    if existing_ids:
        print(f"Embeddings for {pdf_name} already exist in the database.")
        return

    ids = [str(uuid.uuid4()) for _ in range(len(text_chunks))]
    metadatas = [{"pdf_name": pdf_name, "chunk_id": i, "pdf_hash": pdf_hash} for i in range(len(text_chunks))]
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=text_chunks,
    )
    print(f"Embeddings for {pdf_name} stored successfully!")


# Query the vector database
def query_vector_db(query_text, top_k=5):
    try:
        query_embedding_response = openai.Embedding.create(
            input=query_text,
            model=EMBEDDING_MODEL,
        )
        query_embedding = query_embedding_response['data'][0]['embedding']
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        return results
    except Exception as e:
        print(f"Error querying vector database: {e}")
        return []


# Main function to process PDF and store embeddings
def process_pdf(pdf_path):
    pdf_name = os.path.basename(pdf_path)
    pdf_hash = compute_pdf_hash(pdf_path)
    print(f"Processing: {pdf_name} (Hash: {pdf_hash})")

    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if not text:
        text = extract_text_via_ocr(pdf_path)

    if not text:
        print(f"Failed to extract text from {pdf_name}")
        return

    # Preprocess text and generate embeddings
    text_chunks = split_text(text)
    embeddings = generate_embeddings(text_chunks)

    # Store in vector database
    store_embeddings_in_db(pdf_name, text_chunks, embeddings, pdf_hash)


# Example usage
if __name__ == "__main__":
    pdf_files = ["example.pdf"]  # Replace with paths to your PDF files
    for pdf_file in pdf_files:
        process_pdf(pdf_file)

    # Query example
    query_result = query_vector_db("Is there any termite?")
    print("Query Results:", json.dumps(query_result, indent=2))
    # if query_result and 'documents' in query_result:
    #     for document in query_result['documents']:
    #         print(document)
    #         print("=======")
    # else:
    #     print("No results found.")
