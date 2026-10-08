from typing import Dict, List
from .provider import IntegrationProvider

class IntegrationRegistry:
    def __init__(self):
        self._providers: Dict[str, IntegrationProvider] = {}

    def register(self, provider: IntegrationProvider):
        self._providers[provider.provider_id] = provider

    def get_provider(self, provider_id: str) -> IntegrationProvider:
        if provider_id not in self._providers:
            raise ValueError(f"Integration Provider '{provider_id}' not found")
        return self._providers[provider_id]

    def list_providers(self) -> List[IntegrationProvider]:
        return list(self._providers.values())

integration_registry = IntegrationRegistry()

from .providers.ga4 import GA4Provider
from .providers.gsc import GSCProvider
from .providers.wordpress import WordPressProvider
from .providers.linkedin import LinkedInProvider
from .providers.x import XProvider
from .providers.reddit import RedditProvider
from .providers.github import GitHubProvider

integration_registry.register(GA4Provider())
integration_registry.register(GSCProvider())
integration_registry.register(WordPressProvider())
integration_registry.register(LinkedInProvider())
integration_registry.register(XProvider())
integration_registry.register(RedditProvider())
integration_registry.register(GitHubProvider())
