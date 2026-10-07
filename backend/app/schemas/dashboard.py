from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
import uuid
from .opportunity import OpportunityResponse

class KPI(BaseModel):
    label: str
    value: str
    change: str
    trend: str # e.g. "up" or "down"
    
class ActivityEventResponse(BaseModel):
    id: uuid.UUID
    type: str
    description: str
    metadata_json: Optional[dict] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DashboardResponse(BaseModel):
    kpis: List[KPI]
    opportunities: List[OpportunityResponse]
    recent_activity: List[ActivityEventResponse]
    system_status: str # e.g. "Operational", "Degraded"
