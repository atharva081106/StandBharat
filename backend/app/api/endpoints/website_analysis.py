import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

from app.api import deps
from app.models.all_models import Brand, WebsiteAnalysis
from app.services.website_analysis import WebsiteAnalysisService, SSRFProtectionError
from app.workers.celery_worker import generate_core_brand_strategy
from app.core.limiter import limiter
from starlette.requests import Request

router = APIRouter()

class WebsiteAnalysisResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    brand_id: uuid.UUID
    status: str
    url: Optional[str] = None
    result_metadata: Optional[Dict[str, Any]] = None
    analysis_results: Optional[Dict[str, Any]] = None
    errors: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

async def _run_analysis_task(analysis_id: uuid.UUID, url: str, db: Session):
    analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.id == analysis_id).first()
    if not analysis:
        return
        
    try:
        analysis.status = "RUNNING"
        db.commit()
        
        result = await WebsiteAnalysisService.analyze_url(url)
        
        analysis.result_metadata = result["metadata"]
        analysis.analysis_results = result["analysis_results"]
        analysis.status = "COMPLETED"
        analysis.errors = None
        
        # Pre-create BrandStrategy as QUEUED so UI knows it's processing before worker picks it up
        from app.models.all_models import BrandStrategy
        strategy = db.query(BrandStrategy).filter_by(brand_id=analysis.brand_id).first()
        if not strategy:
            strategy = BrandStrategy(brand_id=analysis.brand_id)
            db.add(strategy)
        strategy.business_strategy = "QUEUED"
        
        db.commit() # Commit the completed analysis and queued strategy before triggering the celery task
        generate_core_brand_strategy.delay(str(analysis.workspace_id), str(analysis.brand_id))
    except SSRFProtectionError as e:
        analysis.status = "FAILED"
        analysis.errors = {"message": "Invalid or unsafe URL"}
    except Exception as e:
        analysis.status = "FAILED"
        analysis.errors = {"message": "Failed to analyze website"}
    finally:
        # If strategy was created as QUEUED but dispatch failed (analysis is FAILED), mark it as FAILED
        if analysis.status == "FAILED":
            from app.models.all_models import BrandStrategy
            strategy = db.query(BrandStrategy).filter_by(brand_id=analysis.brand_id).first()
            if strategy and strategy.business_strategy == "QUEUED":
                strategy.business_strategy = "FAILED"
        db.commit()

@router.get("/{brand_id}/website-analysis", response_model=WebsiteAnalysisResponse)
@limiter.limit("20/minute")
def get_website_analysis(
    request: Request,
    brand: Brand = Depends(deps.get_current_brand),
    db: Session = Depends(deps.get_db)
):
    analysis = db.query(WebsiteAnalysis).filter(
        WebsiteAnalysis.brand_id == brand.id,
        WebsiteAnalysis.workspace_id == brand.workspace_id
    ).first()
    
    if not analysis:
        analysis = WebsiteAnalysis(
            workspace_id=brand.workspace_id,
            brand_id=brand.id,
            status="NOT_ANALYZED",
            url=brand.website_url
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
    return analysis

@router.post("/{brand_id}/website-analysis", response_model=WebsiteAnalysisResponse)
@limiter.limit("5/minute")
def trigger_website_analysis(
    request: Request,
    background_tasks: BackgroundTasks,
    brand: Brand = Depends(deps.get_current_brand),
    db: Session = Depends(deps.get_db)
):
    if not brand.website_url:
        raise HTTPException(status_code=400, detail="Brand has no website URL configured")
        
    analysis = db.query(WebsiteAnalysis).filter(
        WebsiteAnalysis.brand_id == brand.id,
        WebsiteAnalysis.workspace_id == brand.workspace_id
    ).first()
    
    if not analysis:
        analysis = WebsiteAnalysis(
            workspace_id=brand.workspace_id,
            brand_id=brand.id,
            url=brand.website_url
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
    if analysis.status in ("QUEUED", "RUNNING"):
        return analysis
        
    # If analysis is already completed, just trigger the next step
    if analysis.status == "COMPLETED" and analysis.analysis_results:
        from app.models.all_models import BrandStrategy
        strategy = db.query(BrandStrategy).filter_by(brand_id=analysis.brand_id).first()
        if not strategy:
            strategy = BrandStrategy(brand_id=analysis.brand_id)
            db.add(strategy)
        
        # Only dispatch if strategy is not actively running
        if strategy.business_strategy not in ("QUEUED", "RUNNING"):
            strategy.business_strategy = "QUEUED"
            db.commit()
            db.refresh(analysis)
            try:
                generate_core_brand_strategy.delay(str(analysis.workspace_id), str(analysis.brand_id))
            except Exception as e:
                strategy.business_strategy = "FAILED"
                db.commit()
        return analysis
        
    analysis.status = "QUEUED"
    analysis.url = brand.website_url
    db.commit()
    db.refresh(analysis)
    
    # Run in background to not block the request
    background_tasks.add_task(_run_analysis_task, analysis.id, brand.website_url, db)
    
    return analysis
