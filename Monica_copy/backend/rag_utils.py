from typing import List, Dict, Optional
from vector_store import VectorStore
import os
import uuid
import datetime
import logging

logger = logging.getLogger(__name__)

class RAGManager:
    def __init__(self, vector_store_name: str = "default"):
        """Initialize the RAG manager with a vector store."""
        self.vector_store = VectorStore()
        self.vector_store_name = vector_store_name
        self.files = {}  # Store file metadata: {file_id: {name, size, chunks}}
        self._load_or_create_store()
        
    def _load_or_create_store(self) -> None:
        """Load existing vector store or create a new one."""
        if not self.vector_store.load(self.vector_store_name):
            print(f"Creating new vector store: {self.vector_store_name}")
            
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
        self.vector_store.save(self.vector_store_name)
        return file_id
        
    def query_knowledge(self, query: str, k: int = 5) -> List[Dict]:
        """Query the knowledge base."""
        return self.vector_store.search(query, k)
        
    def format_for_context(self, results: List[Dict]) -> str:
        """Format search results for adding to prompt context."""
        context = "Relevant information from the knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['text']}\n"
            if result['metadata'].get('source'):
                context += f"   Source: {result['metadata']['source']}\n"
            context += "\n"
        return context
        
    def generate_rag_prompt(self, query: str, k: int = 5) -> str:
        """Generate a prompt with relevant context for the query."""
        results = self.query_knowledge(query, k)
        context = self.format_for_context(results)
        
        prompt = f"""Based on the following context and the user's question, provide a comprehensive and accurate answer.
If the context doesn't contain relevant information, acknowledge that and provide a general response.

{context}

User's question: {query}

Answer:"""
        
        return prompt
        
    def delete_file(self, file_id: str) -> bool:
        """Delete a file and its chunks from the vector store."""
        try:
            if file_id not in self.files:
                return False
                
            # Remove documents with matching file_id
            self.vector_store.delete_by_metadata({'file_id': file_id})
            del self.files[file_id]
            
            # Save changes to disk
            self.vector_store.save(self.vector_store_name)
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
        self.vector_store.save(self.vector_store_name)
        self.files = {}
