from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.api.deps import get_current_brand, get_current_user
from app.models.all_models import Brand, User, AgentRun
from app.db.session import SessionLocal
import uuid

router = APIRouter()

@router.get("/")
def list_agent_runs(
    agent_id: Optional[str] = None,
    brand: Brand = Depends(get_current_brand),
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        query = db.query(AgentRun).filter(AgentRun.brand_id == brand.id)
        if agent_id:
            query = query.filter(AgentRun.agent_id == agent_id)
        
        runs = query.order_by(AgentRun.created_at.desc()).all()
        return [{
            "id": str(r.id),
            "agent_id": r.agent_id,
            "status": r.status,
            "result_data": r.output,
            "error_message": r.error,
            "created_at": r.created_at
        } for r in runs]
    finally:
        db.close()

@router.get("/{run_id}")
def get_agent_run(
    run_id: str,
    brand: Brand = Depends(get_current_brand),
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        run = db.query(AgentRun).filter(
            AgentRun.id == uuid.UUID(run_id),
            AgentRun.brand_id == brand.id
        ).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
            
        return {
            "id": str(run.id),
            "agent_id": run.agent_id,
            "status": run.status,
            "result_data": run.output,
            "error_message": run.error,
            "created_at": run.created_at
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run ID")
    finally:
        db.close()
