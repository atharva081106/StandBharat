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

class TikTokProvider(IntegrationProvider):
    provider_id = "tiktok"
    name = "TikTok"
    category = "SOCIAL"
    capabilities = ["read", "write", "publish", "metrics"]
    auth_type = "oauth2"
    required_scopes = ["video.upload", "user.info.basic"]

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
            
            response = httpx.get("https://open.tiktokapis.com/v2/user/info/", headers=headers, timeout=10.0)
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
        
        account_id = creds.get("author_urn")
        if not account_id:
            raise AuthenticationError("Missing account identity for TikTok. Please disconnect and reconnect.")
            
        content_type = content.get("content_type")
        if content_type not in ("TIKTOK_POST", "SOCIAL_POST", "VIDEO"):
            raise UnsupportedContentError(f"Content type '{content_type}' is not supported by TikTok connector.")
            
        media_url = content.get("metadata", {}).get("media_url")
        if not media_url:
            raise ProviderError("A media_url (video) is required to publish to TikTok.")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "post_info": {
                "title": content.get("body", ""),
                "privacy_level": "PUBLIC",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": media_url
            }
        }
        
        try:
            response = httpx.post(
                "https://open.tiktokapis.com/v2/post/publish/video/init/",
                headers=headers,
                json=payload,
                timeout=15.0
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                if data.get("error", {}).get("code") != "ok":
                    raise ProviderError(f"TikTok API returned an error: {data.get('error')}")
                    
                external_id = data.get("data", {}).get("publish_id")
                return {
                    "status": "success",
                    "external_id": external_id,
                    "url": None, # Direct URL is not returned immediately
                    "raw_response": data
                }
                
            elif response.status_code == 401:
                raise AuthenticationError("TikTok access token is invalid or expired")
            elif response.status_code == 429:
                raise RateLimitError("TikTok API rate limit exceeded")
            else:
                raise ProviderError(f"TikTok API error: {response.status_code} {response.text}")
                
        except httpx.RequestError as e:
            raise ProviderError(f"Network error communicating with TikTok: {str(e)}")

    def get_metrics(self, workspace_id: str, entity_id: str) -> Dict[str, Any]:
        return {"views": 0, "likes": 0, "shares": 0}
