from typing import List, Dict, Any, Optional
from .schemas import AIRequestMessage, AIResponse
from .exceptions import AINotConfiguredException, AIProviderException
from .config import ai_config
from .providers.openai import OpenAIProvider
from .providers.mistral import MistralProvider

class AIGateway:
    def __init__(self):
        self.providers = {}
        # Try to initialize configured providers
        try:
            self.providers["openai"] = OpenAIProvider()
        except AINotConfiguredException:
            pass
        try:
            self.providers["mistral"] = MistralProvider()
        except AINotConfiguredException:
            pass

    def _get_provider(self, provider_name: Optional[str] = None):
        target = provider_name or ai_config.DEFAULT_PROVIDER
        if target not in self.providers:
            # Fallback: if default provider (e.g. openai) is not configured, but mistral is, use mistral
            if (not provider_name or target == "openai") and "mistral" in self.providers:
                return self.providers["mistral"]
            raise AINotConfiguredException(f"AI Provider '{target}' is not configured.")
        return self.providers[target]

    def generate(
        self,
        messages: List[AIRequestMessage],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        
        provider_impl = self._get_provider(provider)
        if not model:
            model = getattr(provider_impl, "default_model", ai_config.DEFAULT_MODEL)
        elif getattr(provider_impl, "provider_name", "") == "mistral" and model.startswith("gpt-"):
            model = getattr(provider_impl, "default_model", "ministral-8b-latest")
        
        # Here we could implement retries and timeouts
        # For this foundation, we just pass through to the provider
        
        return provider_impl.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            metadata=metadata
        )

ai_gateway = AIGateway()
