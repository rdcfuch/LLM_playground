from typing import Optional, Dict, Any, List, Callable
import logging
from pydantic_ai import Agent, RunContext
from .models import DynamicModel

logger = logging.getLogger(__name__)

class DynamicAgent:
    SUPPORTED_TOOL_TYPES = ["tool_plain", "tool"]

    def __init__(self, model_type: str, system_prompt: str, result_type: Any = None, deps_type: Any = Dict[str, Any]):
        self.model_manager = DynamicModel(model_type)
        self.agent: Optional[Agent] = None
        self.chat_history: List[Dict[str, str]] = []
        self.result_type = result_type
        self.deps_type = deps_type
        self.create_agent(system_prompt)

    def create_agent(self, system_prompt: str) -> None:
        model = self.model_manager.get_model()
        self.agent = Agent(
            model=model,
            deps_type=self.deps_type,
            system_prompt=system_prompt,
            result_type=self.result_type
        )
        logger.info(f"Initialized agent with model: {model}")

    def update_system_prompt(self, new_system_prompt: str) -> None:
        """Update the system prompt and recreate the agent with the new prompt.

        Args:
            new_system_prompt (str): The new system prompt to use for the agent.
        """
        self.create_agent(new_system_prompt)
        logger.info(f"Updated system prompt and recreated agent")

    def add_tool(self, func: Callable, tool_type: str = "tool_plain") -> None:
        if tool_type not in self.SUPPORTED_TOOL_TYPES:
            raise ValueError(f"Unsupported tool type: {tool_type}. Valid options: {self.SUPPORTED_TOOL_TYPES}")
        
        if tool_type == "tool_plain":
            self.agent.tool_plain(func)
        else:
            self.agent.tool(func)
        logger.info(f"Added tool: {func.__name__} ({tool_type})")

    def interact_with_model(self, user_input: str, deps: Dict[str, Any] = None) -> str:
        if not self.agent:
            raise ValueError("Agent not initialized - call create_agent first")
        
        self.chat_history.append({"role": "user", "content": user_input})
        deps = deps or {}
        deps["chat_history"] = self.chat_history
        
        result = self.agent.run_sync(user_input, deps=deps)
        self.chat_history.append({"role": "assistant", "content": result.data})
        return result.data

    def get_chat_history(self) -> List[Dict[str, str]]:
        return self.chat_history.copy()

    def clear_chat_history(self) -> None:
        self.chat_history.clear()
        logger.info("Chat history cleared")