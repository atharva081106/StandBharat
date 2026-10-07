import os
import requests
from typing import Dict, Any
from app.publishing.base import PublisherConnector
from app.publishing.registry import PublisherRegistry
from app.publishing.exceptions import (
    AuthenticationError,
    NotConfiguredError,
    ProviderError,
    UnsupportedContentError,
    RateLimitError
)

@PublisherRegistry.register("linkedin")
class LinkedInConnector(PublisherConnector):
    platform = "linkedin"
    
    supports_publish = True
    supports_delete = False
    supports_update = False
    supports_metrics = False
    
    def _get_access_token(self, credentials: Dict[str, Any]) -> str:
        token = credentials.get("access_token")
        if not token:
            raise AuthenticationError("Missing access token for LinkedIn")
        return token
        
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        if not credentials:
            raise NotConfiguredError()
            
        token = self._get_access_token(credentials)
        headers = {
            "Authorization": f"Bearer {token}",
            "Connection": "Keep-Alive"
        }
        
        try:
            response = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers, timeout=10)
            if response.status_code == 401:
                return False
            if response.status_code == 200:
                return True
            return False
        except requests.RequestException:
            return False

    def publish(self, credentials: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
        if not credentials:
            raise NotConfiguredError()
            
        token = self._get_access_token(credentials)
        author_urn = credentials.get("author_urn") or credentials.get("external_account_id")
        if not author_urn:
            raise AuthenticationError("Missing author URN for LinkedIn")
            
        # We only support text posts (LINKEDIN_POST) for now
        content_type = content.get("content_type")
        if content_type not in ("LINKEDIN_POST", "SOCIAL_POST", "TEXT"):
            raise UnsupportedContentError(f"Content type '{content_type}' is not supported by LinkedIn connector.")
            
        text_body = content.get("body", "")
        if not text_body:
            raise InvalidContentError("Content body is empty")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202401"
        }
        
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text_body
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code in (200, 201):
                # UGC post returns ID in X-RestLi-Id header or body
                external_id = response.headers.get("X-RestLi-Id") or response.json().get("id")
                return {
                    "external_id": external_id,
                    "status": "PUBLISHED",
                    "raw_response": response.json() if response.content else {}
                }
                
            elif response.status_code == 401:
                raise AuthenticationError("LinkedIn access token is invalid or expired")
            elif response.status_code == 429:
                raise RateLimitError("LinkedIn API rate limit exceeded")
            else:
                raise ProviderError(f"LinkedIn API error: {response.status_code} {response.text}")
                
        except requests.RequestException as e:
            raise ProviderError(f"Network error communicating with LinkedIn: {str(e)}")

    def get_publication_status(self, credentials: Dict[str, Any], external_id: str) -> Dict[str, Any]:
        # LinkedIn UGC Posts don't strictly have a 'status' endpoint that is commonly used for async polling in the same way,
        # but we can try to fetch it.
        token = self._get_access_token(credentials)
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        try:
            response = requests.get(
                f"https://api.linkedin.com/v2/ugcPosts/{external_id}",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return {"status": "PUBLISHED"}
            elif response.status_code == 404:
                return {"status": "DELETED"}
            else:
                return {"status": "UNKNOWN"}
        except requests.RequestException:
            return {"status": "UNKNOWN"}
