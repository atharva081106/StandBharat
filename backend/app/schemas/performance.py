from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class PerformanceSnapshotSchema(BaseModel):
    id: UUID
    publication_id: Optional[UUID]
    channel: str
    captured_at: datetime
    
    impressions: Optional[int]
    reach: Optional[int]
    engagements: Optional[int]
    likes: Optional[int]
    comments: Optional[int]
    shares: Optional[int]
    clicks: Optional[int]
    video_views: Optional[int]
    saves: Optional[int]
    engagement_rate: Optional[float]
    
    source_status: str
    
    model_config = {"from_attributes": True}

class PerformanceSummaryResponse(BaseModel):
    status: str # AVAILABLE, NOT_AVAILABLE, PARTIAL
    reason: Optional[str] = None
    period: Dict[str, Any]
    channels: List[str]
    metrics: Dict[str, Any]
    top_publications: List[PerformanceSnapshotSchema]
    trends: List[Dict[str, Any]]
