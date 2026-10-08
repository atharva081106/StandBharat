from typing import Dict, Any, List
from app.integrations.provider import IntegrationProvider

class WordPressProvider(IntegrationProvider):
    provider_id = "wordpress"
    name = "WordPress"
    category = "CMS"
    capabilities = ["read", "write", "publish"]
    auth_type = "app_password"
    required_scopes = []

    def connect(self, workspace_id: str, credentials: Dict[str, Any]) -> bool:
        return True

    def validate(self, workspace_id: str) -> bool:
        return True

    def refresh(self, workspace_id: str) -> bool:
        return True

    def sync(self, workspace_id: str) -> Dict[str, Any]:
        return {"status": "success", "posts_synced": 10}

    def publish(self, workspace_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "external_id": "wp-100", "url": "https://example.com/post"}

    def get_metrics(self, workspace_id: str, entity_id: str) -> Dict[str, Any]:
        raise NotImplementedError("WordPress does not support metrics directly")
