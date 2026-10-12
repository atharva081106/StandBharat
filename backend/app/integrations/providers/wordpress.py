from typing import Dict, Any, List
import json
import httpx
from app.integrations.provider import IntegrationProvider
from app.db.session import SessionLocal
from app.models.all_models import Integration
from app.core.encryption import decrypt
from app.publishing.exceptions import AuthenticationError, PublishingError
from app.services.website_analysis import is_safe_url, SSRFProtectionError

class WordPressProvider(IntegrationProvider):
    provider_id = "wordpress"
    name = "WordPress"
    category = "CMS"
    capabilities = ["read", "write", "publish"]
    auth_type = "app_password"
    required_scopes = []

    def connect(self, workspace_id: str, credentials: Dict[str, Any]) -> bool:
        site_url = credentials.get("site_url")
        username = credentials.get("username")
        password = credentials.get("app_password")
        
        if not site_url or not username or not password:
            raise ValueError("site_url, username, and app_password are required")
            
        if not is_safe_url(site_url):
            raise SSRFProtectionError("Invalid or unsafe WordPress site URL")
            
        api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/users/me"
        try:
            response = httpx.get(
                api_url, 
                auth=(username, password),
                timeout=10.0,
                follow_redirects=True
            )
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403):
                raise ValueError("WordPress authentication failed. Please check your credentials.")
            raise ValueError(f"WordPress API error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ValueError(f"Could not connect to WordPress site: {str(e)}")

    def validate(self, workspace_id: str) -> bool:
        return True

    def refresh(self, workspace_id: str) -> bool:
        return True

    def sync(self, workspace_id: str) -> Dict[str, Any]:
        return {"status": "success", "posts_synced": 0}

    def publish(self, workspace_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        brand_id = content.get("brand_id")
        db = SessionLocal()
        try:
            query = db.query(Integration).filter(Integration.workspace_id == workspace_id, Integration.provider == self.provider_id)
            if brand_id:
                query = query.filter(Integration.brand_id == brand_id)
            integ = query.first()
            
            if not integ or not integ.credentials_encrypted:
                raise AuthenticationError("WordPress is not connected or missing credentials")
                
            creds = json.loads(decrypt(integ.credentials_encrypted))
            site_url = creds.get("site_url")
            username = creds.get("username")
            password = creds.get("app_password")
            
            if not site_url or not username or not password:
                raise AuthenticationError("WordPress credentials incomplete")
                
            api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
            payload = {
                "title": content.get("title", "Untitled"),
                "content": content.get("body", ""),
                "status": "publish" # Create as published immediately, as per PublishingRouter logic
            }
            
            try:
                response = httpx.post(
                    api_url,
                    json=payload,
                    auth=(username, password),
                    timeout=30.0,
                    follow_redirects=True
                )
                
                if response.status_code in (401, 403):
                    raise AuthenticationError("WordPress authentication failed or insufficient permissions")
                    
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "external_id": str(data.get("id")),
                    "url": data.get("link")
                }
            except httpx.HTTPStatusError as e:
                raise PublishingError(f"WordPress API error: {e.response.text}", "PROVIDER_ERROR")
            except httpx.RequestError as e:
                raise PublishingError(f"Network error: {str(e)}", "NETWORK_ERROR")
        finally:
            db.close()

    def get_metrics(self, workspace_id: str, entity_id: str) -> Dict[str, Any]:
        raise NotImplementedError("WordPress does not support metrics directly")
