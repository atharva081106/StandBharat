import json
import httpx
from typing import Dict, Any, List
from app.integrations.provider import IntegrationProvider
from app.db.session import SessionLocal
from app.models.all_models import Integration
from app.core.encryption import decrypt
from app.publishing.exceptions import (
    AuthenticationError,
    NotConfiguredError,
    ProviderError,
    UnsupportedContentError,
    RateLimitError
)

class XProvider(IntegrationProvider):
    provider_id = "twitter_x"
    name = "X (Twitter)"
    category = "SOCIAL"
    capabilities = ["read", "write", "publish", "metrics"]
    auth_type = "oauth2"
    required_scopes = ["tweet.read", "tweet.write", "users.read", "offline.access"]

    def _get_credentials(self, workspace_id: str, brand_id: str = None) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            query = db.query(Integration).filter(Integration.workspace_id == workspace_id, Integration.provider == self.provider_id)
            if brand_id:
                query = query.filter(Integration.brand_id == brand_id)
            integ = query.first()
            
            if not integ or not integ.credentials_encrypted:
                raise NotConfiguredError(f"{self.name} is not connected or missing credentials")
                
            creds = json.loads(decrypt(integ.credentials_encrypted))
            return creds
        finally:
            db.close()

    def connect(self, workspace_id: str, credentials: Dict[str, Any]) -> bool:
        return True

    def validate(self, workspace_id: str) -> bool:
        try:
            creds = self._get_credentials(workspace_id)
            token = creds.get("access_token")
            if not token:
                return False
                
            headers = {
                "Authorization": f"Bearer {token}",
            }
            
            response = httpx.get("https://api.twitter.com/2/users/me", headers=headers, timeout=10.0)
            if response.status_code == 200:
                return True
            return False
        except Exception:
            return False

    def refresh(self, workspace_id: str) -> bool:
        return True

    def sync(self, workspace_id: str) -> Dict[str, Any]:
        return {"status": "success", "posts_synced": 0}

    def publish(self, workspace_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        brand_id = content.get("brand_id")
        creds = self._get_credentials(workspace_id, brand_id)
        token = creds.get("access_token")
        
        author_urn = creds.get("author_urn")
        if not author_urn:
            raise AuthenticationError("Missing author identity for X. Please disconnect and reconnect.")
            
        content_type = content.get("content_type")
        if content_type not in ("X_POST", "TWITTER_POST", "SOCIAL_POST", "TEXT"):
            raise UnsupportedContentError(f"Content type '{content_type}' is not supported by X connector.")
            
        text_body = content.get("body", "")
        if not text_body:
            raise ProviderError("Content body is empty")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "text": text_body
        }
        
        try:
            response = httpx.post(
                "https://api.twitter.com/2/tweets",
                headers=headers,
                json=payload,
                timeout=15.0
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                external_id = data.get("data", {}).get("id")
                return {
                    "status": "success",
                    "external_id": external_id,
                    "url": f"https://twitter.com/user/status/{external_id}" if external_id else None,
                    "raw_response": data
                }
                
            elif response.status_code == 401:
                raise AuthenticationError("X access token is invalid or expired")
            elif response.status_code == 429:
                raise RateLimitError("X API rate limit exceeded")
            else:
                raise ProviderError(f"X API error: {response.status_code} {response.text}")
                
        except httpx.RequestError as e:
            raise ProviderError(f"Network error communicating with X: {str(e)}")

    def get_metrics(self, workspace_id: str, entity_id: str) -> Dict[str, Any]:
        return {"likes": 0, "retweets": 0, "impressions": 0}
