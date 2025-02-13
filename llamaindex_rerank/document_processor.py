from typing import List, Union, Optional
from pathlib import Path
import logging
from llama_index.core import (
    Document,
    VectorStoreIndex,
    ServiceContext,
    download_loader,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

class IntelligentDocumentProcessor:
    def __init__(
        self,
        embedding_model: str = "openai",  # "openai" or "ollama"
        openai_api_key: Optional[str] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        use_semantic_splitter: bool = False,
        reranker_model: str = "BAAI/bge-reranker-base",
    ):
        self.logger = logging.getLogger(__name__)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_semantic_splitter = use_semantic_splitter
        
        # Initialize embedding model
        if embedding_model == "openai":
            if not openai_api_key:
                raise ValueError("OpenAI API key is required for OpenAI embeddings")
            self.embed_model = OpenAIEmbedding(model_name="text-embedding-ada-002", api_key=openai_api_key)
        elif embedding_model == "ollama":
            # Use Ollama's OpenAI-compatible API endpoint
            self.embed_model = OpenAIEmbedding(
                model_name="nomic-embed-text:latest",
                api_base="http://localhost:11434/v1",
                api_key="ollama"
            )
        else:
            raise ValueError(f"Unsupported embedding model: {embedding_model}")
            
        # Initialize node parser
        if use_semantic_splitter:
            self.node_parser = SentenceSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        else:
            self.node_parser = SentenceSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
        # Initialize reranker
        self.reranker_model = AutoModelForSequenceClassification.from_pretrained(reranker_model)
        self.reranker_tokenizer = AutoTokenizer.from_pretrained(reranker_model)
        
        # Initialize settings
        from llama_index.core.settings import Settings
        Settings.embed_model = self.embed_model
        Settings.node_parser = self.node_parser
        
    def load_documents(self, file_paths: Union[str, List[str], Path, List[Path]]) -> List[Document]:
        """Load documents from various file formats (PDF, TXT, CSV)"""
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]
            
        documents = []
        for file_path in file_paths:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            if file_path.suffix.lower() == ".pdf":
                PDFReader = download_loader("PDFReader")
                loader = PDFReader()
                docs = loader.load_data(file=file_path)
            elif file_path.suffix.lower() in [".txt", ".csv"]:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                docs = [Document(text=content)]
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
                
            documents.extend(docs)
            
        return documents
    
    def process_documents(self, documents: List[Document]) -> VectorStoreIndex:
        """Process documents and create a searchable index"""
        return VectorStoreIndex.from_documents(
            documents,
            node_parser=self.node_parser
        )
    
    def rerank(self, query: str, nodes: List[dict], top_k: int = 5) -> List[dict]:
        """Re-rank the retrieved nodes using the reranker model"""
        # Prepare pairs for reranking
        pairs = [(query, node.node.text) for node in nodes]
        features = self.reranker_tokenizer(
            pairs,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=512
        )
        
        # Get scores from reranker model
        with torch.no_grad():
            scores = self.reranker_model(**features).logits
            
        # Combine results
        results = []
        for i, (node, score) in enumerate(zip(nodes, scores)):
            results.append({
                "text": node.node.text,
                "score": float(score),
                "metadata": node.node.metadata
            })
            
        # Sort by re-ranker score and take top k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def search(self, index: VectorStoreIndex, query: str, top_k: int = 5) -> dict:
        """Perform semantic search and re-ranking"""
        # Initial retrieval
        retriever = index.as_retriever(similarity_top_k=top_k * 2)
        initial_nodes = retriever.retrieve(query)
        
        # Format initial results
        initial_results = [{
            "text": node.node.text,
            "score": float(node.score),
            "metadata": node.node.metadata
        } for node in initial_nodes]
        
        # Re-rank the results
        reranked_results = self.rerank(query, initial_nodes, top_k)
        
        return {
            "initial_results": initial_results[:top_k],
            "reranked_results": reranked_results
        }

# Example usage
if __name__ == "__main__":
    processor = IntelligentDocumentProcessor(
        embedding_model="ollama",  # or "openai"
        openai_api_key="",  # Required if using OpenAI
        chunk_size=512,
        chunk_overlap=50,
        use_semantic_splitter=False,
        reranker_model="BAAI/bge-reranker-base"
    )
    file_paths = ["path/to/your/document1.pdf", "path/to/your/document2.txt"]
    documents = processor.load_documents(file_paths)
    index = processor.process_documents(documents)
    query = "What is the main topic of the document?"
    results = processor.search(index, query, top_k=5)
    for result in results:
        print(result["text"], result["score"])
