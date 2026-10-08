import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from backend.app.core.llm_provider import get_llm_provider, BaseLLMProvider

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")
        self.llm: BaseLLMProvider = get_llm_provider()

    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the claim state and return the agent's updated contributions.
        """
        pass
