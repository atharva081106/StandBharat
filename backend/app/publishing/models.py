import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class PublisherConnection(Base):
    __tablename__ = "publisher_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id"), nullable=False, index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brand.id"), nullable=False, index=True)
    
    platform = Column(String, nullable=False, index=True) # e.g. "linkedin"
    status = Column(String, nullable=False, default="NOT_CONNECTED") # CONNECTED, ERROR, REVOKED
    
    encrypted_credentials = Column(String, nullable=True)
    external_account_id = Column(String, nullable=True)
    external_account_name = Column(String, nullable=True)
    scopes = Column(JSON, nullable=True)
    
    last_validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id"), nullable=False, index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brand.id"), nullable=False, index=True)
    
    content_project_id = Column(UUID(as_uuid=True), ForeignKey("contentproject.id"), nullable=False)
    content_draft_id = Column(UUID(as_uuid=True), ForeignKey("contentdraft.id"), nullable=False, index=True)
    
    platform = Column(String, nullable=False, index=True)
    external_post_id = Column(String, nullable=True)
    
    status = Column(String, nullable=False, default="DRAFT", index=True) # DRAFT, QUEUED, PUBLISHING, PUBLISHED, FAILED, CANCELLED
    
    published_at = Column(DateTime, nullable=True)
    scheduled_for = Column(DateTime, nullable=True)
    
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    
    idempotency_key = Column(String, nullable=False, unique=True, index=True)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    attempts = relationship("PublicationAttempt", back_populates="publication", cascade="all, delete-orphan")

class PublicationAttempt(Base):
    __tablename__ = "publication_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publication_id = Column(UUID(as_uuid=True), ForeignKey("publications.id"), nullable=False)
    
    attempt_number = Column(String, nullable=False) # Store as string or int
    status = Column(String, nullable=False)
    
    request_metadata = Column(JSON, nullable=True)
    response_metadata = Column(JSON, nullable=True)
    
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    publication = relationship("Publication", back_populates="attempts")
