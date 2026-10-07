from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class ContentProjectBase(BaseModel):
    title: str
    objective: Optional[str] = None
    content_type: Optional[str] = None
    priority: Optional[int] = 0
    opportunity_id: Optional[UUID] = None

class ContentProjectCreate(ContentProjectBase):
    pass

class ContentProjectUpdate(BaseModel):
    title: Optional[str] = None
    objective: Optional[str] = None
    content_type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None

class ContentProjectResponse(ContentProjectBase):
    id: UUID
    workspace_id: UUID
    brand_id: UUID
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentBriefBase(BaseModel):
    title: str
    objective: Optional[str] = None
    target_audience: Optional[str] = None
    key_message: Optional[str] = None
    angle: Optional[str] = None
    content_type: Optional[str] = None
    tone: Optional[str] = None
    call_to_action: Optional[str] = None
    keywords: Optional[str] = None
    competitor_context: Optional[str] = None
    supporting_evidence: Optional[str] = None

class ContentBriefCreate(ContentBriefBase):
    pass

class ContentBriefUpdate(BaseModel):
    title: Optional[str] = None
    objective: Optional[str] = None
    target_audience: Optional[str] = None
    key_message: Optional[str] = None
    angle: Optional[str] = None
    content_type: Optional[str] = None
    tone: Optional[str] = None
    call_to_action: Optional[str] = None
    keywords: Optional[str] = None
    competitor_context: Optional[str] = None
    supporting_evidence: Optional[str] = None
    status: Optional[str] = None

class ContentBriefResponse(ContentBriefBase):
    id: UUID
    content_project_id: UUID
    workspace_id: UUID
    brand_id: UUID
    source_opportunity_id: Optional[UUID] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentDraftResponse(BaseModel):
    id: UUID
    content_project_id: UUID
    brief_id: Optional[UUID] = None
    workspace_id: UUID
    brand_id: UUID
    content_type: Optional[str] = None
    title: str
    body: str
    status: str
    generated_by: Optional[str] = None
    generation_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentVersionResponse(BaseModel):
    id: UUID
    content_draft_id: UUID
    version_number: int
    title: str
    body: str
    change_summary: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ContentApprovalSubmit(BaseModel):
    content_draft_id: UUID

class ContentApprovalReview(BaseModel):
    review_comment: Optional[str] = None

class ContentApprovalResponse(BaseModel):
    id: UUID
    content_project_id: UUID
    content_draft_id: UUID
    workspace_id: UUID
    brand_id: UUID
    requested_by: UUID
    reviewed_by: Optional[UUID] = None
    status: str
    review_comment: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
