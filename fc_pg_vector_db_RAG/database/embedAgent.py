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
import pandas as pd

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
        self.cohere_client = cohere.Client(api_key=self.config.cohere.api_key) if hasattr(self.config, 'cohere') else None

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

    def semantic_search(self, query: str, limit: int = 5, metadata_filter: Dict[str, Any] = None) -> pd.DataFrame:
        """Perform semantic search using vector similarity.

        Args:
            query: The search query string
            limit: Maximum number of results to return
            metadata_filter: Optional metadata filter criteria

        Returns:
            DataFrame containing the search results with columns: id, title, content, metadata, and similarity_score
        """
        # Generate embedding for the query
        query_embedding = self.embedding_service(query)

        # Construct the search query
        search_sql = f"""
            SELECT id, title, content, metadata::text,
                   1 - (embedding <=> %s::vector) as similarity_score
            FROM {self.config.table.name}
            WHERE TRUE
        """
        params = [query_embedding]

        # Add metadata filter if provided
        if metadata_filter:
            conditions = []
            for key, value in metadata_filter.items():
                conditions.append(f"metadata->>'%s' = %s")
                params.extend([key, str(value)])
            search_sql += " AND " + " AND ".join(conditions)

        # Add ordering and limit
        search_sql += """
            ORDER BY similarity_score DESC
            LIMIT %s
        """
        params.append(limit)

        # Execute search
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(search_sql, params)
            results = cursor.fetchall()
            
            # Convert to DataFrame
            df = pd.DataFrame(results, columns=['id', 'title', 'content', 'metadata', 'similarity_score'])
            df['metadata'] = df['metadata'].apply(json.loads)  # Parse JSON metadata
            df['search_type'] = 'semantic'  # Add search type for consistency with hybrid search
            return df
        finally:
            cursor.close()

    def keyword_search(self, query: str, limit: int = 5) -> pd.DataFrame:
        """Perform keyword-based full-text search.

        Args:
            query: The search query string
            limit: Maximum number of results to return

        Returns:
            DataFrame containing the search results with columns: id, title, content, metadata, and similarity_score
        """
        search_sql = f"""
            WITH search_query AS (
                SELECT plainto_tsquery('english', %s) AS query
            )
            SELECT id, title, content, metadata::text,
                   (ts_rank_cd(to_tsvector('english', title), query) +
                    ts_rank_cd(to_tsvector('english', content), query) +
                    ts_rank_cd(to_tsvector('english', metadata::text), query))::float as similarity_score
            FROM {self.config.table.name}, search_query
            WHERE to_tsvector('english', title) @@ query OR
                  to_tsvector('english', content) @@ query OR
                  to_tsvector('english', metadata::text) @@ query
            ORDER BY similarity_score DESC
            LIMIT %s
        """

        cursor = self.db_connection.cursor()
        try:
            cursor.execute(search_sql, (query, limit))
            results = cursor.fetchall()
            
            # Convert to DataFrame
            df = pd.DataFrame(results, columns=['id', 'title', 'content', 'metadata', 'similarity_score'])
            if not df.empty:
                df['metadata'] = df['metadata'].apply(json.loads)  # Parse JSON metadata
                df['search_type'] = 'keyword'  # Add search type for consistency with hybrid search
            return df
        finally:
            cursor.close()

    def hybrid_search(self, query: str, keyword_k: int = 5, semantic_k: int = 5, rerank: bool = False, top_n: int = 5) -> pd.DataFrame:
        """Perform hybrid search combining both keyword and semantic search results.

        Args:
            query: The search query string
            keyword_k: Number of results to return from keyword search
            semantic_k: Number of results to return from semantic search
            rerank: Whether to apply Cohere reranking
            top_n: Number of top results to return after reranking

        Returns:
            DataFrame containing the combined search results with search_type and similarity_score columns
        """
        # Get keyword search results
        keyword_results = self.keyword_search(query, limit=keyword_k)

        # Get semantic search results
        semantic_results = self.semantic_search(query, limit=semantic_k)

        # Combine results
        combined_results = pd.concat([keyword_results, semantic_results], ignore_index=True)

        # Remove duplicates based on id, keeping the first occurrence
        combined_results = combined_results.drop_duplicates(subset=['id'], keep='first')

        if rerank and self.cohere_client:
            return self._rerank_results(query, combined_results, top_n)

        # Ensure all required columns are present
        if 'relevance_score' not in combined_results.columns:
            combined_results['relevance_score'] = combined_results['similarity_score']

        return combined_results

    def _rerank_results(self, query: str, combined_results: pd.DataFrame, top_n: int) -> pd.DataFrame:
        """
        Rerank the combined search results using Cohere.

        Args:
            query: The original search query.
            combined_results: DataFrame containing the combined keyword and semantic search results.
            top_n: The number of top results to return after reranking.

        Returns:
            A pandas DataFrame containing the reranked results.
        """
        rerank_results = self.cohere_client.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=combined_results["content"].tolist(),
            top_n=top_n,
            return_documents=True
        )

        reranked_df = pd.DataFrame(
            [
                {
                    "id": combined_results.iloc[result.index]["id"],
                    "content": result.document,
                    "search_type": combined_results.iloc[result.index]["search_type"],
                    "relevance_score": result.relevance_score,
                }
                for result in rerank_results.results
            ]
        )

        return reranked_df.sort_values("relevance_score", ascending=False)

if __name__ == "__main__":
    # Initialize the embedding agent
    agent = EmbeddingAgent()

    try:
        # Test hybrid search with different reranking configurations
        print("\nTesting hybrid search with different reranking configurations...")
        query = "谁的项链"

        # Test case 1: Basic hybrid search without reranking
        print("\n1. Without reranking (baseline):")
        baseline_results = agent.hybrid_search(
            query=query,
            keyword_k=3,
            semantic_k=3,
            rerank=False
        )
        print(f"Baseline search found {len(baseline_results)} results")
        for idx, row in baseline_results.iterrows():
            print(f"Result {idx + 1}:")
            print(f"Title: {row['title']}")
            print(f"Content: {row['content'][:100]}...")
            print(f"Search Type: {row['search_type']}")
            print(f"Score: {row['relevance_score']:.4f}\n")

        # Test case 2: Hybrid search with reranking and different top_n values
        print("\n2. With Cohere reranking (top_n=3):")
        reranked_results_3 = agent.hybrid_search(
            query=query,
            keyword_k=5,
            semantic_k=5,
            rerank=True,
            top_n=3
        )
        print(f"Reranked results (top_n=3) found {len(reranked_results_3)} results")
        for idx, row in reranked_results_3.iterrows():
            print(f"Result {idx + 1}:")
            print(f"Title: {row['title']}")
            print(f"Content: {row['content'][:100]}...")
            print(f"Search Type: {row['search_type']}")
            print(f"Relevance Score: {row['relevance_score']:.4f}\n")

        # Test case 3: Hybrid search with reranking and larger result set
        print("\n3. With Cohere reranking (top_n=5):")
        reranked_results_5 = agent.hybrid_search(
            query=query,
            keyword_k=8,
            semantic_k=8,
            rerank=True,
            top_n=5
        )
        print(f"Reranked results (top_n=5) found {len(reranked_results_5)} results")
        for idx, row in reranked_results_5.iterrows():
            print(f"Result {idx + 1}:")
            print(f"Title: {row['title']}")
            print(f"Content: {row['content'][:100]}...")
            print(f"Search Type: {row['search_type']}")
            print(f"Relevance Score: {row['relevance_score']:.4f}\n")

    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        # Close the database connection
        agent.close()