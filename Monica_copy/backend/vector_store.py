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
        # Initialize Milvus connection with persistence configuration
        try:
            connections.connect(
                alias="default",
                host="localhost",
                port="19530",
                # Add persistence configuration
                db_name="default",
                user="root",
                password="milvus",
                enable_persistent=True,
                persistent_path="/var/lib/milvus"  # Default Milvus data path
            )
            logger.info("Successfully connected to Milvus")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
            
        self.client = MilvusClient(
            uri="http://localhost:19530",
            token="root:milvus"  # Add authentication
        )
        self.collection_name = collection_name
        
        # Initialize OpenAI client for embeddings
        self.openai_client = OpenAI()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Increased for more context
            chunk_overlap=200,  # Increased overlap for better context preservation
            length_function=len,
            separators=["\n\n", "\n", "。", ".", "!", "?", ";", ",", " "]  # Added more separators
        )

        # Initialize embedding model
        self.embedding_model = milvus_model.DefaultEmbeddingFunction()
        
        # Ensure collection exists and is properly configured
        self.ensure_collection_exists()

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
                # Load the collection to ensure it's ready for operations
                self.client.load_collection(self.collection_name)
                return
                
            # Get dimension from embedding model
            test_dim = len(self.embedding_model.encode_queries(["test"])[0])
            logger.info(f"Creating collection with dimension {test_dim}")
            
            # Create collection schema with persistence settings
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
                        "max_length": 255
                    }
                ],
                "enable_dynamic_field": True
            }
            
            # Create collection with persistence configuration
            self.client.create_collection(
                collection_name=self.collection_name,
                schema=schema,
                consistency_level="Strong"  # Ensure strong consistency
            )
            
            # Create index for vector field
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            self.client.create_index(
                collection_name=self.collection_name,
                field_name="vector",
                index_params=index_params
            )
            
            # Load collection into memory
            self.client.load_collection(self.collection_name)
            logger.info(f"Successfully created and loaded collection {self.collection_name}")
            
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
        try:
            # Ensure collection exists and is loaded
            if not self.client.describe_collection(self.collection_name):
                raise ValueError("Collection does not exist")
                
            # Load collection if not already loaded
            try:
                self.client.load_collection(self.collection_name)
                logger.info("Collection loaded successfully")
            except Exception as e:
                logger.error(f"Error loading collection: {e}")
                raise
                
            # Get query embedding
            try:
                query_embedding = self.embedding_model.encode_queries([query])[0].tolist()
                logger.info("Generated query embedding successfully")
            except Exception as e:
                logger.error(f"Error generating query embedding: {e}")
                raise
            
            # Search in Milvus with improved parameters
            logger.info("Searching in Milvus")
            search_params = {
                "metric_type": "IP",
                "params": {
                    "nprobe": 16,  # Increased for better recall
                    "ef": 64       # Search scope
                }
            }
            
            # Search with more results initially
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_embedding],
                output_fields=["text", "source", "type", "file_id"],
                search_params=search_params,
                limit=k * 2  # Get more results initially for better filtering
            )
            
            if not results:
                logger.warning("No results found for query")
                return []
                
            # Format results with improved filtering
            formatted_results = []
            seen_texts = set()  # To avoid near-duplicate chunks
            
            for hits in results:
                for hit in hits:
                    # Extract entity data
                    entity = hit.get('entity', {})
                    if not entity or not all(field in entity for field in ["text", "source", "type", "file_id"]):
                        logger.warning(f"Skipping hit due to missing fields: {hit}")
                        continue
                    
                    # Skip if too similar to already included texts
                    text = entity["text"].strip()
                    if text in seen_texts:
                        continue
                        
                    # Skip if score is too low
                    score = float(hit["distance"])
                    if score < 0.5:  # Adjust threshold as needed
                        logger.debug(f"Skipping result with low score: {score}")
                        continue
                        
                    result = {
                        'text': text,
                        'score': score,
                        'metadata': {
                            'source': entity["source"],
                            'type': entity["type"],
                            'file_id': entity["file_id"]
                        }
                    }
                    formatted_results.append(result)
                    seen_texts.add(text)
                    
                    # Stop if we have enough good results
                    if len(formatted_results) >= k:
                        break
                        
                if len(formatted_results) >= k:
                    break
            
            logger.info(f"Found {len(formatted_results)} relevant documents")
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
