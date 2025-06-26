from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    @abstractmethod
    def configure(self, **kwargs) -> None:
        pass

    def get_model_name(self) -> str:
        return self.model_name