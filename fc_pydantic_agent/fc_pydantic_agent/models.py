import os
import logging
from dotenv import load_dotenv
from typing import Optional
from pydantic_ai.models.openai import OpenAIModel

logger = logging.getLogger(__name__)

class DynamicModel:
    SUPPORTED_MODELS = ["gpt-4o-mini", "kimi", "deepseek", "ollama"]

    def __init__(self, model_type: str):
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.kimi_api_key = os.getenv("KIMI_API_KEY")
        self.kimi_model = os.getenv("KIMI_MODEL")
        self.kimi_base_url = os.getenv("KIMI_BASE_URL")
        self.deepseek_api_key = os.getenv("DeepSeek_API_KEY")
        self.deepseek_model = os.getenv("DeepSeek_MODEL")
        self.deepseek_base_url = os.getenv("DeepSeek_BASE_URL")
        self.ollama_api_key = os.getenv("OLLAMA_API_KEY")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "deepseek-r1:14b")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL")
        
        self.model: Optional[OpenAIModel] = None
        self.create_model(model_type)

    def create_model(self, model_type: str) -> None:
        model_type = model_type.lower()
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model type: {model_type}. Supported: {self.SUPPORTED_MODELS}")
        
        if model_type == "gpt-4o-mini":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in .env file.")
            self.model = OpenAIModel(
                model_name="gpt-4o-mini",
                api_key=self.openai_api_key,
                base_url="https://api.openai.com/v1",
            )
        elif model_type == "kimi":
            if not all([self.kimi_api_key, self.kimi_model, self.kimi_base_url]):
                raise ValueError("Missing Kimi API credentials in .env file.")
            self.model = OpenAIModel(
                model_name=self.kimi_model,
                api_key=self.kimi_api_key,
                base_url=self.kimi_base_url,
            )
        elif model_type == "deepseek":
            if not all([self.deepseek_api_key, self.deepseek_model, self.deepseek_base_url]):
                raise ValueError("Missing DeepSeek API credentials in .env file.")
            self.model = OpenAIModel(
                model_name=self.deepseek_model,
                api_key=self.deepseek_api_key,
                base_url=self.deepseek_base_url,
            )
        elif model_type == "ollama":
            if not all([self.ollama_api_key, self.ollama_model, self.ollama_base_url]):
                raise ValueError("Missing Ollama API credentials in .env file.")
            self.model = OpenAIModel(
                model_name=self.ollama_model,
                api_key=self.ollama_api_key,
                base_url=self.ollama_base_url,
            )
        logger.info(f"Created {model_type} model: {self.model}")

    def get_model(self) -> OpenAIModel:
        if not self.model:
            raise ValueError("No model created. Call create_model first.")
        return self.model