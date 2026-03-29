from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ReasoningResult:
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    confidence: float = 1.0


class ReasoningEngine(ABC):
    @abstractmethod
    def think(self, task: str, memory_context: str, available_tools: List[Dict[str, str]]) -> ReasoningResult:
        pass

    @abstractmethod
    def supports_tokens(self) -> bool:
        pass
