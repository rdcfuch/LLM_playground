#!/usr/bin/env python3
"""
Interactive example for the Enhanced Gemini COT Agent with Web Search
Run this script to start a conversation with the thinking agent that can search the web
"""

from agent_function import GeminiCOTAgent

def main():
    print("🤖 Welcome to the Enhanced Gemini Chain of Thought Agent!")
    print("💭 I will think step by step before answering your questions.")
    print("🔍 I can also search the web for current information when needed.")
    print("🔧 Using Gemini API: AIzaSyDTa2e6FIBjh56icX-umgw3vHn3AuYeoeo")
    print("🔧 Using Jina API: jina_71f1ffcdfde24902b9ee1810eb610071IFuOaEq5N_7Ffrux68bSyEET_YpT")
    print("="*80)
    
    # Initialize the agent with both API keys
    agent = GeminiCOTAgent(
        gemini_api_key="AIzaSyDTa2e6FIBjh56icX-umgw3vHn3AuYeoeo",
        jina_api_key="jina_71f1ffcdfde24902b9ee1810eb610071IFuOaEq5N_7Ffrux68bSyEET_YpT"
    )
    
    print("✅ Agent initialized with web search capabilities!")
    print("\n🎯 **What's New in This Enhanced Version:**")
    print("• 🔍 Automatic web search for current information")
    print("• 🤖 Smart detection of when search is needed")
    print("• � Integration of search results into responses")
    print("• 🧠 Chain of Thought reasoning with real-time data")
    
    print("\n�💡 **Usage Tips:**")
    print("• Ask about current events, latest news, or recent developments")
    print("• Try: 'What are the latest AI breakthroughs?'")
    print("• Try: 'Current trends in renewable energy'")
    print("• Try: 'Recent news about space exploration'")
    print("• Type 'nosearch <question>' to disable web search for a specific question")
    print("• Type 'quit', 'exit', or 'bye' to end the conversation")
    
    print("\n🔍 **Search Examples:**")
    print("• Questions about 2025 developments will trigger web search")
    print("• General knowledge questions won't need search")
    print("• Math problems will use reasoning without search")
    
    print("\n🚀 Ready to chat! Ask me anything...")
    print("(Try asking about something current to see web search in action)")
    print("-" * 80)
    
    # Start interactive chat
    agent.interactive_chat()

if __name__ == "__main__":
    main()
