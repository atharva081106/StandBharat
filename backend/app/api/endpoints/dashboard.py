from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.dashboard import DashboardResponse, KPI, ActivityEventResponse
from app.schemas.opportunity import OpportunityResponse
from app.models.all_models import Brand, Opportunity, MetricSnapshot, ActivityEvent
from typing import List

router = APIRouter()

@router.get("/command-center", response_model=DashboardResponse)
def get_command_center(
    db: Session = Depends(deps.get_db),
    brand: Brand = Depends(deps.get_current_brand)
):
    opportunities = db.query(Opportunity).filter(
        Opportunity.workspace_id == brand.workspace_id,
        Opportunity.brand_id == brand.id,
        Opportunity.status != "DISMISSED"
    ).order_by(Opportunity.priority.desc()).limit(5).all()
    
    recent_activity = db.query(ActivityEvent).filter(
        ActivityEvent.workspace_id == brand.workspace_id,
        ActivityEvent.brand_id == brand.id
    ).order_by(ActivityEvent.created_at.desc()).limit(10).all()
    
    # We will generate static NO_DATA kpis for now to preserve the UI design while remaining honest.
    kpis = [
        KPI(label="Revenue (AI Attributed)", value="NO_DATA", change="0%", trend="up"),
        KPI(label="Leads Generated", value="NO_DATA", change="0", trend="up"),
        KPI(label="Avg Conversion Rate", value="NO_DATA", change="0%", trend="up"),
        KPI(label="AI Spend (Est)", value="NO_DATA", change="0%", trend="down")
    ]
    
    return DashboardResponse(
        kpis=kpis,
        opportunities=[OpportunityResponse.model_validate(o) for o in opportunities],
        recent_activity=[ActivityEventResponse.model_validate(a) for a in recent_activity],
        system_status="Operational"
    )
