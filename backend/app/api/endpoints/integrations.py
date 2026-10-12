from fastapi import APIRouter, Depends, HTTPException, Body, Request
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import uuid
import time
import logging

logger = logging.getLogger(__name__)

from app.api.deps import get_db, get_current_user, get_current_brand
from app.models.all_models import User, Brand, Integration

router = APIRouter()

INTEGRATION_CATALOG = [
    {"id": "ga4",         "provider": "Google Analytics 4",  "category": "Analytics",  "capabilities": ["traffic", "conversions", "goals"]},
    {"id": "gsc",         "provider": "Google Search Console","category": "SEO",        "capabilities": ["impressions", "clicks", "keywords"]},
    {"id": "linkedin",    "provider": "LinkedIn",             "category": "Social",     "capabilities": ["publish", "analytics"]},
    {"id": "twitter_x",   "provider": "X (Twitter)",          "category": "Social",     "capabilities": ["publish", "analytics"]},
    {"id": "reddit",      "provider": "Reddit",               "category": "Social",     "capabilities": ["publish"]},
    {"id": "wordpress",   "provider": "WordPress",            "category": "CMS",        "capabilities": ["publish"]},
    {"id": "webflow",     "provider": "Webflow",              "category": "CMS",        "capabilities": ["publish"]},
    {"id": "framer",      "provider": "Framer",               "category": "CMS",        "capabilities": ["publish"], "status_override": "COMING_SOON"},
    {"id": "wix",         "provider": "Wix",                  "category": "CMS",        "capabilities": ["publish"], "status_override": "COMING_SOON"},
    {"id": "sanity",      "provider": "Sanity",               "category": "CMS",        "capabilities": ["publish"], "status_override": "COMING_SOON"},
    {"id": "github",      "provider": "GitHub",               "category": "Developer",  "capabilities": ["code_publish"]},
    {"id": "slack",       "provider": "Slack",                "category": "Comms",      "capabilities": ["notify"]},
    {"id": "whatsapp",    "provider": "WhatsApp",             "category": "Comms",      "capabilities": ["notify"], "status_override": "COMING_SOON"},
    {"id": "telegram",    "provider": "Telegram",             "category": "Comms",      "capabilities": ["notify"], "status_override": "COMING_SOON"},
    {"id": "instagram",   "provider": "Instagram",            "category": "Social",     "capabilities": ["publish", "analytics"], "status_override": "COMING_SOON"},
    {"id": "tiktok",      "provider": "TikTok",               "category": "Social",     "capabilities": ["publish", "analytics"], "status_override": "COMING_SOON"},
]

class IntegrationResponse(BaseModel):
    id: str
    provider: str
    category: str
    capabilities: List[str]
    status: str
    last_sync_at: Optional[str] = None
    last_error: Optional[str] = None

