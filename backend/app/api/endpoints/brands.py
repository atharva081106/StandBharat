from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.brand import BrandCreate, BrandResponse
from app.models.all_models import Brand, WorkspaceMember, User
import uuid

router = APIRouter()

@router.post("/", response_model=BrandResponse)
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(deps.get_db),
    context: dict = Depends(deps.get_current_workspace)
):
    if str(brand_in.workspace_id) != str(context["workspace"].id):
        raise HTTPException(status_code=400, detail="Brand workspace does not match context")
        
    brand = Brand(**brand_in.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

@router.get("/", response_model=list[BrandResponse])
def get_brands(
    db: Session = Depends(deps.get_db),
    context: dict = Depends(deps.get_current_workspace)
):
    brands = db.query(Brand).filter(Brand.workspace_id == context["workspace"].id).all()
    return brands

@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand: Brand = Depends(deps.get_current_brand)
):
    return brand

@router.patch("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_in: dict, # Simplified for demo
    brand: Brand = Depends(deps.get_current_brand),
    db: Session = Depends(deps.get_db),
    context: dict = Depends(deps.require_role(["OWNER", "ADMIN"]))
):
    for field in ["name", "website_url", "description", "industry", "category", "location", "mission", "vision", "values", "tagline", "status"]:
        if field in brand_in:
            setattr(brand, field, brand_in[field])
    db.commit()
    db.refresh(brand)
    return brand

@router.get("/{brand_id}/workflow-status")
def get_workflow_status(
    brand_id: str,
    brand: Brand = Depends(deps.get_current_brand),
    db: Session = Depends(deps.get_db)
):
    if str(brand_id) != str(brand.id):
        raise HTTPException(status_code=403, detail="Path brand_id does not match authorized context")
        
    from app.models.all_models import WebsiteAnalysis, BrandStrategy, StrategyDocument
    
    analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.brand_id == brand.id).first()
    strategy = db.query(BrandStrategy).filter(BrandStrategy.brand_id == brand.id).first()
    documents = db.query(StrategyDocument).filter(StrategyDocument.brand_id == brand.id).all()
    
    import os
    from datetime import datetime, timedelta, timezone
    
    try:
        stale_timeout_mins = int(os.environ.get("STALE_WORKFLOW_TIMEOUT_MINUTES", "10"))
        if stale_timeout_mins <= 0:
            stale_timeout_mins = 10
    except ValueError:
        stale_timeout_mins = 10
        
    stale_threshold = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=stale_timeout_mins)
    
    analysis_status = analysis.status if analysis else "NOT_CONFIGURED"
    
    # Self-healing for stale analysis tasks
    if analysis and analysis_status in ("QUEUED", "RUNNING"):
        updated_naive = analysis.updated_at.replace(tzinfo=None) if analysis.updated_at.tzinfo else analysis.updated_at
        if updated_naive < stale_threshold:
            rows = db.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.id == analysis.id,
                WebsiteAnalysis.status.in_(["QUEUED", "RUNNING"])
            ).update({
                "status": "FAILED",
                "errors": {"message": "Task stalled and timed out (Worker/Broker failure)"}
            }, synchronize_session=False)
            db.commit()
            if rows > 0:
                analysis_status = "FAILED"
            else:
                db.refresh(analysis)
                analysis_status = analysis.status
    
    strategy_status = "NOT_CONFIGURED"
    if strategy and strategy.business_strategy:
        if strategy.business_strategy in ("PARTIAL", "FAILED", "NOT_CONFIGURED", "QUEUED", "RUNNING"):
            # Self-healing for stale strategy tasks
            if strategy.business_strategy in ("QUEUED", "RUNNING"):
                updated_naive = strategy.updated_at.replace(tzinfo=None) if strategy.updated_at.tzinfo else strategy.updated_at
                if updated_naive < stale_threshold:
                    rows = db.query(BrandStrategy).filter(
                        BrandStrategy.id == strategy.id,
                        BrandStrategy.business_strategy.in_(["QUEUED", "RUNNING"])
                    ).update({
                        "business_strategy": "FAILED"
                    }, synchronize_session=False)
                    db.commit()
                    if rows > 0:
                        strategy_status = "FAILED"
                    else:
                        db.refresh(strategy)
                        strategy_status = strategy.business_strategy
                else:
                    strategy_status = strategy.business_strategy
            else:
                strategy_status = strategy.business_strategy
        else:
            strategy_status = "COMPLETED"
    
    overall_status = "NOT_STARTED"
    if analysis_status == "FAILED" or strategy_status == "FAILED":
        overall_status = "FAILED"
    elif analysis_status in ("QUEUED", "RUNNING") or strategy_status in ("QUEUED", "RUNNING"):
        overall_status = "PROCESSING"
    elif analysis_status == "COMPLETED" and strategy_status == "COMPLETED":
        overall_status = "COMPLETED"
    elif analysis_status == "COMPLETED" and strategy_status == "NOT_CONFIGURED":
        overall_status = "NOT_CONFIGURED"
        
    return {
        "website_analysis": analysis_status,
        "brand_strategy": strategy_status,
        "documents_generated": len(documents),
        "overall_status": overall_status
    }

