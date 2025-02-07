from typing import Optional, Dict, Any, List
from duckduckgo_search import DDGS
import asyncio
from fc_pydantic_agent.agent import DynamicAgent

class SearchAgent(DynamicAgent):
    """An agent with built-in web search capabilities using DuckDuckGo."""

    def duckduckgo_search(self, query: str, max_results: int = 3) -> List[str]:
        """Perform a web search using DuckDuckGo.

        Args:
            query (str): The search query
            max_results (int, optional): Maximum number of results to return. Defaults to 3.

        Returns:
            List[str]: List of search results
        """
        ddgs = DDGS()
        results = [result for result in ddgs.text(query, max_results=max_results)]
        return results

    def __init__(self, model_type: str, system_prompt: str, result_type: Any = None, deps_type: Any = Dict[str, Any]):
        super().__init__(model_type, system_prompt, result_type, deps_type)
        
        # Register the search tool
        self.tool = self.duckduckgo_search

def main():
    # Create a search agent instance
    agent = SearchAgent(
        model_type="kimi",
        system_prompt="You are a helpful assistant that can search the web for information."
    )
    
    # Test the search functionality
    query = "What is the latest news about artificial intelligence?"
    print(f"Searching for: {query}")
    
    # Get the search tool from the agent
    search_tool = agent.tool
    
    # Execute the search
    results = search_tool(query)
    
    # Print results
    print("\nSearch Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result}")

if __name__ == '__main__':
    main()