@router.get("/", response_model=List[IntegrationResponse])
def list_integrations(
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    active_integrations = db.query(Integration).filter(Integration.brand_id == brand.id).all()
    active_map = {integ.provider: integ for integ in active_integrations}

    result = []
    for item in INTEGRATION_CATALOG:
        if item["id"] in active_map:
            db_integ = active_map[item["id"]]
            status = db_integ.status
            last_sync_at = db_integ.last_sync_at.isoformat() if db_integ.last_sync_at else None
            last_error = db_integ.last_error
        else:
            status = item.get("status_override", "NOT_CONFIGURED")
            last_sync_at = None
            last_error = None
            
        result.append(IntegrationResponse(
            id=item["id"],
            provider=item["provider"],
            category=item["category"],
            capabilities=item["capabilities"],
            status=status,
            last_sync_at=last_sync_at,
            last_error=last_error
        ))
    return result

import json
from app.core.encryption import encrypt, decrypt
from app.models.all_models import IntegrationSyncRun
from app.worker import sync_integration as sync_integration_task

@router.post("/{integration_id}/connect")
def connect_integration(
    integration_id: str,
    credentials: Dict[str, Any] = Body(...),
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    if not any(item["id"] == integration_id for item in INTEGRATION_CATALOG):
        raise HTTPException(status_code=404, detail="Integration provider not found")
        
    # Disallow dummy/mock tokens or empty credentials
    if not credentials or "dummy_token" in credentials or credentials.get("dummy_token") == "mock_credential_123":
        raise HTTPException(status_code=400, detail="Valid credentials required; mock tokens are not permitted")

    # Validate connection using the provider
    try:
        from app.integrations.registry import integration_registry
        provider = integration_registry.get_provider(integration_id)
        if not provider.connect(str(brand.workspace_id), credentials):
            raise HTTPException(status_code=400, detail="Connection validation failed")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection validation error: {str(e)}")
        
    integ = db.query(Integration).filter(Integration.brand_id == brand.id, Integration.provider == integration_id).first()
    creds_str = json.dumps(credentials)
    encrypted = encrypt(creds_str)

    if not integ:
        integ = Integration(
            workspace_id=brand.workspace_id,
            brand_id=brand.id,
            provider=integration_id,
            credentials_encrypted=encrypted,
            status="CONNECTED"
        )
        db.add(integ)
    else:
        integ.credentials_encrypted = encrypted
        integ.status = "CONNECTED"
        integ.last_error = None
    
    db.commit()
    return {"status": "SUCCESS"}

@router.post("/{integration_id}/disconnect")
def disconnect_integration(
    integration_id: str,
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    integ = db.query(Integration).filter(Integration.brand_id == brand.id, Integration.provider == integration_id).first()
    if integ:
        db.delete(integ)
        db.commit()
    return {"status": "SUCCESS"}

@router.post("/{integration_id}/sync")
def sync_integration_endpoint(
    integration_id: str,
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    integ = db.query(Integration).filter(Integration.brand_id == brand.id, Integration.provider == integration_id).first()
    if not integ:
        raise HTTPException(status_code=404, detail="Integration not configured")
        
    run = IntegrationSyncRun(
        integration_id=integ.id,
        workspace_id=brand.workspace_id,
        brand_id=brand.id,
        provider_id=integration_id,
        status="QUEUED"
    )
    db.add(run)
    integ.status = "SYNCING"
    db.commit()
    
    sync_integration_task.delay(str(run.id))
    
    return {"status": "QUEUED", "run_id": str(run.id)}

@router.get("/{integration_id}/oauth/login")
def oauth_login(
    integration_id: str,
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    """
    Initiate the OAuth flow for the integration.
    """
    if integration_id not in ["gsc", "ga4", "linkedin", "twitter_x", "reddit"]:
        raise HTTPException(status_code=400, detail="OAuth not supported for this provider")
        
    try:
        import urllib.parse
        from app.core.config import settings

        # Replay-protected state parameter including timestamp and HMAC signature
        import hmac
        import hashlib
        now_ts = int(time.time())
        payload = f"{brand.workspace_id}:{brand.id}:{integration_id}:{now_ts}"
        signature = hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        state = f"{payload}:{signature}"

        if integration_id == "linkedin":
            if not settings.LINKEDIN_CLIENT_ID:
                raise HTTPException(status_code=500, detail="LinkedIn OAuth configuration is missing (LINKEDIN_CLIENT_ID not set)")
            client_id = settings.LINKEDIN_CLIENT_ID
            redirect_uri = settings.OAUTH_REDIRECT_URI
            scopes = "w_member_social r_liteprofile"
            
            auth_url = (
                f"https://www.linkedin.com/oauth/v2/authorization?"
                f"response_type=code&client_id={client_id}&"
                f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
                f"state={urllib.parse.quote(state)}&"
                f"scope={urllib.parse.quote(scopes)}"
            )
            return {"authorization_url": auth_url}

        if integration_id == "twitter_x":
            client_id = getattr(settings, "X_CLIENT_ID", "X_CLIENT_ID_PLACEHOLDER")
            redirect_uri = settings.OAUTH_REDIRECT_URI
            scopes = "tweet.read tweet.write users.read offline.access"
            # In a real app we need PKCE code_challenge
            code_challenge = "challenge"
            auth_url = (
                f"https://twitter.com/i/oauth2/authorize?"
                f"response_type=code&client_id={client_id}&"
                f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
                f"state={urllib.parse.quote(state)}&"
                f"scope={urllib.parse.quote(scopes)}&"
                f"code_challenge={code_challenge}&code_challenge_method=plain"
            )
            return {"authorization_url": auth_url}

        if integration_id == "reddit":
            client_id = getattr(settings, "REDDIT_CLIENT_ID", "REDDIT_CLIENT_ID_PLACEHOLDER")
            redirect_uri = settings.OAUTH_REDIRECT_URI
            scopes = "read submit identity"
            auth_url = (
                f"https://www.reddit.com/api/v1/authorize?"
                f"client_id={client_id}&response_type=code&"
                f"state={urllib.parse.quote(state)}&"
                f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
                f"duration=permanent&scope={urllib.parse.quote(scopes)}"
            )
            return {"authorization_url": auth_url}
        from google_auth_oauthlib.flow import Flow
        scopes = [
            "https://www.googleapis.com/auth/webmasters.readonly" if integration_id == "gsc" 
            else "https://www.googleapis.com/auth/analytics.readonly"
        ]
        
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="Google OAuth configuration is missing (GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set)")
            
        google_redirect_uri = getattr(settings, "GOOGLE_REDIRECT_URI", None) or settings.OAUTH_REDIRECT_URI
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=scopes,
            redirect_uri=google_redirect_uri
        )
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )
        
        return {"authorization_url": authorization_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth initiation failed: {str(e)}")

@router.get("/oauth/callback")
@router.get("/google/callback")
def oauth_callback(
    request: Request,
    state: Optional[str] = None,
    code: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Complete the OAuth flow and store credentials.
    """
    from app.core.config import settings
    import urllib.parse
    import hmac
    import hashlib

    # 1. Handle user-denied or provider-reported OAuth errors
    if error:
        redirect_url = f"{settings.FRONTEND_URL}/app/integrations?status=error&error={urllib.parse.quote(error)}"
        accept = request.headers.get("accept", "")
        if ("text/html" in accept or request.query_params.get("redirect") == "true") and not accept.startswith("application/json"):
            return RedirectResponse(url=redirect_url, status_code=302)
        return {"status": "ERROR", "error": error, "redirect_url": redirect_url}

    if not state or not code:
        raise HTTPException(status_code=400, detail="Missing required state or code parameter")

    try:
        # 2. State validation: Extract workspace, brand, integration_id (supports 5-part timestamped or 4-part legacy)
        parts = state.split(':')
        if len(parts) == 5:
            workspace_id, brand_id, integration_id, ts_str, signature = parts
            payload = f"{workspace_id}:{brand_id}:{integration_id}:{ts_str}"
            try:
                state_age = int(time.time()) - int(ts_str)
                if state_age > 900 or state_age < -60:  # 15 min expiration window with clock skew allowance
                    raise HTTPException(status_code=400, detail="OAuth state has expired")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid state timestamp format")
        elif len(parts) == 4:
            workspace_id, brand_id, integration_id, signature = parts
            payload = f"{workspace_id}:{brand_id}:{integration_id}"
        else:
            raise HTTPException(status_code=400, detail="Invalid state parameter format")

        expected_signature = hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=403, detail="Cross-tenant access or tampered state denied")
        
        from app.core.config import settings
        import httpx

        if integration_id == "linkedin":
            if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET:
                raise HTTPException(status_code=500, detail="LinkedIn OAuth configuration is missing")
            client_id = settings.LINKEDIN_CLIENT_ID
            client_secret = settings.LINKEDIN_CLIENT_SECRET
            redirect_uri = settings.OAUTH_REDIRECT_URI
            
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri
            }
            # Using httpx synchronously in the endpoint for simplicity, although it blocks
            # But the existing code is sync anyway
            resp = httpx.post(token_url, data=data, timeout=10.0)
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail=f"LinkedIn token exchange failed: {resp.text}")
                
            token_data = resp.json()
            access_token = token_data.get("access_token")
            
            # Fetch user info to get the URN
            userinfo_url = "https://api.linkedin.com/v2/userinfo"
            user_resp = httpx.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=10.0)
            author_urn = None
            if user_resp.status_code == 200:
                author_urn = f"urn:li:person:{user_resp.json().get('sub')}"

            creds_dict = {
                "access_token": access_token,
                "expires_in": token_data.get("expires_in"),
                "refresh_token": token_data.get("refresh_token"),
                "refresh_token_expires_in": token_data.get("refresh_token_expires_in"),
                "scope": token_data.get("scope"),
                "author_urn": author_urn
            }
        elif integration_id == "twitter_x":
            client_id = getattr(settings, "X_CLIENT_ID", "X_CLIENT_ID_PLACEHOLDER")
            client_secret = getattr(settings, "X_CLIENT_SECRET", "X_CLIENT_SECRET_PLACEHOLDER")
            redirect_uri = settings.OAUTH_REDIRECT_URI
            
            token_url = "https://api.twitter.com/2/oauth2/token"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "code_verifier": "challenge" # In reality matches PKCE
            }
            auth = (client_id, client_secret)
            resp = httpx.post(token_url, data=data, auth=auth, timeout=10.0)
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail=f"X token exchange failed: {resp.text}")
                
            token_data = resp.json()
            access_token = token_data.get("access_token")
            
            userinfo_url = "https://api.twitter.com/2/users/me"
            user_resp = httpx.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=10.0)
            author_urn = None
            if user_resp.status_code == 200:
                author_urn = user_resp.json().get("data", {}).get("id")

            creds_dict = {
                "access_token": access_token,
                "expires_in": token_data.get("expires_in"),
                "refresh_token": token_data.get("refresh_token"),
                "scope": token_data.get("scope"),
                "author_urn": author_urn
            }
        elif integration_id == "reddit":
            client_id = getattr(settings, "REDDIT_CLIENT_ID", "REDDIT_CLIENT_ID_PLACEHOLDER")
            client_secret = getattr(settings, "REDDIT_CLIENT_SECRET", "REDDIT_CLIENT_SECRET_PLACEHOLDER")
            redirect_uri = settings.OAUTH_REDIRECT_URI
            
            token_url = "https://www.reddit.com/api/v1/access_token"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri
            }
            auth = (client_id, client_secret)
            headers = {"User-Agent": "StandBharat/1.0"}
            resp = httpx.post(token_url, data=data, auth=auth, headers=headers, timeout=10.0)
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Reddit token exchange failed: {resp.text}")
                
            token_data = resp.json()
            access_token = token_data.get("access_token")
            
            userinfo_url = "https://oauth.reddit.com/api/v1/me"
            user_resp = httpx.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}", "User-Agent": "StandBharat/1.0"}, timeout=10.0)
            author_urn = None
            if user_resp.status_code == 200:
                author_urn = user_resp.json().get("name")

            creds_dict = {
                "access_token": access_token,
                "expires_in": token_data.get("expires_in"),
                "refresh_token": token_data.get("refresh_token"),
                "scope": token_data.get("scope"),
                "author_urn": author_urn
            }
        else:
            if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                raise HTTPException(status_code=500, detail="Google OAuth configuration is missing")
                
            from google_auth_oauthlib.flow import Flow
            google_redirect_uri = getattr(settings, "GOOGLE_REDIRECT_URI", None) or settings.OAUTH_REDIRECT_URI
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                scopes=[], # scopes inferred from token
                redirect_uri=google_redirect_uri
            )
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            creds_dict = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes
            }
            
        creds_str = json.dumps(creds_dict)
        encrypted = encrypt(creds_str)
        
        integ = db.query(Integration).filter(Integration.brand_id == brand_id, Integration.provider == integration_id).first()
        if not integ:
            integ = Integration(
                workspace_id=workspace_id,
                brand_id=brand_id,
                provider=integration_id,
                credentials_encrypted=encrypted,
                status="CONNECTED"
            )
            db.add(integ)
        else:
            integ.credentials_encrypted = encrypted
            integ.status = "CONNECTED"
            integ.last_error = None
            
        db.commit()
        
        # Enqueue initial sync ONLY AFTER successful database commit
        run = IntegrationSyncRun(
            integration_id=integ.id,
            workspace_id=integ.workspace_id,
            brand_id=integ.brand_id,
            provider_id=integration_id,
            status="QUEUED"
        )
        db.add(run)
        db.commit()

        try:
            sync_integration_task.delay(str(run.id))
        except Exception as dispatch_err:
            logger.warning(f"Initial sync dispatch failed for integration {integ.id}: {dispatch_err}")
            run.status = "FAILED"
            run.error = f"Initial sync dispatch failed: {str(dispatch_err)}"
            db.commit()

        redirect_url = f"{settings.FRONTEND_URL}/app/integrations?status=success&provider={integration_id}"
        accept = request.headers.get("accept", "")
        # If request is from browser navigation, issue HTTP 302 redirect
        if ("text/html" in accept or request.query_params.get("redirect") == "true") and not accept.startswith("application/json"):
            return RedirectResponse(url=redirect_url, status_code=302)
        
        # Programmatic callers receive structured JSON with redirect_url
        return {"status": "SUCCESS", "message": "Successfully connected", "redirect_url": redirect_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}")

class ConfigureGA4PropertyRequest(BaseModel):
    property_id: str
    property_name: Optional[str] = None

@router.get("/ga4/properties")
def list_ga4_properties(
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    integ = db.query(Integration).filter(
        Integration.brand_id == brand.id,
        Integration.provider == "ga4"
    ).first()
    if not integ or not integ.credentials_encrypted:
        raise HTTPException(status_code=400, detail="GA4 integration is not connected")
        
    try:
        creds_json = json.loads(decrypt(integ.credentials_encrypted))
        from google.oauth2.credentials import Credentials
        from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
        creds = Credentials(**creds_json)
        admin_client = AnalyticsAdminServiceClient(credentials=creds)
        summaries = admin_client.list_account_summaries()
        properties = []
        for account in summaries:
            for prop_sum in account.property_summaries:
                p_id = prop_sum.property.split("/")[-1] if "/" in prop_sum.property else prop_sum.property
                properties.append({
                    "property_id": p_id,
                    "display_name": prop_sum.display_name,
                    "account_name": account.display_name
                })
        return {"properties": properties}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch GA4 properties: {str(e)}")

@router.post("/ga4/configure-property")
def configure_ga4_property(
    payload: ConfigureGA4PropertyRequest,
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    integ = db.query(Integration).filter(
        Integration.brand_id == brand.id,
        Integration.provider == "ga4"
    ).first()
    if not integ:
        raise HTTPException(status_code=400, detail="GA4 integration is not connected")
    
    prop_id = payload.property_id.strip()
    if prop_id.startswith("properties/"):
        prop_id = prop_id.split("/")[-1]
        
    if not integ.config:
        integ.config = {}
    else:
        integ.config = dict(integ.config)
        
    integ.config["property_id"] = prop_id
    if payload.property_name:
        integ.config["property_name"] = payload.property_name
    integ.status = "CONNECTED"
    integ.last_error = None
    db.commit()

    # Enqueue initial sync with newly configured property
    run = IntegrationSyncRun(
        integration_id=integ.id,
        workspace_id=integ.workspace_id,
        brand_id=integ.brand_id,
        provider_id="ga4",
        status="QUEUED"
    )
    db.add(run)
    db.commit()
    try:
        sync_integration_task.delay(str(run.id))
    except Exception as err:
        logger.warning(f"Sync dispatch failed after GA4 property config: {err}")
        run.status = "FAILED"
        run.error = f"Dispatch failed: {str(err)}"
        db.commit()

    return {"status": "SUCCESS", "property_id": prop_id}
