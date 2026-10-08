from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import datetime

from app.db.session import get_db
from app.api.deps import get_current_user as get_current_active_user, get_current_workspace, get_current_brand
from app.core.authorization import check_workspace_role
from app.models.all_models import User, Workspace, Brand, ContentProject, ContentBrief, ContentDraft, ContentVersion, ContentApproval, AgentTask, AgentRun
from app.schemas.content import (
    ContentProjectCreate, ContentProjectUpdate, ContentProjectResponse,
    ContentBriefCreate, ContentBriefResponse, ContentDraftResponse,
    ContentVersionResponse
)

router = APIRouter()

@router.post("/projects", response_model=ContentProjectResponse)
def create_content_project(
    project_in: ContentProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR"])
    workspace_id = workspace_ctx["workspace"].id
    
    project = ContentProject(
        workspace_id=workspace_id,
        brand_id=brand.id,
        title=project_in.title,
        objective=project_in.objective,
        content_type=project_in.content_type,
        priority=project_in.priority,
        opportunity_id=project_in.opportunity_id,
        created_by=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/projects", response_model=List[ContentProjectResponse])
def get_content_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR", "VIEWER"])
    workspace_id = workspace_ctx["workspace"].id
    
    return db.query(ContentProject).filter(
        ContentProject.workspace_id == workspace_id,
        ContentProject.brand_id == brand.id
    ).order_by(ContentProject.created_at.desc()).all()

@router.get("/projects/{id}", response_model=ContentProjectResponse)
def get_xxx_content_project(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR", "VIEWER"])
    workspace_id = workspace_ctx["workspace"].id
    
    project = db.query(ContentProject).filter(
        ContentProject.id == id,
        ContentProject.workspace_id == workspace_id,
        ContentProject.brand_id == brand.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Content project not found")
    return project

@router.patch("/projects/{id}", response_model=ContentProjectResponse)
def update_content_project(
    id: UUID,
    project_in: ContentProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR"])
    workspace_id = workspace_ctx["workspace"].id
    
    project = db.query(ContentProject).filter(
        ContentProject.id == id,
        ContentProject.workspace_id == workspace_id,
        ContentProject.brand_id == brand.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Content project not found")
        
    for field, value in project_in.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
        
    db.commit()
    db.refresh(project)
    return project

@router.post("/projects/{id}/brief", response_model=ContentBriefResponse)
def create_content_brief(
    id: UUID,
    brief_in: ContentBriefCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR"])
    workspace_id = workspace_ctx["workspace"].id
    
    project = db.query(ContentProject).filter(
        ContentProject.id == id,
        ContentProject.workspace_id == workspace_id,
        ContentProject.brand_id == brand.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Content project not found")
        
    brief = ContentBrief(
        content_project_id=project.id,
        workspace_id=workspace_id,
        brand_id=brand.id,
        source_opportunity_id=project.opportunity_id,
        **brief_in.model_dump()
    )
    db.add(brief)
    db.commit()
    db.refresh(brief)
    return brief

@router.get("/projects/{id}/brief", response_model=ContentBriefResponse)
def get_xxx_content_brief(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR", "VIEWER"])
    workspace_id = workspace_ctx["workspace"].id
    
    project = db.query(ContentProject).filter(
        ContentProject.id == id,
        ContentProject.workspace_id == workspace_id,
        ContentProject.brand_id == brand.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Content project not found")
        
    brief = db.query(ContentBrief).filter(
        ContentBrief.content_project_id == project.id
    ).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Content brief not found")
    return brief

@router.post("/projects/{id}/generate")
def generate_content_draft(
    id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR"])
    workspace_id = workspace_ctx["workspace"].id
    
    project = db.query(ContentProject).filter(
        ContentProject.id == id,
        ContentProject.workspace_id == workspace_id,
        ContentProject.brand_id == brand.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Content project not found")
        
    brief = db.query(ContentBrief).filter(
        ContentBrief.content_project_id == project.id
    ).first()
    if not brief:
        raise HTTPException(status_code=400, detail="Cannot generate draft without a brief")
        
    # Create AgentTask for ContentWriterAgent
    task = AgentTask(
        workspace_id=workspace_id,
        brand_id=brand.id,
        agent_type="content_writer",
        task_type="GENERATE_DRAFT",
        status="QUEUED",
        input_data={"brief_id": str(brief.id)},
        created_by=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    run = AgentRun(
        workspace_id=workspace_id,
        brand_id=brand.id,
        agent_type="content_writer",
        task_id=task.id,
        status="QUEUED"
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    # Send to Celery
    from app.core.celery_app import celery_app
    celery_app.send_task("app.worker.execute_agent_task", args=[str(task.id), str(run.id)])
    
    return {"message": "Draft generation started", "task_id": str(task.id)}

@router.get("/projects/{id}/drafts", response_model=List[ContentDraftResponse])
def get_xxx_project_drafts(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR", "VIEWER"])
    workspace_id = workspace_ctx["workspace"].id
    
    return db.query(ContentDraft).filter(
        ContentDraft.content_project_id == id,
        ContentDraft.workspace_id == workspace_id,
        ContentDraft.brand_id == brand.id
    ).order_by(ContentDraft.created_at.desc()).all()

@router.get("/drafts/{id}", response_model=ContentDraftResponse)
def get_xxx_content_draft(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR", "VIEWER"])
    workspace_id = workspace_ctx["workspace"].id
    
    draft = db.query(ContentDraft).filter(
        ContentDraft.id == id,
        ContentDraft.workspace_id == workspace_id,
        ContentDraft.brand_id == brand.id
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

@router.get("/drafts/{id}/versions", response_model=List[ContentVersionResponse])
def get_xxx_draft_versions(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR", "VIEWER"])
    workspace_id = workspace_ctx["workspace"].id
    
    draft = db.query(ContentDraft).filter(
        ContentDraft.id == id,
        ContentDraft.workspace_id == workspace_id,
        ContentDraft.brand_id == brand.id
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
        
    return db.query(ContentVersion).filter(
        ContentVersion.content_draft_id == id
    ).order_by(ContentVersion.version_number.desc()).all()
