from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class PublisherConnector(ABC):
    platform: str
    
    # Capabilities
    supports_publish: bool = True
    supports_delete: bool = False
    supports_update: bool = False
    supports_metrics: bool = False
    
    @abstractmethod
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        pass
        
    @abstractmethod
    def publish(self, credentials: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publishes content to the external platform.
        Returns a dictionary containing 'external_id' and 'status' (and any other metadata).
        """
        pass
        
    @abstractmethod
    def get_publication_status(self, credentials: Dict[str, Any], external_id: str) -> Dict[str, Any]:
        pass
        
    def delete_or_unpublish(self, credentials: Dict[str, Any], external_id: str) -> bool:
        if not self.supports_delete:
            raise NotImplementedError(f"Delete not supported for {self.platform}")
        pass
