from typing import Dict, Any, List
from app.integrations.provider import IntegrationProvider

class GitHubProvider(IntegrationProvider):
    provider_id = "github"
    name = "GitHub"
    category = "DEVELOPER"
    capabilities = ["read", "write", "pull_request"]
    auth_type = "oauth2"
    required_scopes = ["repo"]

    def connect(self, workspace_id: str, credentials: Dict[str, Any]) -> bool:
        return True

    def validate(self, workspace_id: str) -> bool:
        return True

    def refresh(self, workspace_id: str) -> bool:
        return True

    def sync(self, workspace_id: str) -> Dict[str, Any]:
        return {"status": "success"}

    def publish(self, workspace_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "external_id": "pr-42", "url": "https://github.com/pr/42"}

    def get_metrics(self, workspace_id: str, entity_id: str) -> Dict[str, Any]:
        return {"status": "merged"}
