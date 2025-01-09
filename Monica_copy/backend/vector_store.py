import os
import logging
from typing import List, Dict, Optional
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymilvus import connections, MilvusClient, utility, model as milvus_model
from tqdm import tqdm
from openai import OpenAI

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, collection_name: str = "document_store"):
        """Initialize the vector store with Milvus."""
        # Initialize Milvus connection
        try:
            connections.connect(
                alias="default",
                host="localhost",
                port="19530"
            )
            logger.info("Successfully connected to Milvus")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
            
        self.client = MilvusClient(uri="http://localhost:19530")
        self.collection_name = collection_name
        
        # Initialize OpenAI client for embeddings
        self.openai_client = OpenAI()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )

        # Initialize embedding model
        self.embedding_model = milvus_model.DefaultEmbeddingFunction()

    def __del__(self):
        """Cleanup Milvus connection when object is destroyed."""
        try:
            connections.disconnect("default")
            logger.info("Successfully disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {e}")

    def ensure_collection_exists(self):
        """Ensure collection exists and is properly initialized."""
        try:
            # Drop existing collection if it exists
            if self.client.has_collection(self.collection_name):
                logger.info(f"Dropping existing collection {self.collection_name}")
                self.client.drop_collection(self.collection_name)
                
            # Get dimension from embedding model
            test_dim = len(self.embedding_model.encode_queries(["test"])[0])
            logger.info(f"Creating collection with dimension {test_dim}")
            
            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=test_dim,
                metric_type="IP",
                consistency_level="Strong"
            )
            logger.info(f"Created collection {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def add_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> None:
        """Add documents to the vector store."""
        if not texts:
            return
            
        # Ensure collection exists
        self.ensure_collection_exists()
            
        # Split texts into chunks
        chunks = []
        for text in texts:
            chunks.extend(self.text_splitter.split_text(text))
            
        try:
            # Get embeddings using embedding model
            embeddings = self.embedding_model.encode_queries(chunks)
            logger.info(f"Created embeddings for {len(chunks)} chunks")
            
            # Prepare data for insertion
            data = []
            for i, (text, embedding) in enumerate(zip(chunks, embeddings)):
                data.append({
                    'id': i,
                    'text': text,
                    'vector': embedding  # Embedding model already returns a list
                })
            
            # Insert into Milvus
            logger.info(f"Inserting {len(data)} documents into Milvus")
            self.client.insert(
                collection_name=self.collection_name,
                data=data
            )
            logger.info(f"Successfully inserted {len(data)} documents")
            
        except Exception as e:
            logger.error(f"Error inserting documents: {e}")
            raise

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents."""
        # Ensure collection exists
        self.ensure_collection_exists()
        
        try:
            # Get query embedding using embedding model
            query_embedding = self.embedding_model.encode_queries([query])[0]
            
            # Search in Milvus
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_embedding],
                anns_field="vector",
                param={"metric_type": "IP", "params": {"nprobe": 10}},
                limit=k,
                output_fields=["text"]
            )
            
            # Format results
            formatted_results = []
            for hit in results[0]:
                formatted_results.append({
                    "text": hit.entity.get("text"),
                    "metadata": {},
                    "score": float(hit.score)
                })
                
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def has_documents(self) -> bool:
        """Check if the collection has any documents."""
        try:
            if not self.client.has_collection(self.collection_name):
                return False
            return self.client.get_collection_stats(self.collection_name)["row_count"] > 0
        except Exception as e:
            logger.error(f"Error checking for documents: {e}")
            return False
