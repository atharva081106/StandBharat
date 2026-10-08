from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.api.deps import get_db, get_current_workspace, get_current_brand
from app.models.all_models import Brand, BrandVoice, Audience, Competitor, Goal, Positioning
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class OnboardingPayload(BaseModel):
    businessName: str
    website: str
    description: str
    valueProposition: str
    brandVoice: List[str]
    targetDemographic: str
    customerPainPoints: str
    primaryObjective: str
    targetRevenue: str
    competitors: List[str]

@router.post("/complete")
def complete_onboarding(
    payload: OnboardingPayload,
    db: Session = Depends(get_db),
    brand: Brand = Depends(get_current_brand)
):
    try:
        # 1. Update Brand basic details
        brand.name = payload.businessName
        brand.website_url = payload.website
        brand.tagline = payload.description
        brand.mission = payload.valueProposition
        
        # 2. Create/Update Brand Voice
        voice = db.query(BrandVoice).filter(BrandVoice.brand_id == brand.id).first()
        if not voice:
            voice = BrandVoice(brand_id=brand.id)
            db.add(voice)
        voice.personality = ", ".join(payload.brandVoice)
        voice.formality = "Professional" if "Professional" in payload.brandVoice else "Casual"
        voice.tone = ", ".join(payload.brandVoice)

        # 3. Create/Update Audience
        audience = db.query(Audience).filter(Audience.brand_id == brand.id).first()
        if not audience:
            audience = Audience(brand_id=brand.id, name=payload.targetDemographic)
            db.add(audience)
        audience.name = payload.targetDemographic
        audience.demographics = payload.targetDemographic
        audience.pain_points = payload.customerPainPoints

        # 4. Create/Update Goal
        goal = db.query(Goal).filter(Goal.brand_id == brand.id).first()
        if not goal:
            goal = Goal(brand_id=brand.id, goal=payload.primaryObjective)
            db.add(goal)
        goal.goal = payload.primaryObjective
        goal.target_value = payload.targetRevenue

        # 5. Create/Update Positioning
        positioning = db.query(Positioning).filter(Positioning.brand_id == brand.id).first()
        if not positioning:
            positioning = Positioning(brand_id=brand.id)
            db.add(positioning)
        positioning.unique_value_proposition = payload.valueProposition
        
        # 6. Create/Update Competitors
        # Clear existing competitors to keep it idempotent based on frontend state
        db.query(Competitor).filter(Competitor.brand_id == brand.id).delete()
        for comp_name in payload.competitors:
            if comp_name.strip():
                comp = Competitor(brand_id=brand.id, name=comp_name.strip())
                db.add(comp)

        db.commit()

        # TODO: Queue website analysis and strategy bootstrap using Celery
        from app.worker import celery_app
        celery_app.send_task("app.worker.tasks.initialize_brand_system", args=[str(brand.id)])

        return {"status": "success", "message": "Onboarding completed successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error completing onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))
