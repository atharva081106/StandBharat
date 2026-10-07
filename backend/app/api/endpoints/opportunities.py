from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunityResponse
from app.models.all_models import Opportunity, Brand
import uuid

router = APIRouter()

@router.get("/", response_model=list[OpportunityResponse])
def get_opportunities(
    db: Session = Depends(deps.get_db),
    brand: Brand = Depends(deps.get_current_brand)
):
    opportunities = db.query(Opportunity).filter(
        Opportunity.workspace_id == brand.workspace_id,
        Opportunity.brand_id == brand.id
    ).order_by(Opportunity.priority.desc(), Opportunity.created_at.desc()).all()
    return opportunities

@router.get("/{id}", response_model=OpportunityResponse)
def get_opportunity(
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    brand: Brand = Depends(deps.get_current_brand)
):
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == id,
        Opportunity.workspace_id == brand.workspace_id,
        Opportunity.brand_id == brand.id
    ).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

@router.post("/", response_model=OpportunityResponse)
def create_opportunity(
    opportunity_in: OpportunityCreate,
    db: Session = Depends(deps.get_db),
    brand: Brand = Depends(deps.get_current_brand)
):
    opportunity = Opportunity(
        **opportunity_in.model_dump(),
        workspace_id=brand.workspace_id,
        brand_id=brand.id
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity

@router.patch("/{id}", response_model=OpportunityResponse)
def update_opportunity(
    id: uuid.UUID,
    opportunity_in: OpportunityUpdate,
    db: Session = Depends(deps.get_db),
    brand: Brand = Depends(deps.get_current_brand)
):
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == id,
        Opportunity.workspace_id == brand.workspace_id,
        Opportunity.brand_id == brand.id
    ).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    update_data = opportunity_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opportunity, field, value)
        
    db.commit()
    db.refresh(opportunity)
    return opportunity

@router.delete("/{id}")
def delete_opportunity(
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    brand: Brand = Depends(deps.get_current_brand)
):
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == id,
        Opportunity.workspace_id == brand.workspace_id,
        Opportunity.brand_id == brand.id
    ).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    db.delete(opportunity)
    db.commit()
    return {"message": "Opportunity deleted"}
