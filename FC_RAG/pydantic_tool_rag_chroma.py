from typing import Dict, List, Optional
import nest_asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel
import os
import json
from utils.chroma_v_db import query_vector_db, process_file, remove_file_from_db, list_files_in_db

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

def analyze_with_reflection(query_text: str, context: str = ""):
    """Analyze documents with self-reflection capabilities"""
    
    # Initialize agent with enhanced prompt for self-reflection
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
        ),
        tools=[Tool(query_vector_db, takes_ctx=True)],
    )

    @agent.tool_plain()
    def refine_search(initial_results: str, focus_area: str) -> str:
        """Refine the search based on initial results and a specific focus area."""
        try:
            # Parse initial results
            results = json.loads(initial_results)
            if not results.get("results", {}).get("documents"):
                raise ModelRetry(
                    "No relevant documents found. Consider:\n"
                    "1. Broadening the search terms\n"
                    "2. Checking if documents are properly loaded\n"
                    "3. Using alternative keywords"
                )
            
            # Perform refined search
            refined_query = f"{query_text} {focus_area}"
            refined_results = query_vector_db(refined_query)
            return refined_results
            
        except json.JSONDecodeError:
            raise ModelRetry("Error parsing search results. Please try a different search approach.")

    # First, query the vector database
    print("\nInitial Search Results:")
    results = query_vector_db(query_text)
    print(json.dumps(json.loads(results), indent=2))

    # Run analysis with reflection
    query = QueryInput(query=query_text, context=context)
    response = agent.run_sync(
        user_prompt=f"Analyze the following query with self-reflection: {query_text}",
        deps=query
    )

    # Print results with reflection details
    print("\nAnalysis Results (with Reflection):")
    print(json.dumps(json.loads(response.data.model_dump_json()), indent=2))
    
    return response.data

def handle_questions():
    """Handle asking questions about the knowledge base with reflection"""
    while True:
        clear_screen()
        print("\n=== Ask Questions About Knowledge Base ===")
        print("\nOptions:")
        print("1. Ask a question")
        print("2. Return to main menu")
        
        choice = input("\nSelect an option (1-2): ")
        
        if choice == "1":
            query = input("\nEnter your question: ")
            context = input("\nOptional - Provide any additional context: ")
            
            try:
                response = analyze_with_reflection(query, context)
                
                # Display reflection process
                print("\n=== Analysis Process ===")
                print(f"\nQuery Understanding:")
                print(f"- {response.reflection.understanding}")
                print(f"- Confidence: {response.reflection.confidence:.2f}")
                
                if response.reflection.needs_clarification:
                    print("\nClarification Needed:")
                    for q in response.reflection.follow_up_questions:
                        print(f"- {q}")
                
                print("\n=== Findings ===")
                for topic, findings in response.findings.items():
                    print(f"\n{topic}:")
                    for finding in findings:
                        print(f"- {finding}")
                
                if response.limitations:
                    print("\nLimitations:")
                    for limitation in response.limitations:
                        print(f"- {limitation}")
                
                if response.recommendations:
                    print("\nRecommendations:")
                    for rec in response.recommendations:
                        print(f"- {rec}")
                
            except Exception as e:
                print(f"\nError during analysis: {e}")
            
            input("\nPress Enter to continue...")
        elif choice == "2":
            return
        else:
            print("\nInvalid option")
            input("\nPress Enter to continue...")

def add_document(file_path: str):
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

def list_documents():
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

def remove_document(file_name: str):
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

def print_menu():
    """Print the main menu"""
    clear_screen()
    print("\n=== Termite Inspection Knowledge Base ===")
    print("\n1. Add File to Knowledge Base")
    print("2. List and Remove Files")
    print("3. Ask Questions About Knowledge Base")
    print("4. Exit")
    print("\nSelect an option (1-4): ")

def handle_add_file():
    """Handle adding a file to the knowledge base"""
    clear_screen()
    print("\n=== Add File to Knowledge Base ===")
    file_path = input("\nEnter the path to the file: ")
    add_document(file_path)
    input("\nPress Enter to continue...")

def handle_list_and_remove():
    """Handle listing and removing files"""
    while True:
        clear_screen()
        print("\n=== List and Remove Files ===")
        files = list_documents()
        
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
                    remove_document(files[file_num - 1])
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

def main():
    """Main interactive menu loop"""
    while True:
        print_menu()
        choice = input().strip()
        
        if choice == "1":
            handle_add_file()
        elif choice == "2":
            handle_list_and_remove()
        elif choice == "3":
            handle_questions()
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
