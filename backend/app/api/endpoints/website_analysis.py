import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

from app.api import deps
from app.models.all_models import Brand, WebsiteAnalysis
from app.services.website_analysis import WebsiteAnalysisService, SSRFProtectionError

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
    except SSRFProtectionError as e:
        analysis.status = "FAILED"
        analysis.errors = {"message": "Invalid or unsafe URL"}
    except Exception as e:
        analysis.status = "FAILED"
        analysis.errors = {"message": "Failed to analyze website"}
    finally:
        db.commit()

@router.get("/{brand_id}/website-analysis", response_model=WebsiteAnalysisResponse)
def get_website_analysis(
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
def trigger_website_analysis(
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
        
    analysis.status = "QUEUED"
    analysis.url = brand.website_url
    db.commit()
    db.refresh(analysis)
    
    # Run in background to not block the request
    background_tasks.add_task(_run_analysis_task, analysis.id, brand.website_url, db)
    
    return analysis
