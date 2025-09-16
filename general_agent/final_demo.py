#!/usr/bin/env python3
"""
🎯 FINAL DEMO: Enhanced Gemini COT Agent with Jina AI Web Search
Your agent is now ready with advanced capabilities!
"""

from agent_function import GeminiCOTAgent, quick_ask
import os

def main():
    print("🤖 Enhanced Gemini Chain of Thought Agent")
    print("🔍 Now with Jina AI Web Search Integration!")
    print("=" * 60)
    
    # Your API keys
    gemini_key = "AIzaSyDTa2e6FIBjh56icX-umgw3vHn3AuYeoeo"
    jina_key = "jina_71f1ffcdfde24902b9ee1810eb610071IFuOaEq5N_7Ffrux68bSyEET_YpT"
    
    # Initialize the enhanced agent
    agent = GeminiCOTAgent(
        gemini_api_key=gemini_key,
        jina_api_key=jina_key
    )
    
    print("✅ Agent initialized with:")
    print(f"   🧠 Gemini API: {gemini_key[:20]}...")
    print(f"   🔍 Jina API: {jina_key[:20]}...")
    
    print("\n🎯 Agent Capabilities:")
    print("• 🤔 Chain of Thought reasoning")
    print("• 🔍 Automatic web search for current information")
    print("• 🤖 Smart search query generation")
    print("• 📊 Integration of search results into responses")
    print("• ⚙️ Configurable search enable/disable")
    
    print("\n" + "=" * 60)
    print("📋 USAGE EXAMPLES:")
    print("=" * 60)
    
    # Example 1: Quick Ask
    print("\n1️⃣ Quick Ask (with web search)")
    print("-" * 40)
    
    question1 = "What are the latest developments in electric vehicles?"
    print(f"Question: {question1}")
    
    # Using quick_ask function
    response1 = quick_ask(question1, gemini_api_key=gemini_key, jina_api_key=jina_key)
    print("\n🤖 Response:")
    print(response1[:300] + "..." if len(response1) > 300 else response1)
    
    # Example 2: Detailed Response
    print("\n\n2️⃣ Detailed Response with Search Info")
    print("-" * 40)
    
    question2 = "How does artificial intelligence work?"
    print(f"Question: {question2}")
    
    response2 = agent.think_and_respond(question2, enable_search=True)
    
    print(f"\n🔍 Search Used: {response2['search_info']['used_search']}")
    if response2['search_info']['used_search']:
        print(f"   Query: {response2['search_info']['query']}")
        print(f"   Results: {len(response2['search_info']['results'])}")
    
    print("\n🤔 Thinking:")
    print(response2['thinking'][:200] + "..." if len(response2['thinking']) > 200 else response2['thinking'])
    
    print("\n📝 Answer:")
    print(response2['answer'][:300] + "..." if len(response2['answer']) > 300 else response2['answer'])
    
    # Example 3: Control Search
    print("\n\n3️⃣ Search Control")
    print("-" * 40)
    
    question3 = "What is the capital of France?"
    print(f"Question: {question3}")
    
    # Disable search for this general knowledge question
    response3 = agent.think_and_respond(question3, enable_search=False)
    print(f"\n🚫 Search Disabled - Used: {response3['search_info']['used_search']}")
    print(f"📝 Answer: {response3['answer']}")
    
    print("\n\n" + "=" * 60)
    print("🎊 CONGRATULATIONS!")
    print("=" * 60)
    print("Your Gemini COT Agent now has advanced capabilities:")
    print()
    print("🧠 REASONING: Uses Chain of Thought to think step by step")
    print("🔍 WEB SEARCH: Automatically searches for current information")
    print("🤖 INTELLIGENCE: Integrates web results into thoughtful responses")
    print("⚙️ FLEXIBILITY: Configurable search and response parameters")
    print()
    print("🚀 Ready to use for:")
    print("• Research and fact-checking")
    print("• Current events and news analysis")
    print("• Technical questions with latest information")
    print("• Educational content with up-to-date data")
    print("• General conversation with enhanced knowledge")
    
    print("\n💡 Next Steps:")
    print("• Try agent.interactive_chat() for conversation")
    print("• Use enable_search=True/False to control search")
    print("• Experiment with different question types")
    print("• Build upon this foundation for your specific needs")
    
    print("\n🎯 Your enhanced AI agent is ready to use!")

if __name__ == "__main__":
    main()
