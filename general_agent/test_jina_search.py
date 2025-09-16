#!/usr/bin/env python3
"""
Test script showing how to set up and use the Jina AI web search functionality
Run this after setting up your Jina API key
"""

import os
from agent_function import GeminiCOTAgent

def test_with_jina_key():
    """Test the agent with a Jina API key"""
    
    # Replace 'your-jina-api-key' with your actual key
    # Or set the JINA_API_KEY environment variable
    jina_key = os.getenv('JINA_API_KEY') or 'your-jina-api-key-here'
    
    if jina_key == 'your-jina-api-key-here':
        print("⚠️  Please set your Jina API key!")
        print("1. Get a free key from: https://jina.ai/?sui=apikey")
        print("2. Replace 'your-jina-api-key-here' in this script")
        print("3. Or set environment variable: export JINA_API_KEY='your-key'")
        return
    
    print("🤖 Testing Gemini COT Agent with Jina Web Search")
    print("=" * 60)
    
    # Initialize agent with Jina API key
    agent = GeminiCOTAgent(jina_api_key=jina_key)
    
    # Test questions that should trigger web search
    test_questions = [
        "What are the latest developments in AI in 2025?",
        "Current weather in San Francisco",
        "Recent news about SpaceX",
        "Latest stock market trends"
    ]
    
    for question in test_questions:
        print(f"\n📋 Question: {question}")
        print("-" * 40)
        
        try:
            response = agent.think_and_respond(question, enable_search=True)
            
            # Show search information
            if response['search_info']['used_search']:
                print(f"🔍 **Search Query:** {response['search_info']['query']}")
                print(f"📊 **Results Found:** {len(response['search_info']['results'])}")
                
                # Show first result as example
                if response['search_info']['results']:
                    first_result = response['search_info']['results'][0]
                    print(f"📰 **First Result:** {first_result.get('title', 'No title')}")
                    print(f"🔗 **URL:** {first_result.get('url', 'No URL')}")
                
                print("\n🤔 **AI Thinking:**")
                print(response['thinking'][:200] + "..." if len(response['thinking']) > 200 else response['thinking'])
                
                print("\n📝 **AI Answer:**")
                print(response['answer'][:300] + "..." if len(response['answer']) > 300 else response['answer'])
            else:
                print("ℹ️ Search was not triggered for this question")
                print(f"🤔 **AI Response:** {response['answer'][:200]}...")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n" + "=" * 60)
    
    print("\n✅ Web search testing complete!")
    print("\n💡 **What happened:**")
    print("• The agent analyzed each question")
    print("• It determined which questions needed current information")
    print("• For those questions, it generated search queries")
    print("• It retrieved web results using Jina AI")
    print("• It incorporated the results into its reasoning")
    print("• It provided informed, up-to-date answers")

def test_search_control():
    """Test enabling/disabling search"""
    print("\n🎛️ Testing Search Control")
    print("=" * 60)
    
    agent = GeminiCOTAgent()  # No Jina key for this test
    
    question = "What is artificial intelligence?"
    
    # Test with search disabled
    print("🚫 Test 1: Search disabled")
    response1 = agent.think_and_respond(question, enable_search=False)
    print(f"Search used: {response1['search_info']['used_search']}")
    
    # Test with search enabled (but no API key)
    print("\n🔍 Test 2: Search enabled (no API key)")
    response2 = agent.think_and_respond(question, enable_search=True)
    print(f"Search used: {response2['search_info']['used_search']}")
    
    print("\n✅ Search control testing complete!")

if __name__ == "__main__":
    print("🧪 Jina AI Web Search Integration Test")
    print("This script demonstrates the web search capabilities")
    print("\nChoose a test:")
    print("1. Test with Jina API key (requires valid key)")
    print("2. Test search control (no key needed)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_with_jina_key()
    elif choice == "2":
        test_search_control()
    else:
        print("Invalid choice. Running search control test...")
        test_search_control()
