import os
import faiss
import numpy as np
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
import pickle
import json
from datetime import datetime

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the vector store with a sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.texts: List[str] = []
        self.metadata: List[Dict] = []
        self.store_path = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.store_path, exist_ok=True)
        
    def add_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> None:
        """Add documents to the vector store with optional metadata."""
        if not texts:
            return
            
        # Create embeddings for the texts
        embeddings = self.model.encode(texts)
        
        # Add embeddings to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Store documents with metadata
        if metadata is None:
            metadata = [{"timestamp": datetime.now().isoformat()} for _ in texts]
        
        self.texts.extend(texts)
        self.metadata.extend(metadata)
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents using the query."""
        # Create query embedding
        query_embedding = self.model.encode([query])
        
        # Search in FAISS index
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        
        # Get the matching documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.texts):  # Ensure the index is valid
                results.append({
                    "text": self.texts[idx],
                    "metadata": self.metadata[idx],
                    "score": float(distances[0][i]),  # Convert numpy float to Python float
                })
        
        return results
    
    def save(self, name: str = "default") -> None:
        """Save the vector store to disk."""
        # Save FAISS index
        index_path = os.path.join(self.store_path, f"{name}.faiss")
        faiss.write_index(self.index, index_path)
        
        # Save documents and metadata
        docs_path = os.path.join(self.store_path, f"{name}.json")
        with open(docs_path, 'w', encoding='utf-8') as f:
            json.dump({
                'texts': self.texts,
                'metadata': self.metadata
            }, f, ensure_ascii=False, indent=2)
            
    def load(self, name: str = "default") -> bool:
        """Load the vector store from disk."""
        index_path = os.path.join(self.store_path, f"{name}.faiss")
        metadata_path = os.path.join(self.store_path, f"{name}.json")
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            # Initialize a new index if it doesn't exist
            dimension = 384  # dimension for all-MiniLM-L6-v2
            self.index = faiss.IndexFlatL2(dimension)
            self.texts = []
            self.metadata = []
            return False
            
        try:
            self.index = faiss.read_index(index_path)
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                self.texts = data['texts']
                self.metadata = data['metadata']
            return True
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return False
            
    def clear(self) -> None:
        """Clear the vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.texts = []
        self.metadata = []
        
    def get_document_by_id(self, doc_id: int) -> Optional[Dict]:
        """Retrieve a document by its ID."""
        for i, text in enumerate(self.texts):
            if i == doc_id:
                return {
                    "text": text,
                    "metadata": self.metadata[i],
                }
        return None
