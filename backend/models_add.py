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
