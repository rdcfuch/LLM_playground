# Pydantic Dicing Game

A configurable dice game implementation using pydantic-ai agents with support for multiple LLM providers.

## Features

- Multi-model support (OpenAI, Kimi, DeepSeek, Ollama)
- Configurable through environment variables
- Chat history management
- Tool system for game mechanics
- Easy integration with different LLM providers

## Installation

```bash
pip install -e .
```

## Usage

```python
from pydantic_dicing_game import DynamicAgent

# Initialize agent with Ollama
agent = DynamicAgent(
    model_type="ollama",
    system_prompt="You're a dice game assistant"
)

# Add custom game tools
def roll_die():
    return str(random.randint(1, 6))
    
agent.add_tool(roll_die)
```

## Configuration

Create a `.env` file with your API credentials:
```ini
OPENAI_API_KEY=your-openai-key
KIMI_API_KEY=your-kimi-key
OLLAMA_BASE_URL=http://localhost:11434/v1
```

See `examples/dice_game_example.py` for a complete implementation.