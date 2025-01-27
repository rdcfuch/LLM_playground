import os
import requests
import random  # 导入 random 模块
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

# 其余代码保持不变


class DynamicAgent:
    """
    A class to dynamically create and manage models using API keys, model names, and base URLs.
    Supports GPT-4, Kimi (Moonshot), and DeepSeek models.
    """

    def __init__(self, model_type: str, system_prompt: str):
        """
        Initialize the DynamicAgent class. Load environment variables from .env file and create the specified model.

        Args:
            model_type (str): The type of model to create. Supported values: "gpt-4o-mini", "kimi", "deepseek".
            system_prompt (str): The system prompt to use for the agent.
        """
        load_dotenv()  # Load environment variables from .env file
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.kimi_api_key: Optional[str] = os.getenv("KIMI_API_KEY")
        self.kimi_model: Optional[str] = os.getenv("KIMI_MODEL")
        self.kimi_base_url: Optional[str] = os.getenv("KIMI_BASE_URL")
        self.deepseek_api_key: Optional[str] = os.getenv("DeepSeek_API_KEY")
        self.deepseek_model: Optional[str] = os.getenv("DeepSeek_MODEL")
        self.deepseek_base_url: Optional[str] = os.getenv("DeepSeek_BASE_URL")
        self.model_name: Optional[str] = None
        self.model_url: Optional[str] = None
        self.api_key: Optional[str] = None
        self.agent: Optional[Agent] = None

        self.create_model(model_type, system_prompt)

    def create_model(self, model_type: str, system_prompt: str) -> None:
        """
        Dynamically create a model based on the specified model type.

        Args:
            model_type (str): The type of model to create. Supported values: "gpt-4o-mini", "kimi", "deepseek".
            system_prompt (str): The system prompt to use for the agent.

        Raises:
            ValueError: If the model type is not supported or required environment variables are missing.
        """
        if model_type.lower() == "gpt-4o-mini":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in .env file.")
            self.model_name = "gpt-4o-mini"
            self.model_url = "https://api.openai.com/v1"  # Default OpenAI API URL
            self.api_key = self.openai_api_key
            self.agent = Agent(
                model=OpenAIModel(model_name=self.model_name, api_key=self.api_key),
                deps_type=str,
                system_prompt=system_prompt,
            )
            print(f"Created {self.model_name} model with URL: {self.model_url}")

        elif model_type.lower() == "kimi":
            if not self.kimi_api_key or not self.kimi_model or not self.kimi_base_url:
                raise ValueError("KIMI_API_KEY, KIMI_MODEL, or KIMI_BASE_URL not found in .env file.")
            self.model_name = self.kimi_model
            self.model_url = self.kimi_base_url
            self.api_key = self.kimi_api_key
            self.agent = Agent(
                model=OpenAIModel(model_name=self.model_name, api_key=self.api_key),
                deps_type=str,
                system_prompt=system_prompt,
            )
            print(f"Created {self.model_name} model with URL: {self.model_url}")

        elif model_type.lower() == "deepseek":
            if not self.deepseek_api_key or not self.deepseek_model or not self.deepseek_base_url:
                raise ValueError("DeepSeek_API_KEY, DeepSeek_MODEL, or DeepSeek_BASE_URL not found in .env file.")
            self.model_name = self.deepseek_model
            self.model_url = self.deepseek_base_url
            self.api_key = self.deepseek_api_key
            self.agent = Agent(
                model=OpenAIModel(model_name=self.model_name, api_key=self.api_key),
                deps_type=str,
                system_prompt=system_prompt,
            )
            print(f"Created {self.model_name} model with URL: {self.model_url}")

        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def interact_with_model(self, user_input: str, deps: str = None) -> str:
        """
        Interact with the selected model by sending a request to its API.

        Args:
            user_input (str): The input provided by the user.

        Returns:
            str: The response from the model.

        Raises:
            ValueError: If no model has been created.
        """
        if not self.agent:
            raise ValueError("No model has been created. Call `create_model` first.")

        result = self.agent.run_sync(user_input)
        return result.data

    def get_api_key(self) -> Optional[str]:
        """
        Get the API key for the currently created model.

        Returns:
            Optional[str]: The API key, or None if no model has been created.
        """
        return self.api_key

    def get_model_name(self) -> Optional[str]:
        """
        Get the name of the currently created model.

        Returns:
            Optional[str]: The model name, or None if no model has been created.
        """
        return self.model_name

    def get_model_url(self) -> Optional[str]:
        """
        Get the URL of the currently created model.

        Returns:
            Optional[str]: The model URL, or None if no model has been created.
        """
        return self.model_url


if __name__ == "__main__":
    # Define the system prompt
    system_prompt = (
        "You're a dice game, you should roll the die and see if the number "
        "you get back matches the user's guess. If so, tell them they're a winner. "
        "Use the player's name in the response."
    )

    # Create a DynamicAgent instance with the specified model type and system prompt
    model_manager = DynamicAgent("gpt-4o-mini", system_prompt)
    @model_manager.agent.tool_plain
    def roll_die() -> str:
        """Roll a six-sided die and return the result."""
        return str(random.randint(1, 6))

    @model_manager.agent.tool
    def get_player_name(ctx: RunContext[str]) -> str:
        """Get the player's name."""
        return ctx.deps
    # Interact with the model
    user_input = "Hello, how are you?"
    try:
        response = model_manager.interact_with_model('My guess is 4', deps='Anne')
        print(response)  # Example output: "I'm just a computer program, so I don't have feelings, but thanks for asking!"
    except ValueError as e:
        print(f"Error: {e}")
