from typing import List, Dict, Optional
from vector_store import VectorStore
import os
import logging
import datetime
from dotenv import load_dotenv
import httpx

load_dotenv()
logger = logging.getLogger(__name__)

class RAGManager:
    def __init__(self, collection_name: str = "document_store"):
        """Initialize RAG manager with vector store."""
        self.vector_store = VectorStore(collection_name=collection_name)
        self.collection_name = collection_name
        self.files = {}  # Store file metadata: {file_id: {name, size, chunks}}
        self.chat_history = []  # Store chat history as list of (query, response) tuples
        
        # Initialize DeepSeek client
        deepseek_api_key = os.getenv("DeepSeek_API_KEY")
        deepseek_base_url = os.getenv("DeepSeek_BASE_URL")
        
        if not deepseek_api_key or not deepseek_base_url:
            raise ValueError("DeepSeek API key and base URL are required")
            
        self.deepseek_client = httpx.Client(
            base_url=deepseek_base_url,
            headers={"Authorization": f"Bearer {deepseek_api_key}"},
            timeout=30.0
        )
        
    def add_knowledge(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> str:
        """Add new knowledge to the vector store and return the file ID."""
        import uuid
        file_id = str(uuid.uuid4())
        
        if metadata and len(metadata) > 0:
            file_name = metadata[0].get('source', 'unknown')
            self.files[file_id] = {
                'name': file_name,
                'size': sum(len(text.encode('utf-8')) for text in texts),
                'chunks': len(texts),
                'added': str(datetime.datetime.now())
            }
        
        self.vector_store.add_documents(texts, [
            {**meta, 'file_id': file_id} for meta in (metadata or [{}] * len(texts))
        ])
        return file_id
        
    def has_knowledge(self) -> bool:
        """Check if there is any knowledge in the vector store."""
        return self.vector_store.has_documents()
        
    def query_knowledge(self, query: str, k: int = 8) -> List[Dict]:
        """Query the knowledge base."""
        if not self.has_knowledge():
            raise ValueError("Knowledge base is empty. Please add documents first.")
            
        return self.vector_store.search(query, k)
        
    def _format_context(self, results: List[Dict]) -> str:
        """Format search results for adding to prompt context."""
        context = "Here are the relevant passages from the knowledge base:\n\n"
        
        # Sort results by score in descending order
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        for i, result in enumerate(sorted_results, 1):
            # Add score and source information as a header
            context += f"[Passage {i} (Relevance: {result['score']:.2f})"
            if result['metadata'].get('source'):
                context += f", Source: {result['metadata']['source']}"
            context += "]\n"
            
            # Add the text content
            context += f"{result['text'].strip()}\n\n"
            
        return context
        
    def _format_chat_history(self) -> str:
        """Format chat history into a string for context."""
        if not self.chat_history:
            return ""
            
        history = []
        for query, response in self.chat_history[-3:]:  # Only use last 3 exchanges
            history.extend([
                f"User: {query}",
                f"Assistant: {response}"
            ])
        return "\n".join(history)
        
    def _refine_query(self, query: str) -> str:
        """Use DeepSeek to transform the user's query into a more logical search query."""
        try:
            logger.info("Refining search query with DeepSeek")
            chat_history = self._format_chat_history()
            system_prompt = """You are a search query optimization assistant. Your task is to transform user queries into more effective search queries.
Transform the user's question into a clear, concise search query that will help find relevant information.
Focus on key elements, context, time, person, place and background. Remove conversational elements.
Return ONLY the transformed query, nothing else.

Example:
User: "项链值多少钱?"
Output: "项链的价值, 项链的价格，购买项链"
"""

            messages = [{"role": "system", "content": system_prompt}]
            
            if chat_history:
                messages.append({
                    "role": "user", 
                    "content": f"Chat History:\n{chat_history}\n\nCurrent Question: {query}"
                })
            else:
                messages.append({"role": "user", "content": query})
            
            response = self.deepseek_client.post(
                "/v1/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 100
                }
            )
            response.raise_for_status()
            refined_query = response.json()["choices"][0]["message"]["content"].strip()
            logger.info(f"Original query: '{query}' refined to: '{refined_query}'")
            return refined_query
            
        except Exception as e:
            logger.warning(f"Query refinement failed: {e}. Using original query.")
            return query
            
    def generate_response(self, query: str, k: int = 8) -> str:
        """Generate a response using DeepSeek."""
        try:
            # Refine the query first
            refined_query = self._refine_query(query)
            
            # Get relevant documents using refined query
            results = self.query_knowledge(refined_query, k)
            if not results:
                return "I don't have any relevant information to answer that question."
                
            context = self._format_context(results)
            chat_history = self._format_chat_history()
            
            system_prompt = """You are a helpful AI assistant. Answer questions based ONLY on the provided knowledge. 
If you cannot find the answer in the provided information, say "I don't have enough information to answer that question."
DO NOT make up or infer information that is not explicitly stated in the context.

Here is the relevant information:
""" + context

            messages = [{"role": "system", "content": system_prompt}]
            
            if chat_history:
                messages.append({
                    "role": "user",
                    "content": f"Chat History:\n{chat_history}\n\nCurrent Question: {query}"
                })
            else:
                messages.append({"role": "user", "content": query})

            try:
                logger.info("Generating response with DeepSeek")
                response = self.deepseek_client.post(
                    "/v1/chat/completions",
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                response.raise_for_status()
                response_text = response.json()["choices"][0]["message"]["content"]
                
                # Store the exchange in chat history
                self.chat_history.append((query, response_text))
                # Keep only last 10 exchanges
                self.chat_history = self.chat_history[-10:]
                
                return response_text
                    
            except Exception as e:
                logger.error(f"DeepSeek error: {e}")
                raise Exception("Failed to generate a response")
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
            
    def delete_file(self, file_id: str) -> bool:
        """Delete a file and its associated documents from the knowledge base."""
        try:
            if file_id not in self.files:
                logger.warning(f"File {file_id} not found in metadata")
                return False
                
            # Delete documents from vector store
            self.vector_store.delete_by_metadata({'file_id': file_id})
            
            # Remove file metadata
            del self.files[file_id]
            logger.info(f"Successfully deleted file {file_id} and its metadata")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            raise
            
    def list_files(self) -> List[Dict]:
        """List all files in the knowledge base with their metadata."""
        files_list = []
        for file_id, metadata in self.files.items():
            files_list.append({
                'id': file_id,
                'name': metadata['name'],
                'size': metadata['size'],
                'added': metadata['added'],
                'type': 'txt',  # Since we only support text files for now
                'chunks': metadata['chunks']
            })
        return sorted(files_list, key=lambda x: x['added'], reverse=True)  # Most recent first
        
    def clear_knowledge(self) -> None:
        """Clear all knowledge from the vector store."""
        self.vector_store.clear()
        self.files = {}
