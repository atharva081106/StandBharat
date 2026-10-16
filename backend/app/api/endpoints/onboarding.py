from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid
import logging

from app.api import deps
from app.models.all_models import (
    User, Workspace, WorkspaceMember, Brand,
    BrandVoice, Audience, Competitor, Goal, Positioning, UserRole
)

logger = logging.getLogger(__name__)

router = APIRouter()

class OnboardingStartPayload(BaseModel):
    businessName: str
    website: Optional[str] = ""

class OnboardingPayload(BaseModel):
    businessName: str
    website: str = ""
    description: str = ""
    valueProposition: str = ""
    brandVoice: List[str] = []
    targetDemographic: str = ""
    customerPainPoints: str = ""
    primaryObjective: str = ""
    targetRevenue: str = ""
    competitors: List[str] = []

@router.post("/start")
def start_onboarding(
    payload: OnboardingStartPayload,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Atomically ensures a Workspace and Brand exist for the authenticated user during onboarding.
    Returns the workspace and brand IDs so the frontend can immediately set headers and context.
    """
    try:
        # Check if user already belongs to any workspace
        member = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).first()
        if member:
            workspace = db.query(Workspace).filter(Workspace.id == member.workspace_id).first()
        else:
            workspace = None

        if not workspace:
            slug = payload.businessName.lower().strip().replace(" ", "-") + "-" + str(uuid.uuid4())[:8]
            workspace = Workspace(name=f"{payload.businessName} Workspace", slug=slug, owner_id=current_user.id)
            db.add(workspace)
            db.commit()
            db.refresh(workspace)

            member = WorkspaceMember(user_id=current_user.id, workspace_id=workspace.id, role=UserRole.OWNER)
            db.add(member)
            db.commit()

        # Find or create Brand in this workspace
        brand = db.query(Brand).filter(Brand.workspace_id == workspace.id).first()
        if not brand:
            brand = Brand(
                workspace_id=workspace.id,
                name=payload.businessName,
                website_url=payload.website or "",
                status="active"
            )
            db.add(brand)
            db.commit()
            db.refresh(brand)
        else:
            brand.name = payload.businessName
            if payload.website:
                brand.website_url = payload.website
            db.commit()
            db.refresh(brand)

        return {
            "status": "success",
            "workspace_id": str(workspace.id),
            "brand_id": str(brand.id),
            "workspace": {
                "id": str(workspace.id),
                "name": workspace.name,
                "slug": workspace.slug
            },
            "brand": {
                "id": str(brand.id),
                "name": brand.name,
                "website_url": brand.website_url
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error in start_onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete")
def complete_onboarding(
    payload: OnboardingPayload,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Saves the complete onboarding context into the database.
    Seamlessly resolves or creates the workspace and brand for current_user if headers are missing.
    """
    try:
        # 1. Resolve Workspace
        header_ws_id = request.headers.get("X-Workspace-ID")
        workspace = None
        if header_ws_id:
            try:
                ws_uuid = uuid.UUID(header_ws_id)
                member = db.query(WorkspaceMember).filter(
                    WorkspaceMember.user_id == current_user.id,
                    WorkspaceMember.workspace_id == ws_uuid
                ).first()
                if member:
                    workspace = db.query(Workspace).filter(Workspace.id == ws_uuid).first()
            except Exception:
                pass

        if not workspace:
            member = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).first()
            if member:
                workspace = db.query(Workspace).filter(Workspace.id == member.workspace_id).first()

        if not workspace:
            slug = payload.businessName.lower().strip().replace(" ", "-") + "-" + str(uuid.uuid4())[:8]
            workspace = Workspace(name=f"{payload.businessName} Workspace", slug=slug, owner_id=current_user.id)
            db.add(workspace)
            db.commit()
            db.refresh(workspace)

            member = WorkspaceMember(user_id=current_user.id, workspace_id=workspace.id, role=UserRole.OWNER)
            db.add(member)
            db.commit()

        # 2. Resolve Brand
        header_brand_id = request.headers.get("X-Brand-ID")
        brand = None
        if header_brand_id:
            try:
                brand_uuid = uuid.UUID(header_brand_id)
                brand = db.query(Brand).filter(
                    Brand.id == brand_uuid,
                    Brand.workspace_id == workspace.id
                ).first()
            except Exception:
                pass

        if not brand:
            brand = db.query(Brand).filter(Brand.workspace_id == workspace.id).first()

        if not brand:
            brand = Brand(
                workspace_id=workspace.id,
                name=payload.businessName,
                website_url=payload.website or "",
                status="active"
            )
            db.add(brand)
            db.commit()
            db.refresh(brand)

        # 3. Update Brand basic details
        brand.name = payload.businessName
        brand.website_url = payload.website
        brand.tagline = payload.description
        brand.mission = payload.valueProposition
        brand.target_audience = payload.targetDemographic
        brand.status = "active"
        
        # 4. Create/Update Brand Voice
        voice = db.query(BrandVoice).filter(BrandVoice.brand_id == brand.id).first()
        if not voice:
            voice = BrandVoice(brand_id=brand.id)
            db.add(voice)
        voice.personality = ", ".join(payload.brandVoice) if payload.brandVoice else "Professional"
        voice.formality = "Professional" if "Professional" in payload.brandVoice else "Casual"
        voice.tone = ", ".join(payload.brandVoice) if payload.brandVoice else "Empathetic, Authoritative"

        # 5. Create/Update Audience
        audience = db.query(Audience).filter(Audience.brand_id == brand.id).first()
        if not audience:
            audience = Audience(brand_id=brand.id, name=payload.targetDemographic or "Target Audience")
            db.add(audience)
        audience.name = payload.targetDemographic or "Target Audience"
        audience.demographics = payload.targetDemographic or ""
        audience.pain_points = payload.customerPainPoints or ""

        # 6. Create/Update Goal
        goal = db.query(Goal).filter(Goal.brand_id == brand.id).first()
        if not goal:
            goal = Goal(brand_id=brand.id, goal=payload.primaryObjective or "Accelerate Business Growth")
            db.add(goal)
        goal.goal = payload.primaryObjective or "Accelerate Business Growth"
        goal.target_value = payload.targetRevenue or ""

        # 7. Create/Update Positioning
        positioning = db.query(Positioning).filter(Positioning.brand_id == brand.id).first()
        if not positioning:
            positioning = Positioning(brand_id=brand.id)
            db.add(positioning)
        positioning.unique_value_proposition = payload.valueProposition or payload.description or ""
        
        # 8. Create/Update Competitors
        db.query(Competitor).filter(Competitor.brand_id == brand.id).delete()
        for comp_name in payload.competitors:
            cleaned = comp_name.strip()
            if cleaned:
                comp = Competitor(brand_id=brand.id, name=cleaned)
                db.add(comp)

        db.commit()
        db.refresh(brand)
        db.refresh(workspace)

        # Queue website analysis and strategy bootstrap using Celery (optional background task)
        try:
            from app.worker import celery_app
            celery_app.send_task("app.worker.tasks.initialize_brand_system", args=[str(brand.id)])
        except Exception as ce:
            logger.warning(f"Celery task dispatch skipped or failed: {ce}")

        return {
            "status": "success",
            "message": "Onboarding completed successfully",
            "workspace_id": str(workspace.id),
            "brand_id": str(brand.id),
            "workspace": {
                "id": str(workspace.id),
                "name": workspace.name,
                "slug": workspace.slug
            },
            "brand": {
                "id": str(brand.id),
                "name": brand.name,
                "website_url": brand.website_url,
                "tagline": brand.tagline,
                "mission": brand.mission
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error completing onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))
