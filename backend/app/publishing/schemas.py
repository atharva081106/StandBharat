from pydantic import ConfigDict, BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class PublisherConnectionBase(BaseModel):
    platform: str
    status: str
    external_account_id: Optional[str] = None
    external_account_name: Optional[str] = None
    scopes: Optional[List[str]] = None
    last_validated_at: Optional[datetime] = None

class PublisherConnectionResponse(PublisherConnectionBase):
    id: UUID
    workspace_id: UUID
    brand_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PublicationAttemptResponse(BaseModel):
    id: UUID
    publication_id: UUID
    attempt_number: str
    status: str
    request_metadata: Optional[Dict[str, Any]] = None
    response_metadata: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PublicationBase(BaseModel):
    platform: str
    content_project_id: UUID
    content_draft_id: UUID
    status: str
    external_post_id: Optional[str] = None
    published_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    idempotency_key: str

class PublicationResponse(PublicationBase):
    id: UUID
    workspace_id: UUID
    brand_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    attempts: Optional[List[PublicationAttemptResponse]] = []

    model_config = ConfigDict(from_attributes=True)

class OAuthConnectResponse(BaseModel):
    authorization_url: str

class OAuthCallbackRequest(BaseModel):
    code: str
    state: str

class PublishRequest(BaseModel):
    pass # No body needed currently, draft_id is in URL

class ReconcilePublicationRequest(BaseModel):
    resolution: str
    external_post_id: Optional[str] = None
    notes: Optional[str] = None
