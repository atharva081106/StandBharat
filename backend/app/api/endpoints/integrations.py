from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import uuid

from app.api.deps import get_db, get_current_user, get_current_brand
from app.models.all_models import User, Brand, Integration

router = APIRouter()

INTEGRATION_CATALOG = [
    {"id": "ga4",         "provider": "Google Analytics 4",  "category": "Analytics",  "capabilities": ["traffic", "conversions", "goals"]},
    {"id": "gsc",         "provider": "Google Search Console","category": "SEO",        "capabilities": ["impressions", "clicks", "keywords"]},
    {"id": "linkedin",    "provider": "LinkedIn",             "category": "Social",     "capabilities": ["publish", "analytics"]},
    {"id": "twitter_x",  "provider": "X (Twitter)",          "category": "Social",     "capabilities": ["publish", "analytics"]},
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

@router.post("/{integration_id}/connect")
def connect_integration(
    integration_id: str,
    credentials: Dict[str, Any] = Body(...),
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    if not any(item["id"] == integration_id for item in INTEGRATION_CATALOG):
        raise HTTPException(status_code=404, detail="Integration provider not found")
        
    integ = db.query(Integration).filter(Integration.brand_id == brand.id, Integration.provider == integration_id).first()
    if not integ:
        integ = Integration(
            brand_id=brand.id,
            provider=integration_id,
            credentials=credentials,
            status="CONNECTED"
        )
        db.add(integ)
    else:
        integ.credentials = credentials
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
