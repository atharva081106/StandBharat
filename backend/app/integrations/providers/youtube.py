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

class YouTubeProvider(IntegrationProvider):
    provider_id = "youtube"
    name = "YouTube"
    category = "SOCIAL"
    capabilities = ["read", "write", "publish", "metrics"]
    auth_type = "oauth2"
    required_scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]

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
            
            response = httpx.get("https://www.googleapis.com/youtube/v3/channels?part=id&mine=true", headers=headers, timeout=10.0)
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
        
        content_type = content.get("content_type")
        if content_type not in ("YOUTUBE_VIDEO", "VIDEO"):
            raise UnsupportedContentError(f"Content type '{content_type}' is not supported by YouTube connector.")
            
        title = content.get("title", "")
        description = content.get("body", "")
        media_url = content.get("metadata", {}).get("media_url")
        
        if not title:
            raise ProviderError("A title is required to publish to YouTube.")
        if not media_url:
            raise ProviderError("A media_url (video) is required to publish to YouTube.")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Note: In a real implementation, downloading the media and using the resumable upload API is necessary.
        # This is a stub for the metadata creation part of the upload.
        payload = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "22" # People & Blogs
            },
            "status": {
                "privacyStatus": "public"
            }
        }
        
        try:
            # Stubbed: Real upload requires posting to https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable
            # then uploading chunks.
            response = httpx.post(
                "https://www.googleapis.com/youtube/v3/videos?part=snippet,status",
                headers=headers,
                json=payload,
                timeout=15.0
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                external_id = data.get("id")
                return {
                    "status": "success",
                    "external_id": external_id,
                    "url": f"https://youtu.be/{external_id}" if external_id else None,
                    "raw_response": data
                }
                
            elif response.status_code == 401:
                raise AuthenticationError("YouTube access token is invalid or expired")
            elif response.status_code == 429:
                raise RateLimitError("YouTube API rate limit exceeded")
            else:
                raise ProviderError(f"YouTube API error: {response.status_code} {response.text}")
                
        except httpx.RequestError as e:
            raise ProviderError(f"Network error communicating with YouTube: {str(e)}")

    def get_metrics(self, workspace_id: str, entity_id: str) -> Dict[str, Any]:
        return {"views": 0, "likes": 0, "comments": 0}
