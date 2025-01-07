from typing import List, Dict, Optional
from vector_store import VectorStore
import os

class RAGManager:
    def __init__(self, vector_store_name: str = "default"):
        """Initialize the RAG manager with a vector store."""
        self.vector_store = VectorStore()
        self.vector_store_name = vector_store_name
        self._load_or_create_store()
        
    def _load_or_create_store(self) -> None:
        """Load existing vector store or create a new one."""
        if not self.vector_store.load(self.vector_store_name):
            print(f"Creating new vector store: {self.vector_store_name}")
            
    def add_knowledge(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> None:
        """Add new knowledge to the vector store."""
        self.vector_store.add_documents(texts, metadata)
        self.vector_store.save(self.vector_store_name)
        
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
        
    def clear_knowledge(self) -> None:
        """Clear all knowledge from the vector store."""
        self.vector_store.clear()
        self.vector_store.save(self.vector_store_name)
