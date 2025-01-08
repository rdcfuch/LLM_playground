import os
import faiss
import numpy as np
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ollama_embeddings import OllamaEmbeddings

class VectorStore:
    def __init__(self, model_name: str = "nomic-embed-text"):
        """Initialize the vector store with Ollama embeddings model."""
        try:
            self.model = OllamaEmbeddings(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(self.dimension)
            self.texts: List[str] = []
            self.metadata: List[Dict] = []
            self.store_path = os.path.join(os.path.dirname(__file__), "data")
            os.makedirs(self.store_path, exist_ok=True)
        except Exception as e:
            print(f"Error initializing VectorStore: {str(e)}")
            raise
            
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
    
    def save(self, name: str = "default") -> bool:
        """Save the vector store to disk."""
        try:
            # Save FAISS index
            index_path = os.path.join(self.store_path, f"{name}.faiss")
            faiss.write_index(self.index, index_path)
            
            # Save documents and metadata
            docs_path = os.path.join(self.store_path, f"{name}.json")
            with open(docs_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'texts': self.texts,
                    'metadata': self.metadata,
                    'dimension': self.dimension
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving vector store: {str(e)}")
            return False
            
    def load(self, name: str = "default") -> bool:
        """Load the vector store from disk."""
        index_path = os.path.join(self.store_path, f"{name}.faiss")
        metadata_path = os.path.join(self.store_path, f"{name}.json")
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            print(f"No existing vector store found at {index_path}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.texts = []
            self.metadata = []
            return False
            
        try:
            self.index = faiss.read_index(index_path)
            if self.index.d != self.dimension:
                print(f"Index dimension mismatch: stored={self.index.d}, current={self.dimension}")
                self.index = faiss.IndexFlatL2(self.dimension)
                self.texts = []
                self.metadata = []
                return False
                
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.texts = data['texts']
                self.metadata = data['metadata']
            return True
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.texts = []
            self.metadata = []
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

    def delete_by_metadata(self, filter_dict: Dict) -> None:
        """Delete documents that match the metadata filter."""
        if not self.texts:
            return
            
        # Find indices to keep
        indices_to_keep = []
        new_texts = []
        new_metadata = []
        
        for i, meta in enumerate(self.metadata):
            keep = True  # Default to keeping the document
            for key, value in filter_dict.items():
                if key in meta and meta[key] == value:
                    keep = False  # Don't keep if it matches the filter
                    break
            
            if keep:
                indices_to_keep.append(i)
                new_texts.append(self.texts[i])
                new_metadata.append(self.metadata[i])
        
        if not indices_to_keep:
            # If no documents remain, clear everything
            self.clear()
            return
            
        # Create new index with kept documents
        new_index = faiss.IndexFlatL2(self.dimension)
        if indices_to_keep:
            # Get embeddings for kept documents
            embeddings = self.model.encode(new_texts)
            new_index.add(np.array(embeddings).astype('float32'))
        
        # Update instance variables
        self.index = new_index
        self.texts = new_texts
        self.metadata = new_metadata
