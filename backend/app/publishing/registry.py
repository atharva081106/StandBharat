from typing import Dict, Type
from app.publishing.base import PublisherConnector

class PublisherRegistry:
    _connectors: Dict[str, Type[PublisherConnector]] = {}

    @classmethod
    def register(cls, platform: str):
        def wrapper(connector_cls: Type[PublisherConnector]):
            cls._connectors[platform] = connector_cls
            return connector_cls
        return wrapper

    @classmethod
    def get_connector(cls, platform: str) -> PublisherConnector:
        if platform not in cls._connectors:
            raise ValueError(f"Publisher connector for platform '{platform}' not found.")
        return cls._connectors[platform]()

    @classmethod
    def list_platforms(cls) -> list[str]:
        return list(cls._connectors.keys())

# Initialize empty, will be populated by decorators in connector modules
