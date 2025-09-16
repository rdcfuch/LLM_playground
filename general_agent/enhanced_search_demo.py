#!/usr/bin/env python3
"""
Enhanced News Search Demo - Test with more specific queries to get better results.
"""

from agent_function import GeminiCOTAgent

def main():
    print("🔍 **Enhanced News Search Demo**")
    print("=" * 60)
    
    # Initialize the agent
    agent = GeminiCOTAgent(
        gemini_api_key='AIzaSyDTa2e6FIBjh56icX-umgw3vHn3AuYeoeo',
        jina_api_key='jina_71f1ffcdfde24902b9ee1810eb610071IFuOaEq5N_7Ffrux68bSyEET_YpT'
    )
    
    # More specific test questions that should get better content
    test_questions = [
        "Apple iPhone 16 release news September 2024",
        "Tesla stock price latest news",
        "ChatGPT new features 2024",
        "What companies announced AI products this week?",
        "Google Pixel 9 review"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n**Test {i}: {question}**")
        print("-" * 50)
        
        response = agent.think_and_respond(question, enable_search=True)
        
        # Show search info
        if response["search_info"]["used_search"]:
            print(f"🔍 **Search Query:** {response['search_info']['query']}")
            print(f"📊 **Results:** {len(response['search_info']['results'])}")
            
            # Show first search result title and content preview
            if response['search_info']['results']:
                first_result = response['search_info']['results'][0]
                print(f"📰 **Top Result:** {first_result.get('title', 'No title')[:80]}...")
                print(f"🔗 **URL:** {first_result.get('url', 'No URL')}")
                content_preview = first_result.get('content', 'No content')[:150]
                print(f"📄 **Content Preview:** {content_preview}...")
        else:
            print("🚫 **No web search used**")
        
        # Show response
        print(f"\n📝 **Answer:** {response['answer'][:400]}...")
        print("=" * 60)

if __name__ == "__main__":
    main()
