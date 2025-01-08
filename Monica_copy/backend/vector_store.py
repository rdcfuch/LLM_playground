import os
import chromadb
import logging
import shutil
from typing import List, Dict, Optional
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str = None, collection_name: str = "document_store"):
        """Initialize the vector store with ChromaDB."""
        if persist_directory is None:
            persist_directory = os.path.join(os.path.dirname(__file__), "data", "chroma")
            
        # Remove existing directory if it exists to avoid schema issues
        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory)
            
        # Create the persist directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create collection with basic settings
        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )

    def load_pdf_directory(self, directory_path: str) -> None:
        """Load and process all PDFs from a directory."""
        # Load PDFs
        loader = PyPDFDirectoryLoader(directory_path)
        documents = loader.load()
        
        # Split documents
        chunks = self.text_splitter.split_documents(documents)
        
        # Prepare for ChromaDB
        texts = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            texts.append(chunk.page_content)
            metadatas.append(chunk.metadata)
            ids.append(f"doc_{i}")
            
        # Add to ChromaDB
        if texts:  # Only add if there are documents
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

    def add_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> None:
        """Add documents to the vector store."""
        if not texts:
            return
            
        # Split texts into chunks
        chunks = []
        for text in texts:
            chunks.extend(self.text_splitter.split_text(text))
            
        # Generate IDs for chunks
        ids = [f"doc_{i}" for i in range(len(chunks))]
        
        # If no metadata provided, create empty metadata for each chunk
        if metadata is None:
            metadata = [{} for _ in chunks]
        else:
            # Replicate metadata for chunks
            expanded_metadata = []
            for i, meta in enumerate(metadata):
                chunk_count = len(self.text_splitter.split_text(texts[i]))
                expanded_metadata.extend([meta.copy() for _ in range(chunk_count)])
            metadata = expanded_metadata
            
        # Add to ChromaDB
        if chunks:  # Only add if there are chunks
            self.collection.add(
                documents=chunks,
                metadatas=metadata,
                ids=ids
            )
        
    def has_documents(self) -> bool:
        """Check if the collection has any documents."""
        try:
            # Try to get one document to check if collection is empty
            result = self.collection.query(
                query_texts=["test"],
                n_results=1
            )
            return len(result['ids'][0]) > 0
        except Exception as e:
            logger.error(f"Error checking documents: {str(e)}")
            return False
            
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for documents similar to the query."""
        if not self.has_documents():
            raise ValueError("No documents found in the collection. Please add documents first.")
            
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i]
            })
            
        return formatted_results

    def clear(self) -> None:
        """Clear all documents from the collection."""
        self.collection.delete()
