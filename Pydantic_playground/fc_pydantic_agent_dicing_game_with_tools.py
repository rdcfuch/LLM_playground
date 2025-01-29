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


class DynamicModel:
    """
    A class to dynamically create and manage models using API keys, model names, and base URLs.
    Supports GPT-4, Kimi (Moonshot), DeepSeek, and Ollama models.
    """

    SUPPORTED_MODELS = ["gpt-4o-mini", "kimi", "deepseek", "ollama"]

    def __init__(self, model_type: str):
        """
        Initialize the DynamicModel class. Load environment variables from .env file and create the specified model.

        Args:
            model_type (str): The type of model to create. Supported values: "gpt-4o-mini", "kimi", "deepseek", "ollama".
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
        self.ollama_api_key: Optional[str] = os.getenv("OLLAMA_API_KEY")
        self.ollama_api_key: Optional[str] = os.getenv("OLLAMA_API_KEY")
        self.ollama_model: Optional[str] = os.getenv("OLLAMA_MODEL", "deepseek-r1:14b")  # Default to "deepseek-r1:14b"
        self.ollama_base_url: Optional[str] = os.getenv("OLLAMA_BASE_URL")

        self.create_model(model_type)

    def create_model(self, model_type: str) -> None:
        """
        Dynamically create a model based on the specified model type.

        Args:
            model_type (str): The type of model to create. Supported values: "gpt-4o-mini", "kimi", "deepseek", "ollama".

        Raises:
            ValueError: If the model type is not supported or required environment variables are missing.
        """
        if model_type.lower() not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model type: {model_type}. Supported models are: {self.SUPPORTED_MODELS}")

        if model_type.lower() == "gpt-4o-mini":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in .env file.")
            self.model = OpenAIModel(
                model_name="gpt-4o-mini",
                api_key=self.openai_api_key,
                base_url="https://api.openai.com/v1",  # Default OpenAI API URL
            )
            logger.info(f"Created GPT-4 model: {self.model}")

        elif model_type.lower() == "kimi":
            if not self.kimi_api_key or not self.kimi_model or not self.kimi_base_url:
                raise ValueError("KIMI_API_KEY, KIMI_MODEL, or KIMI_BASE_URL not found in .env file.")
            self.model = OpenAIModel(
                model_name=self.kimi_model,
                api_key=self.kimi_api_key,
                base_url=self.kimi_base_url,
            )
            logger.info(f"Created Kimi model: {self.model}")

        elif model_type.lower() == "deepseek":
            if not self.deepseek_api_key or not self.deepseek_model or not self.deepseek_base_url:
                raise ValueError("DeepSeek_API_KEY, DeepSeek_MODEL, or DeepSeek_BASE_URL not found in .env file.")
            self.model = OpenAIModel(
                model_name=self.deepseek_model,
                api_key=self.deepseek_api_key,
                base_url=self.deepseek_base_url,
            )
            logger.info(f"Created DeepSeek model: {self.model}")


        elif model_type.lower() == "ollama":

            if not self.ollama_api_key or not self.ollama_model or not self.ollama_base_url:
                raise ValueError("OLLAMA_API_KEY, OLLAMA_MODEL, or OLLAMA_BASE_URL not found in .env file.")

            self.model = OpenAIModel(

                model_name=self.ollama_model,

                api_key=self.ollama_api_key,

                base_url=self.ollama_base_url,

            )

            logger.info(f"Created Ollama model: {self.model}")

    def get_model(self) -> OpenAIModel:
        """
        Get the created model instance.

        Returns:
            OpenAIModel: The created model instance.

        Raises:
            ValueError: If no model has been created.
        """
        if not self.model:
            raise ValueError("No model has been created. Call `create_model` first.")
        return self.model


class DynamicAgent:
    """
    A class to dynamically create and manage agents using the DynamicModel class.
    Includes memory for chat history.
    """

    SUPPORTED_TOOL_TYPES = ["tool_plain", "tool"]

    def __init__(self, model_type: str, system_prompt: str):
        """
        Initialize the DynamicAgent class. Create a model using DynamicModel and set up the agent.

        Args:
            model_type (str): The type of model to create. Supported values: "gpt-4o-mini", "kimi", "deepseek", "ollama".
            system_prompt (str): The system prompt to use for the agent.
        """
        self.model_manager = DynamicModel(model_type)
        self.agent: Optional[Agent] = None
        self.chat_history: List[Dict[str, str]] = []  # Store chat history

        self.create_agent(system_prompt)

    def create_agent(self, system_prompt: str) -> None:
        """
        Create an agent using the model created by DynamicModel.

        Args:
            system_prompt (str): The system prompt to use for the agent.
        """
        model = self.model_manager.get_model()
        self.agent = Agent(
            model=model,
            deps_type=Dict[str, Any],  # Change deps type to Dict[str, Any]
            system_prompt=system_prompt,
        )
        logger.info(f"Created agent with model: {model}")

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
            raise ValueError(
                f"Unsupported tool type: {tool_type}. Supported tool types are: {self.SUPPORTED_TOOL_TYPES}")

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


if __name__ == "__main__":
    # Define the system prompt
    system_prompt = (
        "You're a dice game, you should roll the die and see if the number "
        "you get back matches the user's guess. If so, tell them they're a winner. "
        "Use the player's name in the response."
    )

    # Create a DynamicAgent instance with the specified model type and system prompt
    model_manager = DynamicAgent("ollama", system_prompt)


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
