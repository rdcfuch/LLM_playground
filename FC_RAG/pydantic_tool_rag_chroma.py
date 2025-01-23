from typing import Dict, List, Optional
import nest_asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel
import os
import json

from utils.chroma_v_db import query_vector_db

# Set environment variable to ignore Logfire warnings
os.environ["LOGFIRE_IGNORE_NO_CONFIG"] = "1"
nest_asyncio.apply()

# Model configuration
DeepSeek_MODEL = "deepseek-chat"
DeepSeek_API_KEY = "sk-be34b6c3d96f416b86a097987ac9b1fe"
DeepSeek_BASE_URL = "https://api.deepseek.com"

model = OpenAIModel(
    model_name=DeepSeek_MODEL,
    api_key=DeepSeek_API_KEY,
    base_url=DeepSeek_BASE_URL,
)

class QueryInput(BaseModel):
    query: str = Field(description="The search query to look for termite-related information")

class SearchResult(BaseModel):
    results: Dict = Field(description="Search results from the vector database")
    query: str = Field(description="The query that was searched for")

# Define response model
class TermiteAnalysisResponse(BaseModel):
    has_termites: bool = Field(description="Whether termites are present")
    confidence: float = Field(description="Confidence level of the analysis (0-1)")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting the conclusion")
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions")

# First, let's directly query the vector database to see the results
print("\nQuerying vector database directly:")
query = "Are there any signs of termite infestation or damage in the property?"
results = query_vector_db(query)
print("\nRetrieval Results:")
print(json.dumps(json.loads(results), indent=2))

# Agent with structured output
agent5 = Agent(
    model=model,
    result_type=TermiteAnalysisResponse,
    deps_type=QueryInput,
    retries=3,
    system_prompt=(
        "You are an expert termite inspector analyzing documents for evidence of termite presence.\n"
        "Use the query_vector_db tool to search through inspection reports and documents.\n"
        "The tool will return a JSON string that you should parse to analyze the results.\n"
        "Analyze the search results and provide a structured response that includes:\n"
        "1. Whether termites are present (true/false)\n"
        "2. Your confidence level (0-1)\n"
        "3. Specific evidence found in the documents\n"
        "4. Practical recommendations based on the findings\n"
        "Always maintain a professional and analytical tone."
    ),
    tools=[Tool(query_vector_db, takes_ctx=True)],
)

# Run analysis
query = QueryInput(query="Are there any signs of termite infestation or damage in the property?")
response = agent5.run_sync(
    user_prompt="Please analyze the documents for any evidence of termites.",
    deps=query
)

# Print results
print("\nAnalysis Results:")
print(response.data.model_dump_json(indent=2))
