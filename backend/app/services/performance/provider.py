from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from uuid import UUID

class PerformanceProvider(ABC):
    """
    Abstract base class for channel performance providers.
    """
    
    @abstractmethod
    def get_available_metrics(self) -> List[str]:
        """Return a list of metrics supported by this provider."""
        pass

    @abstractmethod
    async def get_publication_metrics(self, external_post_id: str, connection: Any) -> Dict[str, Any]:
        """
        Fetch performance metrics for a specific publication.
        Returns a dictionary matching PerformanceSnapshot fields.
        If credentials or permissions do not support analytics, should return a dict with source_status='ANALYTICS_NOT_AVAILABLE'
        """
        pass

    @abstractmethod
    async def get_account_metrics(self, connection: Any) -> Dict[str, Any]:
        """Fetch overall account performance metrics."""
        pass
