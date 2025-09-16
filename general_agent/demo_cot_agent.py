#!/usr/bin/env python3
"""
Demo script for the Gemini Chain of Thought Agent
Shows different ways to use the COT agent
"""

from agent_function import GeminiCOTAgent, quick_ask
import time

def demo_single_question():
    """Demo: Single question with detailed COT response"""
    print("="*60)
    print("🎯 DEMO: Single Question with Chain of Thought")
    print("="*60)
    
    agent = GeminiCOTAgent()
    
    question = "How do solar panels work and why are they becoming more popular?"
    print(f"Question: {question}\n")
    
    response = agent.think_and_respond(question)
    
    print("🤔 **Thinking Process:**")
    print(response["thinking"])
    print("\n📝 **Final Answer:**")
    print(response["answer"])
    print("\n" + "="*60)

def demo_quick_ask():
    """Demo: Quick ask function for simple queries"""
    print("\n🚀 DEMO: Quick Ask Function")
    print("="*60)
    
    question = "What's the difference between AI and machine learning?"
    print(f"Question: {question}\n")
    
    response = quick_ask(question)
    print(response)
    print("\n" + "="*60)

def demo_batch_processing():
    """Demo: Batch processing multiple questions"""
    print("\n📦 DEMO: Batch Processing")
    print("="*60)
    
    agent = GeminiCOTAgent()
    
    questions = [
        "Why is the sky blue?",
        "What is quantum computing?",
        "How does photosynthesis work?"
    ]
    
    responses = agent.batch_questions(questions)
    
    for i, response in enumerate(responses, 1):
        print(f"\n📋 Question {i}: {response['question']}")
        print(f"⏰ Timestamp: {response['timestamp']}")
        print("\n🤔 Thinking:")
        print(response['thinking'][:200] + "..." if len(response['thinking']) > 200 else response['thinking'])
        print("\n📝 Answer:")
        print(response['answer'][:200] + "..." if len(response['answer']) > 200 else response['answer'])
        print("-" * 40)
    
    print("="*60)

def demo_interactive_chat():
    """Demo: Interactive chat mode"""
    print("\n💬 DEMO: Interactive Chat Mode")
    print("="*60)
    print("Starting interactive chat session...")
    print("Note: This will start an interactive session. Type 'quit' to exit.")
    
    # Uncomment the next two lines to actually start interactive mode
    # agent = GeminiCOTAgent()
    # agent.interactive_chat()
    
    print("Interactive chat demo skipped. Uncomment the lines in the function to enable.")
    print("="*60)

def main():
    """Run all demos"""
    print("🤖 Gemini Chain of Thought Agent Demonstration")
    print("This demo shows various ways to use the COT agent\n")
    
    try:
        # Demo 1: Single question
        demo_single_question()
        time.sleep(2)
        
        # Demo 2: Quick ask
        demo_quick_ask()
        time.sleep(2)
        
        # Demo 3: Batch processing
        demo_batch_processing()
        time.sleep(2)
        
        # Demo 4: Interactive chat info
        demo_interactive_chat()
        
        print("\n✅ All demos completed successfully!")
        print("\n📝 **Usage Summary:**")
        print("1. GeminiCOTAgent() - Full-featured agent with COT reasoning")
        print("2. quick_ask() - Simple function for quick questions")
        print("3. agent.think_and_respond() - Single question with detailed response")
        print("4. agent.batch_questions() - Process multiple questions")
        print("5. agent.interactive_chat() - Start interactive chat session")
        
    except Exception as e:
        print(f"❌ Error during demo: {str(e)}")
        print("Make sure you have the correct API key and internet connection.")

if __name__ == "__main__":
    main()
