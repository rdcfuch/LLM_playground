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
        
    def generate_response(self, query: str, k: int = 8) -> str:
        """Generate a response using OpenAI or DeepSeek."""
        if not self.has_knowledge():
            raise ValueError("Cannot enable knowledge base: No files available. Please upload files first.")
            
        try:
            # Get relevant documents
            results = self.query_knowledge(query, k)
            if not results:
                return "I don't have any relevant information to answer that question."
                
            context = self._format_context(results)
            
            system_prompt = """You are a helpful AI assistant. Answer questions based ONLY on the provided knowledge. 
If you cannot find the answer in the provided information, say "I don't have enough information to answer that question."
DO NOT make up or infer information that is not explicitly stated in the context.

Here is the relevant information:
""" + context

            try:
                # Try OpenAI first
                logger.info("Attempting to generate response with OpenAI")
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                return response.choices[0].message.content
                
            except Exception as openai_error:
                logger.error(f"OpenAI error: {openai_error}")
                
                # Fallback to DeepSeek if available
                if self.deepseek_client:
                    try:
                        logger.info("Falling back to DeepSeek")
                        response = self.deepseek_client.post(
                            "/v1/chat/completions",
                            json={
                                "model": "deepseek-chat",
                                "messages": [
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": query}
                                ],
                                "temperature": 0.7,
                                "max_tokens": 500
                            }
                        )
                        response.raise_for_status()
                        return response.json()["choices"][0]["message"]["content"]
                        
                    except Exception as deepseek_error:
                        logger.error(f"DeepSeek error: {deepseek_error}")
                        raise Exception("Both OpenAI and DeepSeek failed to generate a response")
                else:
                    raise openai_error
                    
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
