from typing import Optional, Dict, Any, List, Callable
import logging
from pydantic_ai import Agent, RunContext
from .models import DynamicModel

logger = logging.getLogger(__name__)

class DynamicAgent(Agent):
    SUPPORTED_TOOL_TYPES = ["tool_plain", "tool"]

    def __init__(self, model_type: str, system_prompt: str, result_type: Any = None, deps_type: Any = Dict[str, Any]):
        self.model_manager = DynamicModel(model_type)
        self.chat_history: List[Dict[str, str]] = []
        model = self.model_manager.get_model()
        super().__init__(
            model=model,
            deps_type=deps_type,
            system_prompt=system_prompt,
            result_type=result_type
        )
        logger.info(f"Initialized agent with model: {model}")

    def update_system_prompt(self, new_system_prompt: str) -> None:
        """Update the system prompt and recreate the agent with the new prompt.

        Args:
            new_system_prompt (str): The new system prompt to use for the agent.
        """
        self.system_prompt = new_system_prompt
        logger.info(f"Updated system prompt")

    def add_tool(self, func: Callable, tool_type: str = "tool_plain") -> None:
        if tool_type not in self.SUPPORTED_TOOL_TYPES:
            raise ValueError(f"Unsupported tool type: {tool_type}. Valid options: {self.SUPPORTED_TOOL_TYPES}")
        
        if tool_type == "tool_plain":
            self.tool_plain(func)
        else:
            self.tool(func)
        logger.info(f"Added tool: {func.__name__} ({tool_type})")

    def interact_with_model(self, user_input: str, deps: Any = None) -> str:
        self.chat_history.append({"role": "user", "content": user_input})
        if deps is None:
            deps = {}
        # Check if deps is a dictionary or an object with chat_history attribute
        if isinstance(deps, dict):
            deps["chat_history"] = self.chat_history.copy()
        else:
            # Set the chat_history attribute on the deps object
            deps.chat_history = self.chat_history.copy()
        
        result = self.run_sync(user_input, deps=deps)
        self.chat_history.append({"role": "assistant", "content": result.data})
        return result.data

    def get_chat_history(self) -> List[Dict[str, str]]:
        return self.chat_history.copy()

    def clear_chat_history(self) -> None:
        self.chat_history.clear()
        logger.info("Chat history cleared")