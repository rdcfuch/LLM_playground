# Gemini Chain of Thought (COT) Agent with Web Search

A powerful AI agent built with Google's Gemini API and Jina AI's Search API that uses Chain of Thought reasoning and web search to provide thoughtful, step-by-step responses with access to current information.

## Features

- **Chain of Thought Reasoning**: The agent thinks through problems step by step before providing answers
- **🔍 Web Search Integration**: Automatically searches the web for current information when needed
- **🤖 Smart Search Detection**: Intelligently determines when web search is required
- **📊 Search Results Integration**: Seamlessly incorporates web search results into responses
- **Clear Response Structure**: Separates thinking process from final answers
- **Multiple Usage Modes**: Interactive chat, single questions, batch processing
- **Configurable Parameters**: Temperature, max tokens, model selection, and search enable/disable
- **Error Handling**: Robust error handling with meaningful error messages

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up API keys:
   - **Gemini API**: Currently set to `AIzaSyDTa2e6FIBjh56icX-umgw3vHn3AuYeoeo`
   - **Jina API** (for web search): Get your free key from [https://jina.ai/?sui=apikey](https://jina.ai/?sui=apikey)

3. Set the Jina API key (optional, for web search):
```bash
export JINA_API_KEY='your-jina-api-key'
```

## Usage

### Quick Start

```python
from agent_function import GeminiCOTAgent, quick_ask

# Method 1: Quick ask function (with web search if key is available)
response = quick_ask("What are the latest developments in AI?")
print(response)

# Method 2: Using the full agent
agent = GeminiCOTAgent(jina_api_key='your-jina-key')  # Optional
result = agent.think_and_respond("Explain quantum computing")
print("Thinking:", result["thinking"])
print("Answer:", result["answer"])
print("Search Used:", result["search_info"]["used_search"])
```

### Web Search Examples

```python
from agent_function import GeminiCOTAgent

agent = GeminiCOTAgent(jina_api_key='your-jina-key')

# Questions that benefit from web search
current_info_questions = [
    "What are the latest AI breakthroughs in 2025?",
    "What's happening in the stock market today?",
    "Recent developments in quantum computing"
]

# Questions that don't need web search
general_questions = [
    "How does photosynthesis work?",
    "What is machine learning?",
    "Explain the water cycle"
]

# The agent automatically determines when to search
for question in current_info_questions:
    response = agent.think_and_respond(question)
    if response['search_info']['used_search']:
        print(f"🔍 Searched for: {response['search_info']['query']}")
```

### Interactive Chat Mode

```python
from agent_function import GeminiCOTAgent

agent = GeminiCOTAgent(jina_api_key='your-jina-key')
agent.interactive_chat()  # Starts an interactive session with search

# Special commands in chat:
# - "nosearch <question>" - Disable search for specific question
# - "quit" - Exit chat
```

### Controlling Web Search

```python
# Disable web search for specific questions
response = agent.think_and_respond(
    "What is the capital of France?", 
    enable_search=False  # Force disable search
)

# Enable search even for general questions
response = agent.think_and_respond(
    "What is AI?", 
    enable_search=True  # Allow search if agent thinks it's helpful
)
```

## Response Format

The enhanced agent returns responses with search information:

```python
{
    "thinking": "Step-by-step reasoning process...",
    "answer": "Final answer to the question...",
    "full_response": "Complete formatted response...",
    "timestamp": "2025-09-15 20:30:38",
    "search_info": {
        "used_search": True,
        "query": "latest AI developments 2025",
        "results": [
            {
                "title": "Article title",
                "url": "https://example.com",
                "content": "Article content..."
            }
        ]
    }
}
```

## Configuration

### Initialize with API Keys

```python
agent = GeminiCOTAgent(
    gemini_api_key="your-gemini-key",
    jina_api_key="your-jina-key",  # Optional
    model_name="gemini-1.5-flash"
)
```

### Adjust Response Parameters

```python
response = agent.think_and_respond(
    "Your question here",
    temperature=0.3,    # Lower for more focused responses
    max_tokens=1500,    # Adjust response length
    enable_search=True  # Enable/disable web search
)
```

## Web Search Features

### Automatic Search Detection
The agent automatically determines when web search would be helpful:
- ✅ **Triggers search for**: Current events, recent information, real-time data
- ❌ **Skips search for**: General knowledge, math problems, basic concepts

### Search Query Generation
- Intelligently generates relevant search queries
- Optimizes queries for better search results
- Handles complex multi-part questions

### Results Integration
- Incorporates top search results into reasoning
- Maintains source attribution
- Balances search results with existing knowledge

## Examples

### Example 1: Current Information (With Search)
```python
question = "What are the latest developments in electric vehicles in 2025?"
response = agent.think_and_respond(question)
# Agent will search for current EV news and developments
```

### Example 2: General Knowledge (No Search)
```python
question = "How does photosynthesis work?"
response = agent.think_and_respond(question)
# Agent uses existing knowledge, no search needed
```

### Example 3: Mathematical Problem (No Search)
```python
question = "If I invest $1000 at 5% interest, how much will I have in 10 years?"
response = agent.think_and_respond(question)
# Agent solves using mathematical reasoning
```

## Files

- `agent_function.py` - Main COT agent implementation with web search
- `demo_cot_agent.py` - Original demo script
- `demo_web_search.py` - New demo showcasing web search features
- `interactive_chat.py` - Simple interactive chat script
- `requirements.txt` - Required Python packages
- `README.md` - This documentation

## Running the Demos

```bash
# Original COT demo
python demo_cot_agent.py

# Web search features demo
python demo_web_search.py

# Interactive chat
python interactive_chat.py
```

## API Key Setup

### Jina AI API Key (Free)
1. Visit [https://jina.ai/?sui=apikey](https://jina.ai/?sui=apikey)
2. Sign up for a free account
3. Copy your API key
4. Set environment variable:
   ```bash
   export JINA_API_KEY='your-api-key'
   ```

### Environment Variable Method
```bash
# Set in your shell profile (.bashrc, .zshrc, etc.)
export JINA_API_KEY='your-jina-api-key'
export GEMINI_API_KEY='your-gemini-api-key'  # Optional
```

### Direct Configuration Method
```python
agent = GeminiCOTAgent(
    gemini_api_key='your-gemini-key',
    jina_api_key='your-jina-key'
)
```

## Web Search API Details

The agent uses Jina AI's Search API which provides:
- High-quality search results optimized for LLMs
- Markdown-formatted content
- Source attribution
- Rate limiting: 40 RPM (free), 400 RPM (premium)

## Model Options

The agent supports various Gemini models:
- `gemini-1.5-flash` (default) - Fast responses
- `gemini-1.5-pro` - More detailed reasoning  
- `gemini-1.0-pro` - Stable version

## Error Handling

The enhanced agent includes comprehensive error handling for:
- API connection errors
- Invalid API keys
- Rate limiting
- Search failures
- Malformed responses

## Troubleshooting

### Web Search Not Working
1. Check if `JINA_API_KEY` is set: `echo $JINA_API_KEY`
2. Verify your API key is valid
3. Check rate limits (40 requests per minute for free tier)
4. Ensure internet connectivity

### Search Not Triggered
- The agent intelligently decides when search is needed
- Use `enable_search=True` to allow search for any question
- Use current events or recent information questions to trigger search

## Contributing

Feel free to extend the agent with additional features:
- Custom search engines
- Result caching
- Advanced search filters
- Multiple search sources

## License

This project is for educational and research purposes.
