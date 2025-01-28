from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel
import os
import json
import asyncio
from utils.chroma_v_db import (
    query_vector_db as chroma_query_db,
    process_file,
    remove_file_from_db,
    list_files_in_db,
    get_db_contents,
    ChromaVectorStore,
    client as openai_client,
    EMBEDDING_MODEL,
    display_results,
    display_chunks,
    validate_file
)

# Set environment variable to ignore Logfire warnings
os.environ["LOGFIRE_IGNORE_NO_CONFIG"] = "1"

# Load environment variables
from dotenv import load_dotenv
import os

# Get the project root directory (two levels up from this script)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Load .env from the project root directory
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Model configuration
DeepSeek_MODEL = os.getenv("DeepSeek_MODEL")
DeepSeek_API_KEY = os.getenv("DeepSeek_API_KEY")
DeepSeek_BASE_URL = os.getenv("DeepSeek_BASE_URL")

model = OpenAIModel(
    model_name=DeepSeek_MODEL,
    api_key=DeepSeek_API_KEY,
    base_url=DeepSeek_BASE_URL,
)

class QueryInput(BaseModel):
    query: str = Field(description="The search query to look for information in documents")
    context: Optional[str] = Field(default="", description="Additional context for the query")

class SearchResult(BaseModel):
    results: Dict = Field(description="Search results from the vector database")
    query: str = Field(description="The query that was searched for")

class ReflectionThoughts(BaseModel):
    """Model for agent's self-reflection thoughts"""
    understanding: str = Field(description="Agent's understanding of the query")
    search_strategy: str = Field(description="Strategy for searching the documents")
    confidence: float = Field(description="Confidence in understanding (0-1)")
    needs_clarification: bool = Field(description="Whether clarification is needed")
    follow_up_questions: List[str] = Field(default_factory=list, description="Potential follow-up questions")

class AnalysisResponse(BaseModel):
    """Enhanced response model with self-reflection"""
    reflection: ReflectionThoughts = Field(description="Agent's self-reflection on the analysis")
    findings: Dict[str, List[str]] = Field(description="Key findings from the documents")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting the findings")
    confidence: float = Field(description="Confidence level of the analysis (0-1)")
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions")
    limitations: List[str] = Field(default_factory=list, description="Limitations of the analysis")

# Initialize the agent at the module level
agent = Agent(
    model=model,
    result_type=AnalysisResponse,
    deps_type=QueryInput,
    retries=3,
    system_prompt=(
        "You are an expert document analyzer with advanced self-reflection capabilities.\n"
        "Follow these steps for each analysis:\n\n"
        "1. REFLECT - Before searching:\n"
        "   - Understand the query deeply\n"
        "   - Consider what information you need\n"
        "   - Plan your search strategy\n\n"
        "2. SEARCH - Use the query_vector_db tool to find relevant information\n\n"
        "3. ANALYZE - Process the search results:\n"
        "   - Look for direct evidence\n"
        "   - Consider context and implications\n"
        "   - Note any limitations or gaps\n\n"
        "4. REFLECT AGAIN - After analysis:\n"
        "   - Assess confidence in findings\n"
        "   - Consider alternative interpretations\n"
        "   - Identify follow-up questions\n\n"
        "5. RESPOND - Provide structured output:\n"
        "   - Include your reflection process\n"
        "   - Support findings with evidence\n"
        "   - Note confidence levels and limitations\n"
        "   - Suggest next steps or recommendations\n\n"
        "If you encounter unclear or ambiguous queries, raise a ModelRetry with specific clarification needs."
    )
)

