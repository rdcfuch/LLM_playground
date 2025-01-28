import os
import random
import logging
from dotenv import load_dotenv
from typing import Optional, Callable, List, Dict, Any
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class DynamicAgent:
    """
    A class to dynamically create and manage models using API keys, model names, and base URLs.
    Supports GPT-4, Kimi (Moonshot), and DeepSeek models. Includes memory for chat history.
    """

    SUPPORTED_MODELS = ["gpt-4o-mini", "kimi", "deepseek"]
    SUPPORTED_TOOL_TYPES = ["tool_plain", "tool"]

    def __init__(self, model_type: str, system_prompt: str):
        """
        Initialize the DynamicAgent class. Load environment variables from .env file and create the specified model.

        Args:
            model_type (str): The type of model to create. Supported values: "gpt-4o-mini", "kimi", "deepseek".
            system_prompt (str): The system prompt to use for the agent.
        """
        # Get the project root directory (one level up from this script)
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Load .env from the project root directory
        load_dotenv(os.path.join(PROJECT_ROOT, '.env'))  # Load environment variables from .env file
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
        self.chat_history: List[Dict[str, str]] = []  # Store chat history

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
        if model_type.lower() not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model type: {model_type}. Supported models are: {self.SUPPORTED_MODELS}")

        if model_type.lower() == "gpt-4o-mini":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in .env file.")
            self.model_name = "gpt-4o-mini"
            self.model_url = "https://api.openai.com/v1"  # Default OpenAI API URL
            self.api_key = self.openai_api_key
            self.agent = Agent(
                model=OpenAIModel(model_name=self.model_name, api_key=self.api_key),
                deps_type=Dict[str, Any],  # Change deps type to Dict[str, Any]
                system_prompt=system_prompt,
            )
            logger.info(f"Created {self.model_name} model with URL: {self.model_url}")

        elif model_type.lower() == "kimi":
            if not self.kimi_api_key or not self.kimi_model or not self.kimi_base_url:
                raise ValueError("KIMI_API_KEY, KIMI_MODEL, or KIMI_BASE_URL not found in .env file.")
            self.model_name = self.kimi_model
            self.model_url = self.kimi_base_url
            self.api_key = self.kimi_api_key
            self.agent = Agent(
                model=OpenAIModel(model_name=self.model_name, api_key=self.api_key),
                deps_type=Dict[str, Any],  # Change deps type to Dict[str, Any]
                system_prompt=system_prompt,
            )
            # logger.info(f"Created {self.model_name} model with URL: {self.model_url}")

        elif model_type.lower() == "deepseek":
            if not self.deepseek_api_key or not self.deepseek_model or not self.deepseek_base_url:
                raise ValueError("DeepSeek_API_KEY, DeepSeek_MODEL, or DeepSeek_BASE_URL not found in .env file.")
            self.model_name = self.deepseek_model
            self.model_url = self.deepseek_base_url
            self.api_key = self.deepseek_api_key
            self.agent = Agent(
                model=OpenAIModel(model_name=self.model_name, api_key=self.api_key),
                deps_type=Dict[str, Any],  # Change deps type to Dict[str, Any]
                system_prompt=system_prompt,
            )
            logger.info(f"Created {self.model_name} model with URL: {self.model_url}")

    def add_tool(self, func: Callable, tool_type: str = "tool_plain") -> None:
        """
        Add a tool to the agent.

        Args:
            func (Callable): The function to be added as a tool.
            tool_type (str): The type of tool to add. Supported values: "tool_plain", "tool".

        Raises:
            ValueError: If the tool type is not supported.
        """
        if tool_type not in self.SUPPORTED_TOOL_TYPES:
            raise ValueError(f"Unsupported tool type: {tool_type}. Supported tool types are: {self.SUPPORTED_TOOL_TYPES}")

        if tool_type == "tool_plain":
            self.agent.tool_plain(func)
        elif tool_type == "tool":
            self.agent.tool(func)

    def interact_with_model(self, user_input: str, deps: Dict[str, Any] = None) -> str:
        """
        Interact with the selected model by sending a request to its API.
        Maintains chat history for context.

        Args:
            user_input (str): The input provided by the user.
            deps (Dict[str, Any]): Optional dependencies to pass to the model, including chat history.

        Returns:
            str: The response from the model.

        Raises:
            ValueError: If no model has been created.
        """
        if not self.agent:
            raise ValueError("No model has been created. Call `create_model` first.")

        # Add user input to chat history
        self.chat_history.append({"role": "user", "content": user_input})

        # Prepare deps with chat history
        if deps is None:
            deps = {}
        deps["chat_history"] = self.chat_history

        # Pass deps (including chat history) to the agent
        result = self.agent.run_sync(user_input, deps=deps)

        # Add model response to chat history
        self.chat_history.append({"role": "assistant", "content": result.data})

        return result.data

    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get the chat history for the current instance.

        Returns:
            List[Dict[str, str]]: The chat history, where each entry is a dictionary with "role" and "content".
        """
        return self.chat_history

    def clear_chat_history(self) -> None:
        """
        Clear the chat history for the current instance.
        """
        self.chat_history = []

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

    # Define tools
    def roll_die() -> str:
        """Roll a six-sided die and return the result."""
        return str(random.randint(1, 6))

    def get_player_name(ctx: RunContext[Dict[str, Any]]) -> str:
        """Get the player's name."""
        return ctx.deps.get("player_name", "Unknown Player")

    def get_current_time() -> str:
        """Get the current time."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_user_guess(ctx: RunContext[Dict[str, Any]]) -> str:
        """Get the user's guess."""
        return ctx.deps.get("user_guess", "No guess provided")

    # Add tools to the agent
    model_manager.add_tool(roll_die, "tool_plain")
    model_manager.add_tool(get_player_name, "tool")
    model_manager.add_tool(get_current_time, "tool_plain")
    model_manager.add_tool(get_user_guess, "tool")

    # Interact with the model

    # Prepare deps with additional context

    try:
        while True:
            user_input = input("Let's play a game! Guess a number between 1 and 6 (or type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break

            deps = {
                "player_name": "FC",
                "user_guess": user_input,
            }
            
            response = model_manager.interact_with_model(user_input, deps=deps)
            print(response)

            # Optionally print chat history
            print("\nChat History:")
            for message in model_manager.get_chat_history():
                print(f"{message['role'].capitalize()}: {message['content']}")
            print("\n")
    except ValueError as e:
        logger.error(f"Error: {e}")
