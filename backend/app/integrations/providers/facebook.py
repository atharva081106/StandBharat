import json
import httpx
from typing import Dict, Any
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

class FacebookProvider(IntegrationProvider):
    provider_id = "facebook"
    name = "Facebook Pages"
    category = "SOCIAL"
    capabilities = ["read", "write", "publish", "metrics"]
    auth_type = "oauth2"
    required_scopes = ["pages_manage_posts", "pages_read_engagement"]

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
                
            response = httpx.get(
                "https://graph.facebook.com/me", 
                params={"access_token": token},
                timeout=10.0
            )
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
        
        page_id = creds.get("author_urn")
        if not page_id:
            raise AuthenticationError("Missing page identity for Facebook. Please disconnect and reconnect.")
            
        content_type = content.get("content_type")
        if content_type not in ("FACEBOOK_POST", "SOCIAL_POST", "TEXT", "IMAGE", "VIDEO"):
            raise UnsupportedContentError(f"Content type '{content_type}' is not supported by Facebook connector.")
            
        text_body = content.get("body", "")
        media_url = content.get("metadata", {}).get("media_url")
        
        if not text_body and not media_url:
            raise ProviderError("A body or media_url is required to publish to Facebook.")
            
        payload = {
            "message": text_body,
            "access_token": token
        }
        
        endpoint = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        if media_url:
            if content_type == "VIDEO":
                endpoint = f"https://graph.facebook.com/v19.0/{page_id}/videos"
                payload["file_url"] = media_url
                payload["description"] = text_body
            else:
                endpoint = f"https://graph.facebook.com/v19.0/{page_id}/photos"
                payload["url"] = media_url
        
        try:
            response = httpx.post(endpoint, data=payload, timeout=15.0)
            
            if response.status_code in (200, 201):
                data = response.json()
                external_id = data.get("id")
                return {
                    "status": "success",
                    "external_id": external_id,
                    "url": f"https://facebook.com/{external_id}" if external_id else None,
                    "raw_response": data
                }
                
            elif response.status_code == 401:
                raise AuthenticationError("Facebook access token is invalid or expired")
            elif response.status_code == 429:
                raise RateLimitError("Facebook API rate limit exceeded")
            else:
                raise ProviderError(f"Facebook API error: {response.status_code} {response.text}")
                
        except httpx.RequestError as e:
            raise ProviderError(f"Network error communicating with Facebook: {str(e)}")

    def get_metrics(self, workspace_id: str, entity_id: str) -> Dict[str, Any]:
        return {"likes": 0, "comments": 0, "shares": 0}
