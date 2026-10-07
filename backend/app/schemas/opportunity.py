from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class OpportunityBase(BaseModel):
    title: str
    description: Optional[str] = None
    impact: Optional[str] = None
    confidence: Optional[str] = None
    effort: Optional[str] = None
    priority: Optional[int] = 0
    status: Optional[str] = "NEW"
    source: Optional[str] = None

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    impact: Optional[str] = None
    confidence: Optional[str] = None
    effort: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    source: Optional[str] = None

class OpportunityResponse(OpportunityBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    brand_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
