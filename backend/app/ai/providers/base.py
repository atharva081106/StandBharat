from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..schemas import AIRequestMessage, AIResponse

class BaseAIProvider(ABC):
    
    @abstractmethod
    def generate(
        self,
        messages: List[AIRequestMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        pass
