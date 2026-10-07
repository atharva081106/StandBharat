from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class OrchestratorConfigResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    brand_id: UUID
    mode: str
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]

    class Config:
        from_attributes = True

class OrchestrationRunResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    brand_id: UUID
    trigger_type: str
    status: str
    decision: str
    agent_id: Optional[str]
    reason: str
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class OrchestratorUpdateRequest(BaseModel):
    mode: str
