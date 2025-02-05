from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any
import logging

from pydantic_ai import RunContext
from pydantic_ai.agent import Agent
from embedAgent import EmbeddingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Deps:
    embed_agent: EmbeddingAgent

# Initialize the agent with GPT-4 and our custom dependencies
rag_agent = Agent('openai:gpt-4o-mini', deps_type=Deps)

@rag_agent.tool
async def retrieve(context: RunContext[Deps], query: str, keyword_k: int = 5, 
                semantic_k: int = 5, rerank: bool = True, top_n: int = 5) -> Dict[str, Any]:
    """Retrieve relevant documents using hybrid search.

    Args:
        context: The call context with dependencies.
        query: The search query string.
        keyword_k: Number of keyword search results.
        semantic_k: Number of semantic search results.
        rerank: Whether to apply reranking.
        top_n: Number of top results to return.

    Returns:
        Dict containing search results and metadata.
    """
    logger.info(f"LLM called retrieve tool with query: {query}")
    logger.info(f"Search parameters - keyword_k: {keyword_k}, semantic_k: {semantic_k}, rerank: {rerank}, top_n: {top_n}")

    # Use the hybrid_search method from EmbeddingAgent
    results = context.deps.embed_agent.hybrid_search(
        query=query,
        keyword_k=keyword_k,
        semantic_k=semantic_k,
        rerank=rerank,
        top_n=top_n
    )

    # Convert results to a dictionary format
    results_dict = results.to_dict(orient='records')
    logger.info(f"Retrieved {len(results_dict)} documents")
    logger.debug(f"Retrieved documents: {results_dict}")

    response = {
        "status": "success",
        "results": results_dict,
        "total_results": len(results),
        "search_types": results['search_type'].unique().tolist()
    }
    logger.info(f"Search types used: {response['search_types']}")
    return response

async def run_agent(question: str, embed_agent: EmbeddingAgent):
    """Run the RAG agent to answer questions using the document store.

    Args:
        question: The user's question.
        embed_agent: Instance of EmbeddingAgent for document retrieval.
    """
    try:
        logger.info(f"Starting RAG agent with question: {question}")
        # Create dependencies instance
        deps = Deps(embed_agent=embed_agent)
        
        # Run the agent with the question
        logger.info("Running LLM agent...")
        answer = await rag_agent.run(question, deps=deps)
        logger.info("LLM agent completed successfully")
        return answer.data
        
    except Exception as e:
        logger.error(f"Error running RAG agent: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import asyncio
    from config import Config
    
    async def main():
        # Initialize embedding agent
        config = Config().load_config()
        embed_agent = EmbeddingAgent(config)
        
        try:
            # Test the RAG agent
            question = "谁的项链?项链是多少钱？"
            logger.info("=== Starting RAG Agent Test ===")
            answer = await run_agent(question, embed_agent)
            logger.info(f"Question: {question}")
            logger.info(f"Answer: {answer}")
            logger.info("=== RAG Agent Test Completed ===")
            
        finally:
            embed_agent.close()
    
    asyncio.run(main())