from sqlalchemy import Column, String, ForeignKey, Enum, JSON, Integer, Text, Float, Boolean, DateTime, UniqueConstraint
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.base_class import Base
import enum

class UserRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MARKETER = "MARKETER"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"

class User(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    
class Workspace(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    members = relationship("WorkspaceMember", back_populates="workspace")
    brands = relationship("Brand", back_populates="workspace")

class WorkspaceMember(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'))
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    workspace = relationship("Workspace", back_populates="members")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'workspace_id', name='uq_workspace_member'),
    )

class Brand(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'))
    name = Column(String, nullable=False)
    website_url = Column(String)
    description = Column(Text)
    industry = Column(String)
    category = Column(String)
    location = Column(String)
    mission = Column(Text)
    vision = Column(Text)
    values = Column(Text)
    tagline = Column(String)
    target_audience = Column(Text)
    status = Column(String, default="active")
    workspace = relationship("Workspace", back_populates="brands")

class Agent(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, index=True)
    name = Column(String)
    description = Column(Text)
    capabilities = Column(JSON)
    permissions = Column(JSON)
    autonomy_level = Column(String)

class AgentTask(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'))
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'))
    agent_type = Column(String)
    task_type = Column(String)
    priority = Column(Integer, default=0)
    status = Column(String, default="QUEUED")
    input_data = Column(JSON)
    output_data = Column(JSON)
    dependencies = Column(JSON)
    idempotency_key = Column(String, unique=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    error = Column(Text)
    retry_count = Column(Integer, default=0)

class AgentRun(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'))
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'))
    agent_type = Column(String)
    task_id = Column(UUID(as_uuid=True), ForeignKey('agenttask.id'))
    status = Column(String, default="RUNNING")
    input_data = Column(JSON)
    output_data = Column(JSON)
    provider = Column(String)
    model = Column(String)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration = Column(Float)
    error = Column(Text)
    retry_count = Column(Integer, default=0)

class Approval(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'))
    status = Column(String, default="PENDING")
    
class ContentAsset(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'))
    status = Column(String, default="DRAFT")

class Campaign(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'))
    status = Column(String, default="DRAFT")
    
class Integration(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'))
    provider = Column(String)

class Opportunity(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    impact = Column(String)
    confidence = Column(String)
    effort = Column(String)
    priority = Column(Integer, default=0)
    status = Column(String, default="NEW")
    source = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class MetricSnapshot(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    metric_name = Column(String, index=True)
    value = Column(Float)
    currency = Column(String)
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class ActivityEvent(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    type = Column(String)
    description = Column(Text)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class AIUsageEvent(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), index=True)
    agent_id = Column(String, nullable=True)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey('agentrun.id'), nullable=True)
    provider = Column(String)
    model = Column(String)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, nullable=True)
    status = Column(String) # e.g. SUCCESS, ERROR
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class BrandVoice(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), unique=True, index=True)
    tone = Column(String)
    personality = Column(String)
    writing_style = Column(String)
    preferred_language = Column(String)
    formality = Column(String)
    humor = Column(String)
    words_to_use = Column(Text)
    words_to_avoid = Column(Text)
    messaging_rules = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Audience(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    demographics = Column(Text)
    pain_points = Column(Text)
    needs = Column(Text)
    goals = Column(Text)
    objections = Column(Text)
    buying_triggers = Column(Text)
    preferred_channels = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Product(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    price = Column(String)
    value_proposition = Column(Text)
    features = Column(Text)
    benefits = Column(Text)
    target_audience = Column(String)
    url = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Positioning(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), unique=True, index=True)
    positioning_statement = Column(Text)
    unique_value_proposition = Column(Text)
    differentiators = Column(Text)
    key_messages = Column(Text)
    proof_points = Column(Text)
    market_category = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Goal(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    goal = Column(String, nullable=False)
    target_value = Column(String)
    current_value = Column(String, nullable=True)
    timeframe = Column(String)
    priority = Column(Integer, default=0)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Competitor(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    name = Column(String, nullable=False)
    website = Column(String)
    description = Column(Text)
    positioning = Column(Text)
    strengths = Column(Text)
    weaknesses = Column(Text)
    notes = Column(Text)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class BrandStrategy(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), unique=True, index=True)
    business_strategy = Column(Text)
    marketing_strategy = Column(Text)
    content_strategy = Column(Text)
    channel_strategy = Column(Text)
    growth_strategy = Column(Text)
    campaign_strategy = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class BrandDocument(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    name = Column(String, nullable=False)
    type = Column(String)
    source = Column(String)
    status = Column(String, default="active")
    metadata_json = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class OrchestratorConfig(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True, unique=True)
    mode = Column(String, default="OFF") # OFF, ASSISTED, AUTONOMOUS
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class OrchestrationRun(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    trigger_type = Column(String) # SCHEDULE, NEW_DATA, DEPENDENCY
    status = Column(String, default="RUNNING") # RUNNING, COMPLETED, FAILED
    decision = Column(String) # RUN, SKIP
    agent_id = Column(String, nullable=True)
    reason = Column(Text)
    input_snapshot = Column(JSON, nullable=True)
    output_snapshot = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class ContentProject(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey('opportunity.id'), nullable=True)
    title = Column(String, nullable=False)
    objective = Column(Text)
    content_type = Column(String)
    status = Column(String, default="PLANNED")
    priority = Column(Integer, default=0)
    created_by = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentBrief(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_project_id = Column(UUID(as_uuid=True), ForeignKey('contentproject.id'), index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    title = Column(String)
    objective = Column(Text)
    target_audience = Column(Text)
    key_message = Column(Text)
    angle = Column(Text)
    content_type = Column(String)
    tone = Column(String)
    call_to_action = Column(Text)
    keywords = Column(Text)
    competitor_context = Column(Text)
    supporting_evidence = Column(Text)
    source_opportunity_id = Column(UUID(as_uuid=True), ForeignKey('opportunity.id'), nullable=True)
    status = Column(String, default="DRAFT")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentDraft(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_project_id = Column(UUID(as_uuid=True), ForeignKey('contentproject.id'), index=True)
    brief_id = Column(UUID(as_uuid=True), ForeignKey('contentbrief.id'), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    content_type = Column(String)
    title = Column(String)
    body = Column(Text)
    status = Column(String, default="DRAFT")
    generated_by = Column(String) # E.g. "content_writer_agent" or "user_id"
    generation_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentVersion(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_draft_id = Column(UUID(as_uuid=True), ForeignKey('contentdraft.id'), index=True)
    version_number = Column(Integer)
    title = Column(String)
    body = Column(Text)
    change_summary = Column(Text)
    created_by = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class ContentApproval(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_project_id = Column(UUID(as_uuid=True), ForeignKey('contentproject.id'))
    content_draft_id = Column(UUID(as_uuid=True), ForeignKey('contentdraft.id'))
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'), index=True)
    requested_by = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=True)
    status = Column(String, default="PENDING")
    review_comment = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

from app.publishing.models import PublisherConnection, Publication, PublicationAttempt


from app.models.performance import PerformanceSnapshot

