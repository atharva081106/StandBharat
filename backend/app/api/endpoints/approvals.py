from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import datetime

from app.db.session import get_db
from app.api.deps import get_current_user as get_current_active_user, get_current_workspace, get_current_brand
from app.core.authorization import check_workspace_role
from app.models.all_models import User, Workspace, Brand, ContentProject, ContentDraft, ContentApproval
from app.schemas.content import (
    ContentApprovalSubmit, ContentApprovalReview, ContentApprovalResponse
)

router = APIRouter()

@router.post("/projects/{id}/submit-review", response_model=ContentApprovalResponse)
def submit_for_review(
    id: UUID,
    submit_in: ContentApprovalSubmit,
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
        
    draft = db.query(ContentDraft).filter(
        ContentDraft.id == submit_in.content_draft_id,
        ContentDraft.content_project_id == project.id
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
        
    approval = ContentApproval(
        content_project_id=project.id,
        content_draft_id=draft.id,
        workspace_id=workspace_id,
        brand_id=brand.id,
        requested_by=current_user.id,
        status="PENDING"
    )
    db.add(approval)
    
    project.status = "IN_REVIEW"
    draft.status = "IN_REVIEW"
    
    db.commit()
    db.refresh(approval)
    return approval

@router.get("/approvals", response_model=List[ContentApprovalResponse])
def get_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR", "VIEWER"])
    workspace_id = workspace_ctx["workspace"].id
    
    return db.query(ContentApproval).filter(
        ContentApproval.workspace_id == workspace_id,
        ContentApproval.brand_id == brand.id
    ).order_by(ContentApproval.created_at.desc()).all()

@router.get("/approvals/{id}", response_model=ContentApprovalResponse)
def get_approval(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR", "VIEWER"])
    workspace_id = workspace_ctx["workspace"].id
    
    approval = db.query(ContentApproval).filter(
        ContentApproval.id == id,
        ContentApproval.workspace_id == workspace_id,
        ContentApproval.brand_id == brand.id
    ).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval

@router.post("/approvals/{id}/approve", response_model=ContentApprovalResponse)
def approve_content(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN"])
    workspace_id = workspace_ctx["workspace"].id
    
    approval = db.query(ContentApproval).filter(
        ContentApproval.id == id,
        ContentApproval.workspace_id == workspace_id,
        ContentApproval.brand_id == brand.id
    ).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    approval.status = "APPROVED"
    approval.reviewed_by = current_user.id
    approval.reviewed_at = datetime.datetime.utcnow()
    
    project = db.query(ContentProject).filter(ContentProject.id == approval.content_project_id).first()
    if project:
        project.status = "APPROVED"
        
    draft = db.query(ContentDraft).filter(ContentDraft.id == approval.content_draft_id).first()
    if draft:
        draft.status = "APPROVED"
        
    db.commit()
    db.refresh(approval)
    return approval

@router.post("/approvals/{id}/reject", response_model=ContentApprovalResponse)
def reject_content(
    id: UUID,
    review_in: ContentApprovalReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN"])
    workspace_id = workspace_ctx["workspace"].id
    
    approval = db.query(ContentApproval).filter(
        ContentApproval.id == id,
        ContentApproval.workspace_id == workspace_id,
        ContentApproval.brand_id == brand.id
    ).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    approval.status = "REJECTED"
    approval.reviewed_by = current_user.id
    approval.reviewed_at = datetime.datetime.utcnow()
    approval.review_comment = review_in.review_comment
    
    project = db.query(ContentProject).filter(ContentProject.id == approval.content_project_id).first()
    if project:
        project.status = "REJECTED"
        
    draft = db.query(ContentDraft).filter(ContentDraft.id == approval.content_draft_id).first()
    if draft:
        draft.status = "REJECTED"
        
    db.commit()
    db.refresh(approval)
    return approval

@router.post("/approvals/{id}/request-changes", response_model=ContentApprovalResponse)
def request_changes(
    id: UUID,
    review_in: ContentApprovalReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN"])
    workspace_id = workspace_ctx["workspace"].id
    
    approval = db.query(ContentApproval).filter(
        ContentApproval.id == id,
        ContentApproval.workspace_id == workspace_id,
        ContentApproval.brand_id == brand.id
    ).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    approval.status = "CHANGES_REQUESTED"
    approval.reviewed_by = current_user.id
    approval.reviewed_at = datetime.datetime.utcnow()
    approval.review_comment = review_in.review_comment
    
    project = db.query(ContentProject).filter(ContentProject.id == approval.content_project_id).first()
    if project:
        project.status = "DRAFTING"
        
    draft = db.query(ContentDraft).filter(ContentDraft.id == approval.content_draft_id).first()
    if draft:
        draft.status = "CHANGES_REQUESTED"
        
    db.commit()
    db.refresh(approval)
    return approval
