import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class PerformanceSnapshot(Base):
    __tablename__ = "performance_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id"), nullable=False, index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brand.id"), nullable=False, index=True)
    
    publication_id = Column(UUID(as_uuid=True), ForeignKey("publications.id"), nullable=True, index=True)
    
    channel = Column(String, nullable=False, index=True) # e.g. "linkedin"
    external_post_id = Column(String, nullable=True, index=True)
    
    captured_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, index=True)
    
    # Core metrics (nullable for those not supported by channel)
    impressions = Column(Integer, nullable=True)
    reach = Column(Integer, nullable=True)
    engagements = Column(Integer, nullable=True)
    likes = Column(Integer, nullable=True)
    comments = Column(Integer, nullable=True)
    shares = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=True)
    video_views = Column(Integer, nullable=True)
    saves = Column(Integer, nullable=True)
    
    engagement_rate = Column(Float, nullable=True)
    
    raw_payload = Column(JSON, nullable=True)
    
    source = Column(String, nullable=False) # e.g. "linkedin_api", "google_analytics"
    source_status = Column(String, nullable=False, default="SUCCESS") # SUCCESS, PARTIAL, ERROR
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Note: Define relationship in Publication if needed
