# AI Agent Project

## Overview
This project implements an AI agent that utilizes various large language models (LLMs) through a configurable architecture. The agent can interact with different LLMs such as OpenAI, Ollama, and LM Studio, and is designed to handle requests via a RESTful API.

## Features
- Configurable LLM model selection
- MCP server for managing communication
- RESTful API for handling requests
- Pydantic models for data validation and serialization

## Project Structure
```
ai-agent-project
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── agent
│   │   ├── __init__.py
│   │   ├── core.py
│   │   └── models.py
│   ├── llm
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── openai_client.py
│   │   ├── ollama_client.py
│   │   └── lmstudio_client.py
│   ├── mcp
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── client.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   └── config
│       ├── __init__.py
│       └── settings.py
├── config
│   ├── config.yaml
│   └── mcp_config.yaml
├── tests
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_llm.py
│   └── test_api.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd ai-agent-project
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
Configuration settings for the application can be found in the `config/config.yaml` and `config/mcp_config.yaml` files. Modify these files to suit your environment and requirements.

## Usage
To start the server, run the following command:
```
python src/main.py
```

The server will start and listen for incoming requests. You can interact with the AI agent through the defined RESTful API endpoints.

## Testing
To run the tests, use the following command:
```
pytest tests/
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.