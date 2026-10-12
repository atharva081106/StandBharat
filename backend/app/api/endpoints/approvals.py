from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
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

def _enrich_approval_response(approval: ContentApproval, draft: Optional[ContentDraft] = None, project: Optional[ContentProject] = None) -> ContentApprovalResponse:
    resp = ContentApprovalResponse.model_validate(approval)
    if draft:
        resp.draft_title = draft.title
        resp.draft_type = draft.content_type
        resp.draft_body = draft.body
    if project:
        resp.project_title = project.title
    return resp

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
        ContentDraft.content_project_id == project.id,
        ContentDraft.workspace_id == workspace_id,
        ContentDraft.brand_id == brand.id
    ).with_for_update().first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
        
    # Check if there is already a pending approval for this draft
    existing_pending = db.query(ContentApproval).filter(
        ContentApproval.content_draft_id == draft.id,
        ContentApproval.workspace_id == workspace_id,
        ContentApproval.brand_id == brand.id,
        ContentApproval.status == "PENDING"
    ).first()
    if existing_pending:
        raise HTTPException(status_code=400, detail="An approval review is already pending for this draft")

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
    return _enrich_approval_response(approval, draft, project)

@router.get("", response_model=List[ContentApprovalResponse])
@router.get("/approvals", response_model=List[ContentApprovalResponse])
def get_approvals(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    workspace_ctx: dict = Depends(get_current_workspace),
    brand: Brand = Depends(get_current_brand)
):
    check_workspace_role(db, current_user.id, workspace_ctx["workspace"].id, ["OWNER", "ADMIN", "MARKETER", "EDITOR", "VIEWER"])
    workspace_id = workspace_ctx["workspace"].id
    
    query = db.query(
        ContentApproval,
        ContentDraft,
        ContentProject
    ).outerjoin(
        ContentDraft, ContentApproval.content_draft_id == ContentDraft.id
    ).outerjoin(
        ContentProject, ContentApproval.content_project_id == ContentProject.id
    ).filter(
        ContentApproval.workspace_id == workspace_id,
        ContentApproval.brand_id == brand.id
    )

    if status:
        query = query.filter(ContentApproval.status == status.upper())

    results = query.order_by(ContentApproval.created_at.desc()).all()
    
    approvals_list = []
    for approval, draft, project in results:
        approvals_list.append(_enrich_approval_response(approval, draft, project))
        
    return approvals_list

@router.get("/{id}", response_model=ContentApprovalResponse)
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
    
    result = db.query(
        ContentApproval,
        ContentDraft,
        ContentProject
    ).outerjoin(
        ContentDraft, ContentApproval.content_draft_id == ContentDraft.id
    ).outerjoin(
        ContentProject, ContentApproval.content_project_id == ContentProject.id
    ).filter(
        ContentApproval.id == id,
        ContentApproval.workspace_id == workspace_id,
        ContentApproval.brand_id == brand.id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    approval, draft, project = result
    return _enrich_approval_response(approval, draft, project)

@router.post("/{id}/approve", response_model=ContentApprovalResponse)
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
    ).with_for_update().first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    if approval.status == "APPROVED":
        raise HTTPException(status_code=400, detail="Approval is already approved")
    if approval.status == "REJECTED":
        raise HTTPException(status_code=400, detail="Cannot transition approval from REJECTED to APPROVED")
        
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
    return _enrich_approval_response(approval, draft, project)

@router.post("/{id}/reject", response_model=ContentApprovalResponse)
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
    ).with_for_update().first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    if approval.status == "REJECTED":
        raise HTTPException(status_code=400, detail="Approval is already rejected")
    if approval.status == "APPROVED":
        raise HTTPException(status_code=400, detail="Cannot transition approval from APPROVED to REJECTED")
        
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
    return _enrich_approval_response(approval, draft, project)

@router.post("/{id}/request-changes", response_model=ContentApprovalResponse)
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
    ).with_for_update().first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    if approval.status in ("APPROVED", "REJECTED"):
        raise HTTPException(status_code=400, detail=f"Cannot transition approval from {approval.status} to CHANGES_REQUESTED")
        
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
    return _enrich_approval_response(approval, draft, project)