@agent.tool()
async def query_vector_db(ctx: RunContext, query_text: str, n_results: int = 5) -> Dict:
    """When you think the user's question is related to a specific knowledge, you will use this tool to Query the vector database with the given text query"""
    try:
        print(f"\nDebug - Query text: {query_text}")

        # Generate embedding for the query
        query_response = openai_client.embeddings.create(
            input=query_text,
            model=EMBEDDING_MODEL,
        )
        query_embedding = query_response.data[0].embedding
        print(f"Debug - Generated query embedding of size: {len(query_embedding)}")

        # Get collection info
        print("\nDebug - Collection info:")
        vector_store = ChromaVectorStore()
        collection = vector_store.get_collection()
        print(f"Number of items: {collection.count()}")
        print(f"Available metadata: {[m for m in collection.get()['metadatas']]}")

        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        print("\nDebug - Raw query results:")
        print(json.dumps(results, indent=2, ensure_ascii=False))

        return {
            "results": {
                "documents": [doc for doc in results["documents"][0]],
                "metadata": results["metadatas"][0],
                "distances": results["distances"][0]
            },
            "query": query_text
        }

    except Exception as e:
        print(f"Error querying database: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

async def analyze_with_reflection(query_text: str, context: str = ""):
    """Analyze documents with self-reflection capabilities"""

    # Run analysis with reflection
    query = QueryInput(query=query_text, context=context)
    try:
        response = await agent.run(
            user_prompt=f"Analyze the following query with self-reflection: {query_text}",
            deps=query
        )
        return response.data
    except Exception as e:
        print(f"Error in analyze_with_reflection: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise

async def handle_questions(query: str, context: str = "") -> Dict:
    """Handle asking questions about the knowledge base with reflection"""
    try:
        response = await analyze_with_reflection(query, context)

        # Format response as a dictionary
        formatted_response = {
            "reflection": {
                "understanding": response.reflection.understanding,
                "confidence": response.reflection.confidence,
                "needs_clarification": response.reflection.needs_clarification,
                "follow_up_questions": response.reflection.follow_up_questions,
                "search_strategy": response.reflection.search_strategy
            },
            "findings": response.findings,
            "evidence": response.evidence,
            "confidence": response.confidence,
            "recommendations": response.recommendations,
            "limitations": response.limitations
        }

        print(formatted_response)
        return formatted_response

    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

async def add_document(file_path: str):
    """Add a document to the vector database"""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return False

    print(f"\nProcessing {file_path}...")
    if process_file(file_path):
        print(f"\nSuccessfully added {file_path} to the vector database")
        return True
    else:
        print(f"\nFailed to add {file_path} to the vector database")
        return False

async def list_documents():
    """List all documents in the vector database"""
    files = list_files_in_db()
    if files:
        print("\nFiles in vector database:")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")
        return files
    else:
        print("\nNo files found in vector database")
        return []

async def remove_document(file_name: str):
    """Remove a document from the vector database"""
    if remove_file_from_db(file_name):
        print(f"\nSuccessfully removed {file_name} from the vector database")
        return True
    else:
        print(f"\nFailed to remove {file_name} from the vector database")
        return False

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

async def print_menu():
    """Print the main menu"""
    clear_screen()
    print("\n===  FC RAG Knowledge Base ===")
    print("\n1. Add File to Knowledge Base")
    print("2. List and Remove Files")
    print("3. Ask Questions About Knowledge Base")
    print("4. Exit")
    print("\nSelect an option (1-4): ")

async def handle_add_file():
    """Handle adding a file to the knowledge base"""
    while True:
        await print_menu()
        choice = input("\nSelect an option (1-4): ")

        if choice == "1":
            # Get file path
            file_path = input("\nEnter the path to the file: ")

            try:
                # Process file and get chunks
                chunks = process_file(file_path)

                if chunks:
                    print(f"\nSuccessfully added {file_path} to the knowledge base")

                    # Show current files in database
                    print("\nCurrent files in knowledge base:")
                    files = list_files_in_db()
                    for i, file in enumerate(files, 1):
                        print(f"{i}. {file}")

                else:
                    print(f"\nFailed to add {file_path} to the knowledge base")

            except Exception as e:
                print(f"\nError processing file: {e}")

            input("\nPress Enter to continue...")

        elif choice == "2":
            return
        else:
            print("\nInvalid option")
            input("\nPress Enter to continue...")

async def handle_list_and_remove():
    """Handle listing and removing files"""
    while True:
        clear_screen()
        print("\n=== List and Remove Files ===")
        files = list_files_in_db()

        if not files:
            input("\nPress Enter to return to main menu...")
            return

        print("\nOptions:")
        print("1. Remove a file")
        print("2. Return to main menu")

        choice = input("\nSelect an option (1-2): ")

        if choice == "1":
            file_num = input("\nEnter the number of the file to remove: ")
            try:
                file_num = int(file_num)
                if 1 <= file_num <= len(files):
                    file_to_remove = files[file_num - 1]
                    confirm = input(f"\nAre you sure you want to remove '{file_to_remove}'? (y/n): ")
                    if confirm.lower() == 'y':
                        if remove_file_from_db(file_to_remove):
                            print(f"\nSuccessfully removed {file_to_remove}")
                        else:
                            print(f"\nFailed to remove {file_to_remove}")
                    else:
                        print("\nOperation cancelled")
                    input("\nPress Enter to continue...")
                else:
                    print("\nInvalid file number")
                    input("\nPress Enter to continue...")
            except ValueError:
                print("\nInvalid input")
                input("\nPress Enter to continue...")
        elif choice == "2":
            return
        else:
            print("\nInvalid option")
            input("\nPress Enter to continue...")

async def main():
    """Main interactive menu loop"""
    while True:
        await print_menu()
        choice = input().strip()

        if choice == "1":
            await handle_add_file()
        elif choice == "2":
            await handle_list_and_remove()
        elif choice == "3":
            query = input("\nEnter your question: ")
            context = input("\nOptional - Provide any additional context: ")
            response = await handle_questions(query, context)
            print("\nResponse:")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            input("\nPress Enter to continue...")
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    asyncio.run(main())
