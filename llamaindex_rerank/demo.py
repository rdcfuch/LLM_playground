import os
from document_processor import IntelligentDocumentProcessor

def main():
    # Initialize the processor with Ollama embeddings
    processor = IntelligentDocumentProcessor(
        embedding_model="ollama",
        chunk_size=800,
        chunk_overlap=100,
        use_semantic_splitter=True
    )

    # Load documents
    documents = processor.load_documents("/Users/fcfu/PycharmProjects/LLM_playground/llamaindex_rerank/项链.txt")

    # Process documents and create index
    index = processor.process_documents(documents)

    # Perform search with re-ranking
    query = "这是谁的项链?"
    results = processor.search(index, query, top_k=3)

    # Print results
    print("\nInitial Search Results:")
    for i, result in enumerate(results['initial_results'], 1):
        print(f"\nResult {i}:")
        print(f"Score: {result['score']:.4f}")
        print(f"Text: {result['text'][:200]}...")
        if result['metadata']:
            print(f"Metadata: {result['metadata']}")

    print("\nRe-ranked Results:")
    for i, result in enumerate(results['reranked_results'], 1):
        print(f"\nResult {i}:")
        print(f"Score: {result['score']:.4f}")
        print(f"Text: {result['text'][:200]}...")
        if result['metadata']:
            print(f"Metadata: {result['metadata']}")

if __name__ == "__main__":
    main()