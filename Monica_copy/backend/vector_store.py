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
            # Check if collection exists
            if self.client.describe_collection(self.collection_name):
                logger.info(f"Collection {self.collection_name} already exists")
                return
                
            # Get dimension from embedding model
            test_dim = len(self.embedding_model.encode_queries(["test"])[0])
            logger.info(f"Creating collection with dimension {test_dim}")
            
            # Create collection schema
            schema = {
                "fields": [
                    {
                        "name": "id",
                        "dtype": "Int64",
                        "description": "Primary key",
                        "is_primary": True,
                        "auto_id": True
                    },
                    {
                        "name": "text",
                        "dtype": "VarChar",
                        "description": "Document text",
                        "max_length": 65535
                    },
                    {
                        "name": "vector",
                        "dtype": "FloatVector",
                        "description": "Text embedding",
                        "dim": test_dim
                    },
                    {
                        "name": "source",
                        "dtype": "VarChar",
                        "description": "Source file name",
                        "max_length": 255
                    },
                    {
                        "name": "type",
                        "dtype": "VarChar",
                        "description": "File type",
                        "max_length": 10
                    },
                    {
                        "name": "file_id",
                        "dtype": "VarChar",
                        "description": "File identifier",
                        "max_length": 36
                    }
                ],
                "description": "Document store for text embeddings"
            }
            
            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                schema=schema
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
        chunk_metadata = []
        for i, text in enumerate(texts):
            text_chunks = self.text_splitter.split_text(text)
            chunks.extend(text_chunks)
            # Replicate metadata for each chunk if provided
            if metadata and i < len(metadata):
                chunk_metadata.extend([metadata[i]] * len(text_chunks))
            else:
                chunk_metadata.extend([{}] * len(text_chunks))
            
        try:
            # Get embeddings using embedding model
            embeddings = self.embedding_model.encode_queries(chunks)
            logger.info(f"Created embeddings for {len(chunks)} chunks")
            
            # Prepare data for insertion
            data = []
            for i, (text, embedding, meta) in enumerate(zip(chunks, embeddings, chunk_metadata)):
                entry = {
                    'id': i,
                    'text': text,
                    'vector': embedding.tolist(),  # Ensure embedding is a list
                    'source': meta.get('source', ''),
                    'type': meta.get('type', ''),
                    'file_id': meta.get('file_id', '')
                }
                data.append(entry)
            
            # Insert into Milvus
            self.client.insert(
                collection_name=self.collection_name,
                data=data
            )
            logger.info(f"Successfully inserted {len(data)} documents into Milvus")
            
            # Create index if it doesn't exist
            try:
                # Check if index exists
                indexes = self.client.list_indexes(self.collection_name)
                if not any(index.index_name == "vector_index" for index in indexes):
                    index_params = {
                        "metric_type": "IP",
                        "index_type": "IVF_FLAT",
                        "params": {"nlist": 1024}
                    }
                    self.client.create_index(
                        collection_name=self.collection_name,
                        field_name="vector",
                        index_name="vector_index",
                        index_params=index_params
                    )
                    logger.info("Created index for vector field")
            except Exception as e:
                logger.error(f"Error creating index: {e}")
                # Continue even if index creation fails - the data is still inserted
                pass
            
            try:
                # Load collection into memory
                self.client.load_collection(self.collection_name)
                logger.info("Loaded collection into memory")
            except Exception as e:
                logger.error(f"Error loading collection: {e}")
                # Continue even if loading fails
                pass
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
            
    def delete_by_metadata(self, metadata: Dict) -> None:
        """Delete documents matching the given metadata."""
        try:
            # Ensure collection exists
            if not self.client.describe_collection(self.collection_name):
                raise ValueError("Collection does not exist")

            # Build the expression for metadata matching
            expr = " and ".join([f"{k} == '{v}'" for k, v in metadata.items()])
            logger.info(f"Querying documents with expression: {expr}")
            
            # First query to get matching document IDs
            results = self.client.query(
                collection_name=self.collection_name,
                filter=expr,
                output_fields=["id"]
            )
            
            if not results:
                logger.warning(f"No documents found matching metadata: {metadata}")
                return
                
            # Get the IDs
            ids = [str(r['id']) for r in results]
            logger.info(f"Found {len(ids)} documents to delete")
            
            if not ids:
                logger.warning("No document IDs found to delete")
                return
                
            # Delete by IDs
            self.client.delete(
                collection_name=self.collection_name,
                pks=ids
            )
            
            logger.info(f"Successfully deleted {len(ids)} documents matching metadata: {metadata}")
            
        except Exception as e:
            logger.error(f"Error deleting documents by metadata: {e}")
            raise
            
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents."""
        # Ensure collection exists
        if not self.client.describe_collection(self.collection_name):
            raise ValueError("Collection does not exist")
            
        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode_queries([query])[0]
            
            # Search in Milvus
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_embedding],
                field_name="vector",
                index_name="vector_index",
                limit=k,
                param={
                    "metric_type": "IP",
                    "params": {"nprobe": 10}
                },
                output_fields=["text", "source", "type", "file_id"]  # Include metadata fields
            )
            
            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    result = {
                        'text': hit.entity.get('text', ''),
                        'score': hit.score,
                        'metadata': {
                            'source': hit.entity.get('source'),
                            'type': hit.entity.get('type'),
                            'file_id': hit.entity.get('file_id')
                        }
                    }
                    formatted_results.append(result)
                    
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def has_documents(self) -> bool:
        """Check if there are any documents in the collection."""
        try:
            if not self.client.describe_collection(self.collection_name):
                return False
                
            stats = self.client.get_collection_stats(self.collection_name)
            return int(stats["row_count"]) > 0
            
        except Exception as e:
            logger.error(f"Error checking for documents: {e}")
            return False
