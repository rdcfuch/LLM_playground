import pytest
from unittest.mock import patch, MagicMock
from src.llm.openai_client import OpenAIClient
from src.llm.ollama_client import OllamaClient
from src.llm.lmstudio_client import LMStudioClient

@pytest.fixture
def openai_client():
    return OpenAIClient(api_key="test_api_key", model="gpt-3.5-turbo")

@pytest.fixture
def ollama_client():
    return OllamaClient(base_url="http://localhost:11434")

@pytest.fixture
def lmstudio_client():
    return LMStudioClient(base_url="http://localhost:1234", api_key="test_api_key")

def test_openai_client_initialization(openai_client):
    assert openai_client is not None
    assert openai_client.api_key == "test_api_key"
    assert openai_client.model_name == "gpt-3.5-turbo"

def test_ollama_client_initialization(ollama_client):
    assert ollama_client is not None
    assert ollama_client.base_url == "http://localhost:11434"
    assert ollama_client.model_name == "ollama"

def test_lmstudio_client_initialization(lmstudio_client):
    assert lmstudio_client is not None
    assert lmstudio_client.api_key == "test_api_key"
    assert lmstudio_client.base_url == "http://localhost:1234"

@patch('src.llm.openai_client.requests.post')
def test_openai_client_response(mock_post, openai_client):
    # Mock the API response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello! How can I help you?"}}]
    }
    mock_post.return_value = mock_response
    
    response = openai_client.generate_response("Hello, world!")
    assert isinstance(response, str)
    assert response == "Hello! How can I help you?"

@patch('src.llm.ollama_client.requests.post')
def test_ollama_client_response(mock_post, ollama_client):
    # Mock the API response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"generated_text": "Hello from Ollama!"}
    mock_post.return_value = mock_response
    
    response = ollama_client.generate_response("Hello, world!")
    assert isinstance(response, str)
    assert response == "Hello from Ollama!"

@patch('src.llm.lmstudio_client.requests.post')
def test_lmstudio_client_response(mock_post, lmstudio_client):
    # Mock the API response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"generated_text": "Hello from LM Studio!"}
    mock_post.return_value = mock_response
    
    response = lmstudio_client.generate_response("Hello, world!")
    assert isinstance(response, str)
    assert response == "Hello from LM Studio!"