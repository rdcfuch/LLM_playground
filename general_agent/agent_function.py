import google.generativeai as genai
import requests
import os
from typing import Optional, Dict, Any, List
import json
import time


class GeminiCOTAgent:
    """
    A Gemini-powered agent with Chain of Thought reasoning capability and web search.
    The agent will think step by step before providing answers and can search the web for current information.
    """
    
    def __init__(self, 
                 gemini_api_key: str = "AIzaSyDTa2e6FIBjh56icX-umgw3vHn3AuYeoeo", 
                 jina_api_key: Optional[str] = None,
                 model_name: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini COT Agent with web search capabilities.
        
        Parameters:
        - gemini_api_key (str): Gemini API key
        - jina_api_key (str): Jina AI API key for web search (get from https://jina.ai/?sui=apikey)
        - model_name (str): Gemini model to use
        """
        self.gemini_api_key = gemini_api_key
        self.jina_api_key = jina_api_key or os.getenv('JINA_API_KEY')
        self.model_name = model_name
        
        # Configure the Gemini API
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        # Chain of Thought prompt template with web search capability
        self.cot_prompt_template = """
You are an intelligent AI assistant with Chain of Thought reasoning and web search capabilities. For every question or problem, you must:

1. **Think First**: Break down the problem, analyze what's being asked, and determine if web search is needed
2. **Search if Needed**: If the question requires current information or facts not in your training data, use web search
3. **Reason Step by Step**: Work through the problem methodically, incorporating search results if available
4. **Provide Answer**: Give a clear, well-reasoned final answer

{search_results_context}

Format your response as follows:
🤔 **Thinking:**
[Your step-by-step analysis and reasoning process here]

📝 **Answer:**
[Your final answer here]

Now, please respond to this question: {user_question}
"""

        self.search_prompt_template = """
Based on this question, determine if web search is needed and what to search for:

Question: {question}

If web search would help answer this question (e.g., current events, recent information, specific facts), 
provide ONLY a clean search query without any prefix text. If not, respond with "NO_SEARCH".

Examples:
- Question: "What are today's top news stories?" → today top news stories
- Question: "What is 2+2?" → NO_SEARCH
- Question: "Latest AI developments" → latest AI developments 2024

Response:"""

    def search_web(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using Jina AI's Search API.
        
        Parameters:
        - query (str): Search query
        - num_results (int): Number of results to return
        
        Returns:
        - Dict containing search results
        """
        if not self.jina_api_key:
            return {
                "error": "Jina API key not provided. Get your free key from https://jina.ai/?sui=apikey",
                "results": []
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jina_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-No-Cache": "true"  # Get fresh results
            }
            
            data = {
                "q": query,
                "num": num_results
            }
            
            response = requests.post(
                "https://s.jina.ai/",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                search_data = response.json()
                return {
                    "success": True,
                    "results": search_data.get("data", []),
                    "query": query
                }
            else:
                return {
                    "error": f"Search API error: {response.status_code} - {response.text}",
                    "results": []
                }
                
        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "results": []
            }

    def determine_search_need(self, question: str) -> str:
        """
        Determine if web search is needed for the question and what to search for.
        
        Parameters:
        - question (str): The user's question
        
        Returns:
        - str: Search query or "NO_SEARCH"
        """
        try:
            search_prompt = self.search_prompt_template.format(question=question)
            
            response = self.model.generate_content(
                search_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=100
                )
            )
            
            search_decision = response.text.strip()
            
            # Clean up the search query - remove common prefixes
            if search_decision and search_decision != "NO_SEARCH":
                # Remove common prefixes that might be added by the model
                search_decision = search_decision.replace("Search query:", "").strip()
                search_decision = search_decision.replace("Query:", "").strip()
                search_decision = search_decision.strip('"\'')  # Remove quotes
                
                return search_decision if search_decision else None
            
            return None
            
        except Exception as e:
            print(f"Error determining search need: {str(e)}")
            return None

    def think_and_respond(self, user_question: str, temperature: float = 0.7, max_tokens: int = 1000, enable_search: bool = True) -> Dict[str, str]:
        """
        Generate a response using Chain of Thought reasoning with optional web search.
        
        Parameters:
        - user_question (str): The user's question or prompt
        - temperature (float): Controls randomness (0.0 to 1.0)
        - max_tokens (int): Maximum tokens in response
        - enable_search (bool): Whether to use web search if needed
        
        Returns:
        - Dict[str, str]: Dictionary containing 'thinking', 'answer', 'full_response', and search info
        """
        try:
            search_results_context = ""
            search_info = {"used_search": False, "query": None, "results": []}
            
            # Determine if web search is needed
            if enable_search and self.jina_api_key:
                search_query = self.determine_search_need(user_question)
                
                if search_query:
                    print(f"🔍 Searching web for: {search_query}")
                    search_results = self.search_web(search_query)
                    
                    if search_results.get("success") and search_results.get("results"):
                        search_info["used_search"] = True
                        search_info["query"] = search_query
                        search_info["results"] = search_results["results"]
                        
                        # Format search results for the prompt
                        search_context = "**Web Search Results:**\n"
                        for i, result in enumerate(search_results["results"][:3], 1):  # Use top 3 results
                            search_context += f"{i}. **{result.get('title', 'No title')}**\n"
                            search_context += f"   URL: {result.get('url', 'No URL')}\n"
                            search_context += f"   Content: {result.get('content', 'No content')[:300]}...\n\n"
                        
                        search_results_context = search_context
                    elif search_results.get("error"):
                        search_results_context = f"**Search Error:** {search_results['error']}\n\n"
            
            # Format the prompt with COT structure and search results
            formatted_prompt = self.cot_prompt_template.format(
                user_question=user_question,
                search_results_context=search_results_context
            )
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # Generate response
            response = self.model.generate_content(
                formatted_prompt,
                generation_config=generation_config
            )
            
            # Parse the response to extract thinking and answer sections
            full_response = response.text
            thinking_section = ""
            answer_section = ""
            
            # Extract thinking and answer sections
            if "🤔 **Thinking:**" in full_response and "📝 **Answer:**" in full_response:
                parts = full_response.split("📝 **Answer:**")
                thinking_part = parts[0].replace("🤔 **Thinking:**", "").strip()
                answer_part = parts[1].strip() if len(parts) > 1 else ""
                
                thinking_section = thinking_part
                answer_section = answer_part
            else:
                # Fallback if format is not followed
                thinking_section = "The AI provided a direct response without explicit COT formatting."
                answer_section = full_response
            
            return {
                "thinking": thinking_section,
                "answer": answer_section,
                "full_response": full_response,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "search_info": search_info
            }
            
        except Exception as e:
            error_response = f"An error occurred: {str(e)}"
            return {
                "thinking": "Error in processing the request.",
                "answer": error_response,
                "full_response": error_response,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "search_info": {"used_search": False, "query": None, "results": [], "error": str(e)}
            }

    def interactive_chat(self):
        """
        Start an interactive chat session with the COT agent with web search.
        """
        print("🤖 Gemini COT Agent with Web Search initialized!")
        print("💭 I will think step by step before answering your questions.")
        print("🔍 I can search the web for current information when needed.")
        if not self.jina_api_key:
            print("⚠️  Note: No Jina API key provided. Web search disabled.")
            print("   Get your free key from: https://jina.ai/?sui=apikey")
        print("Type 'quit' to exit, 'nosearch' to disable search for next question.\n")
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Thanks for chatting with the COT Agent!")
                    break
                
                # Check for search control
                enable_search = True
                if user_input.lower().startswith('nosearch '):
                    enable_search = False
                    user_input = user_input[9:]  # Remove 'nosearch ' prefix
                    print("🚫 Web search disabled for this question.")
                
                if not user_input:
                    print("Please enter a question or statement.")
                    continue
                
                print("\n🔄 Processing your question...")
                
                # Get response from the agent
                response = self.think_and_respond(user_input, enable_search=enable_search)
                
                # Display search information if used
                if response["search_info"]["used_search"]:
                    print(f"\n🔍 **Web Search:** {response['search_info']['query']}")
                    print(f"📊 **Found {len(response['search_info']['results'])} results**")
                
                # Display the thinking process and answer
                print("\n" + "="*60)
                print("🤔 **My Thinking Process:**")
                print(response["thinking"])
                print("\n" + "-"*40)
                print("📝 **My Answer:**")
                print(response["answer"])
                print("="*60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Input ended. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")
                # Add a small delay to prevent tight error loops
                import time
                time.sleep(0.1)

    def batch_questions(self, questions: List[str]) -> List[Dict[str, str]]:
        """
        Process multiple questions in batch.
        
        Parameters:
        - questions (List[str]): List of questions to process
        
        Returns:
        - List[Dict[str, str]]: List of responses for each question
        """
        responses = []
        
        for i, question in enumerate(questions, 1):
            print(f"Processing question {i}/{len(questions)}: {question[:50]}...")
            response = self.think_and_respond(question)
            responses.append({
                "question": question,
                **response
            })
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
        
        return responses


def quick_ask(question: str, 
              gemini_api_key: str = "AIzaSyDTa2e6FIBjh56icX-umgw3vHn3AuYeoeo",
              jina_api_key: Optional[str] = None,
              enable_search: bool = True) -> str:
    """
    Quick function to ask a question with COT reasoning and optional web search.
    
    Parameters:
    - question (str): The question to ask
    - gemini_api_key (str): Gemini API key
    - jina_api_key (str): Jina API key for web search (optional)
    - enable_search (bool): Whether to enable web search
    
    Returns:
    - str: The full response with thinking and answer
    """
    agent = GeminiCOTAgent(
        gemini_api_key=gemini_api_key, 
        jina_api_key=jina_api_key
    )
    response = agent.think_and_respond(question, enable_search=enable_search)
    return response["full_response"]


# Example usage and testing
if __name__ == "__main__":
    # Initialize the COT agent with web search
    print("🤖 Initializing Gemini COT Agent with Web Search...")
    
    # Note: Set your Jina API key for web search capabilities
    # Get your free key from: https://jina.ai/?sui=apikey
    jina_key = os.getenv('JINA_API_KEY')  # Set this environment variable
    
    agent = GeminiCOTAgent(jina_api_key=jina_key)
    
    # Example questions to demonstrate COT reasoning with and without search
    example_questions = [
        {
            "question": "What is the capital of Japan and why is it significant?",
            "search": False,  # This is general knowledge
            "description": "General Knowledge (No Search)"
        },
        {
            "question": "What are the latest developments in AI technology in 2025?",
            "search": True,  # This requires current information
            "description": "Current Information (With Search)"
        },
        {
            "question": "If I have 15 apples and give away 7, then buy 12 more, how many apples do I have?",
            "search": False,  # This is a math problem
            "description": "Mathematical Problem (No Search)"
        }
    ]
    
    print("🚀 Testing Gemini COT Agent with Web Search capabilities...")
    print("="*80)
    
    for i, example in enumerate(example_questions, 1):
        print(f"\n📋 Example {i}: {example['description']}")
        print(f"Question: {example['question']}")
        print(f"Search Enabled: {example['search']}")
        print("-" * 60)
        
        response = agent.think_and_respond(
            example['question'], 
            enable_search=example['search']
        )
        
        # Show search info if search was used
        if response["search_info"]["used_search"]:
            print(f"🔍 **Web Search Used:** {response['search_info']['query']}")
            print(f"📊 **Results Found:** {len(response['search_info']['results'])}")
            print()
        
        print("🤔 **Thinking:**")
        print(response["thinking"][:300] + "..." if len(response["thinking"]) > 300 else response["thinking"])
        print("\n📝 **Answer:**")
        print(response["answer"][:400] + "..." if len(response["answer"]) > 400 else response["answer"])
        print("\n" + "="*80)
        
        time.sleep(2)  # Pause between questions
    
    print("\n💡 **Usage Tips:**")
    print("1. Set JINA_API_KEY environment variable for web search")
    print("2. Web search is automatically determined based on question type")
    print("3. Use enable_search=False to disable search for specific questions")
    print("4. Get your free Jina API key: https://jina.ai/?sui=apikey")
    
    # Uncomment the line below to start interactive chat
    # agent.interactive_chat()
