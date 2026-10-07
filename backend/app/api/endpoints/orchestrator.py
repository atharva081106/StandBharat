from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_workspace, get_current_brand
from app.models.all_models import Workspace, Brand, OrchestratorConfig
from app.orchestrator.schemas import OrchestratorConfigResponse, OrchestrationRunResponse, OrchestratorUpdateRequest
from app.orchestrator.service import orchestrator_service

router = APIRouter()

@router.get("/status", response_model=OrchestratorConfigResponse)
def get_status(
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    config = orchestrator_service.get_config(db, brand.id)
    if not config:
        config = orchestrator_service.update_config(db, brand.id, workspace["workspace"].id, "OFF")
    return config

@router.patch("/status", response_model=OrchestratorConfigResponse)
def update_status(
    req: OrchestratorUpdateRequest,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    if req.mode not in ["OFF", "ASSISTED", "AUTONOMOUS"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    config = orchestrator_service.update_config(db, brand.id, workspace["workspace"].id, req.mode)
    return config

@router.get("/runs", response_model=List[OrchestrationRunResponse])
def get_runs(
    limit: int = 50,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    return orchestrator_service.get_runs(db, brand.id, limit)

@router.post("/tick")
def manual_tick(
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    config = orchestrator_service.get_config(db, brand.id)
    if not config:
        config = orchestrator_service.update_config(db, brand.id, workspace["workspace"].id, "OFF")
        
    orchestrator_service.tick(db, config)
    return {"status": "success"}
