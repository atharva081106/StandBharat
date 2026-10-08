from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Any
import uuid

from app.api.deps import get_db, get_current_brand
from app.models.all_models import Brand, Campaign
from pydantic import BaseModel

router = APIRouter()

class CampaignResponse(BaseModel):
    id: str
    workspace_id: str
    brand_id: str
    name: str
    description: str | None
    status: str
    budget: float | None
    spent: float | None
    start_date: str | None
    end_date: str | None
    
    class Config:
        orm_mode = True

@router.get("/", response_model=List[CampaignResponse])
def get_campaigns(
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    campaigns = db.query(Campaign).filter(Campaign.brand_id == brand.id).all()
    return [{
        "id": str(c.id),
        "workspace_id": str(c.workspace_id),
        "brand_id": str(c.brand_id),
        "name": c.name,
        "description": c.description,
        "status": c.status,
        "budget": c.budget,
        "spent": c.spent,
        "start_date": c.start_date.isoformat() if c.start_date else None,
        "end_date": c.end_date.isoformat() if c.end_date else None
    } for c in campaigns]

@router.post("/")
def create_campaign(
    payload: dict = Body(...),
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    c = Campaign(
        workspace_id=brand.workspace_id,
        brand_id=brand.id,
        name=payload.get("name"),
        description=payload.get("description"),
        status=payload.get("status", "DRAFT")
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": str(c.id), "status": "SUCCESS"}
