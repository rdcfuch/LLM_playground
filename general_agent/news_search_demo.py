#!/usr/bin/env python3
"""
News Search Demo - Test the agent's web search capabilities with news queries.
"""

from agent_function import GeminiCOTAgent

def main():
    print("🔍 **News Search Demo**")
    print("=" * 50)
    
    # Initialize the agent
    agent = GeminiCOTAgent(
        gemini_api_key='AIzaSyDTa2e6FIBjh56icX-umgw3vHn3AuYeoeo',
        jina_api_key='jina_71f1ffcdfde24902b9ee1810eb610071IFuOaEq5N_7Ffrux68bSyEET_YpT'
    )
    
    # Test questions that should trigger web search
    test_questions = [
        "What are today's top 3 news stories?",
        "What are the latest AI developments?",
        "What's happening in the world today?",
        "Current events in technology"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n**Test {i}: {question}**")
        print("-" * 40)
        
        response = agent.think_and_respond(question, enable_search=True)
        
        # Show search info
        if response["search_info"]["used_search"]:
            print(f"🔍 **Web Search Used:** {response['search_info']['query']}")
            print(f"📊 **Results Found:** {len(response['search_info']['results'])}")
        else:
            print("🚫 **No web search used**")
        
        # Show response
        print(f"\n🤔 **Thinking:** {response['thinking'][:200]}...")
        print(f"\n📝 **Answer:** {response['answer'][:300]}...")
        print("=" * 50)

if __name__ == "__main__":
    main()
