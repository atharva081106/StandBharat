from typing import List, Dict, Any, Optional
from .schemas import AIRequestMessage, AIResponse
from .exceptions import AINotConfiguredException, AIProviderException
from .config import ai_config
from .providers.openai import OpenAIProvider

class AIGateway:
    def __init__(self):
        self.providers = {}
        # Try to initialize configured providers
        try:
            self.providers["openai"] = OpenAIProvider()
        except AINotConfiguredException:
            pass

    def _get_provider(self, provider_name: Optional[str] = None):
        provider_name = provider_name or ai_config.DEFAULT_PROVIDER
        if provider_name not in self.providers:
            raise AINotConfiguredException(f"AI Provider '{provider_name}' is not configured.")
        return self.providers[provider_name]

    def generate(
        self,
        messages: List[AIRequestMessage],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        
        provider_impl = self._get_provider(provider)
        model = model or ai_config.DEFAULT_MODEL
        
        # Here we could implement retries and timeouts
        # For this foundation, we just pass through to the provider
        
        return provider_impl.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata=metadata
        )

ai_gateway = AIGateway()
