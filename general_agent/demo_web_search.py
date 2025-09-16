#!/usr/bin/env python3
"""
Demo script for the Enhanced Gemini COT Agent with Web Search
Shows how to use the agent with Jina AI web search capabilities
"""

import os
from agent_function import GeminiCOTAgent, quick_ask

def demo_without_search():
    """Demo: Agent without web search (general knowledge)"""
    print("="*60)
    print("🎯 DEMO: COT Agent without Web Search")
    print("="*60)
    
    agent = GeminiCOTAgent()  # No Jina API key
    
    question = "What is photosynthesis and how does it work?"
    print(f"Question: {question}\n")
    
    response = agent.think_and_respond(question, enable_search=False)
    
    print("🤔 **Thinking Process:**")
    print(response["thinking"][:300] + "..." if len(response["thinking"]) > 300 else response["thinking"])
    print("\n📝 **Final Answer:**")
    print(response["answer"][:300] + "..." if len(response["answer"]) > 300 else response["answer"])
    print(f"\n🔍 **Search Used:** {response['search_info']['used_search']}")
    print("\n" + "="*60)

def demo_with_search_simulation():
    """Demo: Show what happens when search is requested but no API key is available"""
    print("\n🔍 DEMO: COT Agent with Search Request (No API Key)")
    print("="*60)
    
    agent = GeminiCOTAgent()  # No Jina API key
    
    question = "What are the latest AI breakthroughs in 2025?"
    print(f"Question: {question}")
    print("Note: This would normally trigger web search but we don't have a Jina API key\n")
    
    response = agent.think_and_respond(question, enable_search=True)
    
    print("🤔 **Thinking Process:**")
    print(response["thinking"][:300] + "..." if len(response["thinking"]) > 300 else response["thinking"])
    print("\n📝 **Final Answer:**")
    print(response["answer"][:300] + "..." if len(response["answer"]) > 300 else response["answer"])
    print(f"\n🔍 **Search Used:** {response['search_info']['used_search']}")
    if 'error' in response['search_info']:
        print(f"⚠️ **Search Error:** {response['search_info']['error']}")
    print("\n" + "="*60)

def demo_quick_ask():
    """Demo: Quick ask function"""
    print("\n🚀 DEMO: Quick Ask Function")
    print("="*60)
    
    question = "How do neural networks learn?"
    print(f"Question: {question}\n")
    
    response = quick_ask(question, enable_search=False)
    print(response[:400] + "..." if len(response) > 400 else response)
    print("\n" + "="*60)

def demo_setup_instructions():
    """Demo: Show how to set up web search"""
    print("\n⚙️ DEMO: Setting up Web Search")
    print("="*60)
    
    print("To enable web search capabilities:")
    print("1. Get a free Jina API key from: https://jina.ai/?sui=apikey")
    print("2. Set the environment variable:")
    print("   export JINA_API_KEY='your-api-key-here'")
    print("3. Or pass it directly to the agent:")
    print("   agent = GeminiCOTAgent(jina_api_key='your-key')")
    print("\nWith web search enabled, the agent can:")
    print("• Search for current events and recent information")
    print("• Get real-time data and facts")
    print("• Automatically determine when search is needed")
    print("• Provide more accurate and up-to-date answers")
    
    # Check if JINA_API_KEY is set
    jina_key = os.getenv('JINA_API_KEY')
    if jina_key:
        print(f"\n✅ JINA_API_KEY is set: {jina_key[:10]}..." if len(jina_key) > 10 else jina_key)
        print("🔍 Web search is ready to use!")
        
        # Demo with actual search if key is available
        print("\n🎯 Testing actual web search...")
        agent = GeminiCOTAgent(jina_api_key=jina_key)
        response = agent.think_and_respond("What's the weather like today?", enable_search=True)
        
        if response['search_info']['used_search']:
            print(f"✅ Search successful! Query: {response['search_info']['query']}")
            print(f"📊 Found {len(response['search_info']['results'])} results")
        else:
            print("ℹ️ Search was not triggered for this question")
    else:
        print("\n❌ JINA_API_KEY is not set")
        print("🔍 Web search is currently disabled")
    
    print("\n" + "="*60)

def main():
    """Run all demos"""
    print("🤖 Enhanced Gemini COT Agent with Web Search - Demo")
    print("This demo shows the new web search capabilities\n")
    
    try:
        # Demo 1: Without search
        demo_without_search()
        
        # Demo 2: Search request without API key
        demo_with_search_simulation()
        
        # Demo 3: Quick ask
        demo_quick_ask()
        
        # Demo 4: Setup instructions
        demo_setup_instructions()
        
        print("\n✅ All demos completed!")
        print("\n📝 **Key Features Added:**")
        print("1. 🔍 Automatic web search when needed")
        print("2. 🤖 Smart search query generation")
        print("3. 📊 Integration of search results into responses")
        print("4. ⚙️ Configurable search enable/disable")
        print("5. 🛡️ Robust error handling for search failures")
        
        print("\n💡 **Next Steps:**")
        print("1. Get your Jina API key: https://jina.ai/?sui=apikey")
        print("2. Set JINA_API_KEY environment variable")
        print("3. Try questions requiring current information!")
        
    except Exception as e:
        print(f"❌ Error during demo: {str(e)}")

if __name__ == "__main__":
    main()
