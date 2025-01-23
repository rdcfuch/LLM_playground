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

def analyze_document(query_text: str):
    """Analyze a document using the agent"""
    # First, let's directly query the vector database to see the results
    print("\nQuerying vector database directly:")
    results = query_vector_db(query_text)
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
    query = QueryInput(query=query_text)
    response = agent5.run_sync(
        user_prompt="Please analyze the documents for any evidence of termites.",
        deps=query
    )

    # Print results
    print("\nAnalysis Results:")
    print(response.data.model_dump_json(indent=2))

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

def handle_questions():
    """Handle asking questions about the knowledge base"""
    while True:
        clear_screen()
        print("\n=== Ask Questions About Knowledge Base ===")
        print("\nOptions:")
        print("1. Ask a question")
        print("2. Return to main menu")
        
        choice = input("\nSelect an option (1-2): ")
        
        if choice == "1":
            query = input("\nEnter your question: ")
            analyze_document(query)
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
