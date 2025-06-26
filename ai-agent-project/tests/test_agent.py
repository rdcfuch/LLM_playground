import pytest
from src.agent.core import AIAgent, AgentConfig

@pytest.fixture
def ai_agent():
    # Create a test configuration
    config = AgentConfig(
        llm_model="openai",
        mcp_server_url="http://localhost:5000",
        timeout=30
    )
    return AIAgent(config)

def test_agent_initialization(ai_agent):
    assert ai_agent is not None
    assert isinstance(ai_agent, AIAgent)
    assert ai_agent.config.llm_model == "openai"
    assert ai_agent.config.mcp_server_url == "http://localhost:5000"

def test_agent_process_request(ai_agent):
    request_data = {"message": "Hello, AI!", "user_id": "test_user"}
    response = ai_agent.process_request(request_data)
    assert response is not None
    assert isinstance(response, dict)
    assert "status" in response
    assert "data" in response

def test_agent_configuration(ai_agent):
    config = ai_agent.config
    assert config is not None
    assert hasattr(config, 'llm_model')
    assert hasattr(config, 'mcp_server_url')
    assert config.llm_model == "openai"

def test_agent_set_config(ai_agent):
    new_config = AgentConfig(
        llm_model="ollama",
        mcp_server_url="http://localhost:8000",
        timeout=60
    )
    ai_agent.set_config(new_config)
    assert ai_agent.config.llm_model == "ollama"
    assert ai_agent.config.mcp_server_url == "http://localhost:8000"
    assert ai_agent.config.timeout == 60