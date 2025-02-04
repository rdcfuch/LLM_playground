import json
import psycopg2
from typing import List, Dict, Any
from openai import OpenAI
import requests
import uuid
import sys
import os
import time
import logging
import ollama

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class EmbeddingAgent:
    def __init__(self, config: Config = None):
        """
        Initialize the EmbeddingAgent with configuration from config.py.
        
        :param config: Optional Config instance. If not provided, creates a new one.
        """
        self.config = config or Config().load_config()
        self.embedding_service = self._initialize_embedding_service()
        self.db_connection = self._initialize_db_connection()

    def _initialize_embedding_service(self):
        """Initialize the embedding service based on the configuration."""
        service_type = self.config.embedding.service_type

        if service_type == "openai":
            if not self.config.embedding.openai_api_key:
                raise ValueError("OpenAI API key must be provided in config")
            self.openai_client = OpenAI(api_key=self.config.embedding.openai_api_key)
            return self._get_openai_embedding
            
        elif service_type == "ollama":
            if not self.config.embedding.ollama_embedding_url:
                raise ValueError("Ollama base URL must be provided in config")
            return self._get_ollama_embedding
            
        else:
            raise ValueError(f"Unsupported embedding service: {service_type}. Supported types are 'openai' and 'ollama'")

    def _initialize_db_connection(self):
        """Initialize the PostgreSQL database connection."""
        try:
            conn = psycopg2.connect(
                host=self.config.database.host,
                port=self.config.database.port,
                database=self.config.database.database,
                user=self.config.database.user,
                password=self.config.database.password
            )
            return conn
        except Exception as e:
            raise ConnectionError(f"Failed to connect to the database: {e}")

    def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI's API."""
        text = text.replace("\n", " ")
        start_time = time.time()
        try:
            response = self.openai_client.embeddings.create(
                input=[text],
                model=self.config.embedding.openai_model
            )
            embedding = response.data[0].embedding
            elapsed_time = time.time() - start_time
            logging.info(f"Embedding generated in {elapsed_time:.3f} seconds")
            return embedding
        except Exception as e:
            logging.error(f"Error generating embedding: {str(e)}")
            raise
    
    def _get_ollama_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama's API using ollama library."""
        text = text.replace("\n", " ")
        start_time = time.time()
        try:
            response = ollama.embed(
                model=self.config.embedding.ollama_model,
                input=text
            )
            if "embeddings" not in response:
                raise ValueError(f"Unexpected response format from Ollama API: {response}")
            
            # Ensure embeddings is a 1-D array
            embedding = response["embeddings"]
            if not isinstance(embedding, list):
                raise ValueError(f"Expected list type for embedding, got {type(embedding)}")
                
            # Handle both single array and nested array formats
            if len(embedding) > 0 and isinstance(embedding[0], list):
                # If we get a 2-D array with one subarray, take the first subarray
                if len(embedding) == 1:
                    embedding = embedding[0]
                else:
                    # If we get multiple subarrays, flatten them
                    embedding = [item for sublist in embedding for item in sublist]
                    
            # Validate the flattened embedding
            if not embedding or not all(isinstance(x, (int, float)) for x in embedding):
                raise ValueError(f"Invalid embedding format: all elements must be numbers")
                
            logging.info(f"Embedding shape: {len(embedding)} dimensions")
                
            elapsed_time = time.time() - start_time
            logging.info(f"Embedding generated in {elapsed_time:.3f} seconds")
            return embedding
        except Exception as e:
            logging.error(f"Error generating Ollama embedding: {str(e)}")
            raise
        
 
    def _chunk_text(self, text: str) -> List[str]:
        """Chunk the input text into smaller pieces."""
        chunk_size = self.config.embedding.chunk_size
        overlap = self.config.embedding.chunk_overlap
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def embed_and_store(self, text: str, file_name: str, source_data: Dict[str, Any] = None):
        """Chunk the input text, generate embeddings, and store them in the database."""
        chunks = self._chunk_text(text)
        for chunk in chunks:
            try:
                chunk_id = str(uuid.uuid4())
                print(f"\nProcessing chunk: {chunk}")
                embedding = self.embedding_service(chunk)
                print(f"Generated embedding (first 5 dimensions): {embedding[:5]}...")
                self._store_in_db(
                    chunk_id=chunk_id,
                    title=file_name,
                    metadata=source_data,
                    content=chunk,
                    embedding=embedding
                )
            except Exception as e:
                print(f"Error processing chunk: {e}")

    def _store_in_db(self, chunk_id: str, title: str, metadata: Dict[str, Any], content: str, embedding: List[float]):
        """Store the chunk and its embedding in the PostgreSQL database."""
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(f"""
                INSERT INTO {self.config.table.name} (id, title, metadata, content, embedding)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                chunk_id,
                title,
                json.dumps(metadata),
                content,
                embedding
            ))
            self.db_connection.commit()
        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Failed to store embedding in database: {e}")
        finally:
            cursor.close()

    def close(self):
        """Close the database connection."""
        if self.db_connection:
            self.db_connection.close()

if __name__ == "__main__":
    # Initialize the embedding agent
    agent = EmbeddingAgent()

    try:
        # Read the content of 项链.txt
        file_path = "../data/项链.txt"
        with open(file_path, "r", encoding="utf-8") as file:
            text_content = file.read()

        # Embed and store the content
        agent.embed_and_store(
            text=text_content,
            file_name="项链.txt",
            source_data={"type": "literature", "language": "chinese"}
        )

        print("Successfully embedded and stored the content of 项链.txt")

    except Exception as e:
        print(f"Error processing file: {e}")
    finally:
        # Close the database connection
        agent.close()