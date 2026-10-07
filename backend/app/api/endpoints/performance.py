from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import datetime

from app.api.deps import get_db, get_current_user
from app.models.all_models import User, WorkspaceMember, Brand, Workspace
from app.models.performance import PerformanceSnapshot
from app.schemas.performance import PerformanceSnapshotSchema, PerformanceSummaryResponse
from app.services.performance.service import PerformanceService

router = APIRouter()

def verify_brand_access(db: Session, user_id: UUID, workspace_id: UUID, brand_id: UUID):
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == user_id,
        WorkspaceMember.workspace_id == workspace_id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not authorized in this workspace")
        
    brand = db.query(Brand).filter(Brand.id == brand_id, Brand.workspace_id == workspace_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

@router.get("/{workspace_id}/{brand_id}/summary", response_model=PerformanceSummaryResponse)
async def get_performance_summary(
    workspace_id: UUID,
    brand_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_brand_access(db, current_user.id, workspace_id, brand_id)
    
    # Get latest snapshots
    snapshots = db.query(PerformanceSnapshot).filter(
        PerformanceSnapshot.workspace_id == workspace_id,
        PerformanceSnapshot.brand_id == brand_id
    ).order_by(PerformanceSnapshot.captured_at.desc()).limit(10).all()
    
    if not snapshots:
        return PerformanceSummaryResponse(
            status="NOT_AVAILABLE",
            reason="No performance data available yet",
            period={"start": datetime.datetime.utcnow(), "end": datetime.datetime.utcnow()},
            channels=[],
            metrics={},
            top_publications=[],
            trends=[]
        )
        
    # Aggregate (simple mock for the API response)
    channels = list(set([s.channel for s in snapshots]))
    total_impressions = sum([s.impressions or 0 for s in snapshots])
    total_engagements = sum([s.engagements or 0 for s in snapshots])
    
    return PerformanceSummaryResponse(
        status="AVAILABLE",
        period={"start": snapshots[-1].captured_at, "end": snapshots[0].captured_at},
        channels=channels,
        metrics={
            "total_impressions": total_impressions,
            "total_engagements": total_engagements
        },
        top_publications=[PerformanceSnapshotSchema.model_validate(s) for s in snapshots[:5]],
        trends=[]
    )

@router.post("/{workspace_id}/{brand_id}/sync/{publication_id}")
async def sync_publication(
    workspace_id: UUID,
    brand_id: UUID,
    publication_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_brand_access(db, current_user.id, workspace_id, brand_id)
    
    service = PerformanceService(db)
    snapshot = await service.sync_publication_performance(str(publication_id))
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="Could not sync publication performance. May not be published or missing credentials.")
        
    return {"status": "success", "snapshot_id": snapshot.id}
