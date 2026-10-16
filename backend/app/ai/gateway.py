from typing import List, Dict, Any, Optional
from .schemas import AIRequestMessage, AIResponse
from .exceptions import AINotConfiguredException
from .config import ai_config
from .providers.openai import OpenAIProvider
from .providers.mistral import MistralProvider
from .providers.groq import GroqProvider
from .providers.gemini import GeminiProvider
from .providers.local import LocalSynthesisProvider

class AIGateway:
    def __init__(self):
        self.providers = {}
        # Always register local synthesis provider as resilient fallback
        self.providers["local"] = LocalSynthesisProvider()
        
        # Try to initialize configured external cloud providers
        try:
            self.providers["openai"] = OpenAIProvider()
        except AINotConfiguredException:
            pass
        try:
            self.providers["mistral"] = MistralProvider()
        except AINotConfiguredException:
            pass
        try:
            self.providers["groq"] = GroqProvider()
        except AINotConfiguredException:
            pass
        try:
            self.providers["gemini"] = GeminiProvider()
        except AINotConfiguredException:
            pass

    def _get_provider(self, provider_name: Optional[str] = None):
        target = provider_name or ai_config.DEFAULT_PROVIDER
        if target in self.providers and target != "local":
            return self.providers[target]
        # Priority for external cloud providers if available: mistral -> gemini -> groq -> openai
        for p in ["mistral", "gemini", "groq", "openai"]:
            if p in self.providers:
                return self.providers[p]
        # Resilient local domain-specific synthesis fallback
        if "local" in self.providers:
            return self.providers["local"]
        raise AINotConfiguredException(f"AI Provider '{target}' is not configured.")

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
            model = getattr(provider_impl, "default_model", "mistral-small-latest")
        elif getattr(provider_impl, "provider_name", "") == "groq" and (model.startswith("gpt-") or model.startswith("mistral-")):
            model = getattr(provider_impl, "default_model", "llama-3.3-70b-versatile")
        elif getattr(provider_impl, "provider_name", "") == "gemini" and (model.startswith("gpt-") or model.startswith("mistral-") or model.startswith("llama-")):
            model = getattr(provider_impl, "default_model", "gemini-1.5-flash")
        
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
