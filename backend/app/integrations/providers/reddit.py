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

class RedditProvider(IntegrationProvider):
    provider_id = "reddit"
    name = "Reddit"
    category = "SOCIAL"
    capabilities = ["read", "write", "publish"]
    auth_type = "oauth2"
    required_scopes = ["read", "submit", "identity"]

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
                "User-Agent": "StandBharat/1.0"
            }
            
            response = httpx.get("https://oauth.reddit.com/api/v1/me", headers=headers, timeout=10.0)
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
            raise AuthenticationError("Missing author identity for Reddit. Please disconnect and reconnect.")
            
        content_type = content.get("content_type")
        if content_type not in ("REDDIT_POST", "SOCIAL_POST", "TEXT"):
            raise UnsupportedContentError(f"Content type '{content_type}' is not supported by Reddit connector.")
            
        text_body = content.get("body", "")
        title = content.get("title", "")
        metadata = content.get("metadata", {})
        subreddit = metadata.get("subreddit")
        
        if not subreddit:
            raise ProviderError("A subreddit must be provided in the metadata to publish to Reddit.")
            
        if not title:
            raise ProviderError("Content title is required for Reddit posts.")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "StandBharat/1.0"
        }
        
        payload = {
            "api_type": "json",
            "kind": "self",
            "title": title,
            "text": text_body,
            "sr": subreddit
        }
        
        try:
            response = httpx.post(
                "https://oauth.reddit.com/api/submit",
                headers=headers,
                data=payload,
                timeout=15.0
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                errors = data.get("json", {}).get("errors", [])
                if errors:
                    raise ProviderError(f"Reddit API returned errors: {errors}")
                    
                post_data = data.get("json", {}).get("data", {})
                external_id = post_data.get("id")
                url = post_data.get("url")
                
                return {
                    "status": "success",
                    "external_id": external_id,
                    "url": url,
                    "raw_response": data
                }
                
            elif response.status_code == 401:
                raise AuthenticationError("Reddit access token is invalid or expired")
            elif response.status_code == 429:
                raise RateLimitError("Reddit API rate limit exceeded")
            else:
                raise ProviderError(f"Reddit API error: {response.status_code} {response.text}")
                
        except httpx.RequestError as e:
            raise ProviderError(f"Network error communicating with Reddit: {str(e)}")

    def get_metrics(self, workspace_id: str, entity_id: str) -> Dict[str, Any]:
        return {"upvotes": 0, "comments": 0}
