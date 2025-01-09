from typing import List, Dict, Optional
from vector_store import VectorStore
import os
import logging
import datetime
from dotenv import load_dotenv
import httpx
from openai import OpenAI

load_dotenv()
logger = logging.getLogger(__name__)

class RAGManager:
    def __init__(self, collection_name: str = "document_store"):
        """Initialize RAG manager with vector store."""
        self.vector_store = VectorStore(collection_name=collection_name)
        self.collection_name = collection_name
        self.files = {}  # Store file metadata: {file_id: {name, size, chunks}}
        
        # Initialize OpenAI client
        self.openai_client = OpenAI()
        
        # Initialize DeepSeek client for backup
        deepseek_api_key = os.getenv("DeepSeek_API_KEY")
        deepseek_base_url = os.getenv("DeepSeek_BASE_URL")
        
        if deepseek_api_key and deepseek_base_url:
            self.deepseek_client = httpx.Client(
                base_url=deepseek_base_url,
                headers={"Authorization": f"Bearer {deepseek_api_key}"},
                timeout=30.0
            )
        else:
            self.deepseek_client = None
            
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
        
    def query_knowledge(self, query: str, k: int = 5) -> List[Dict]:
        """Query the knowledge base."""
        if not self.has_knowledge():
            raise ValueError("Knowledge base is empty. Please add documents first.")
            
        return self.vector_store.search(query, k)
        
    def _format_context(self, results: List[Dict]) -> str:
        """Format search results for adding to prompt context."""
        context = "Here is the relevant information from the knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['text']}\n"
            if result['metadata'].get('source'):
                context += f"   Source: {result['metadata']['source']}\n"
            context += "\n"
        return context
        
    def generate_response(self, query: str, k: int = 5) -> str:
        """Generate a response using OpenAI or DeepSeek."""
        if not self.has_knowledge():
            raise ValueError("Cannot enable knowledge base: No files available. Please upload files first.")
            
        results = self.query_knowledge(query, k)
        context = self._format_context(results)
        
        system_prompt = """You are a helpful AI assistant. Answer questions based ONLY on the provided knowledge. 
If you cannot find the answer in the provided information, say "I don't have enough information to answer that question."
DO NOT make up or infer information that is not explicitly stated in the context.

Here is the relevant information:
""" + context

        try:
            # Try OpenAI first
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            
            # Fall back to DeepSeek if available
            if self.deepseek_client:
                try:
                    response = self.deepseek_client.post("/v1/chat/completions", json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": query}
                        ]
                    })
                    response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    logger.error(f"DeepSeek API error: {e}")
                    raise
            else:
                raise
                
    def delete_file(self, file_id: str) -> bool:
        """Delete a file and its chunks from the vector store."""
        try:
            if file_id not in self.files:
                return False
                
            # Remove documents with matching file_id
            self.vector_store.delete_by_metadata({'file_id': file_id})
            del self.files[file_id]
            return True
            
        except Exception as e:
            logger.error(f"Error in delete_file: {str(e)}", exc_info=True)
            raise
            
    def list_files(self) -> List[Dict]:
        """List all files in the knowledge base."""
        return [
            {'id': file_id, **file_info}
            for file_id, file_info in self.files.items()
        ]
        
    def clear_knowledge(self) -> None:
        """Clear all knowledge from the vector store."""
        self.vector_store.clear()
        self.files = {}
