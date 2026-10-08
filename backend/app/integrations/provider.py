from abc import ABC, abstractmethod
from typing import Dict, Any, List

class IntegrationProvider(ABC):
    """
    Base contract for all external integration providers (GA4, GSC, LinkedIn, etc.)
    """
    provider_id: str
    name: str
    category: str
    capabilities: List[str] # E.g., ['read', 'write', 'publish', 'metrics']
    auth_type: str # E.g., 'oauth2', 'api_key'
    required_scopes: List[str]

    @abstractmethod
    def connect(self, workspace_id: str, credentials: Dict[str, Any]) -> bool:
        """Initialize the connection and securely store credentials"""
        pass

    @abstractmethod
    def validate(self, workspace_id: str) -> bool:
        """Validate if the current connection is still active and valid"""
        pass

    @abstractmethod
    def refresh(self, workspace_id: str) -> bool:
        """Refresh auth tokens if applicable"""
        pass

    @abstractmethod
    def sync(self, workspace_id: str) -> Dict[str, Any]:
        """Perform data synchronization (e.g., fetch metrics into DB)"""
        pass

    @abstractmethod
    def publish(self, workspace_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Publish content to the provider"""
        pass

    @abstractmethod
    def get_metrics(self, workspace_id: str, entity_id: str) -> Dict[str, Any]:
        """Fetch metrics for a specific entity (like a published post)"""
        pass
