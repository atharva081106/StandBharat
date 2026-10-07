import os
from pathlib import Path

BASE_DIR = Path("backend/app")

# Ensure directories exist
dirs = ["models", "schemas", "api/endpoints", "core", "db"]
for d in dirs:
    os.makedirs(BASE_DIR / d, exist_ok=True)

# Generate models
models_content = """from sqlalchemy import Column, String, ForeignKey, Enum, JSON, Integer, Text, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
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

class Brand(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'))
    name = Column(String, nullable=False)
    website_url = Column(String)
    description = Column(Text)
    industry = Column(String)
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
"""
with open(BASE_DIR / "models" / "all_models.py", "w") as f:
    f.write(models_content)

# Update base.py to import all models
base_content = """from app.db.base_class import Base
from app.models.all_models import User, Workspace, WorkspaceMember, Brand, Agent, AgentTask, AgentRun, Approval, ContentAsset, Campaign, Integration
"""
with open(BASE_DIR / "db" / "base.py", "w") as f:
    f.write(base_content)

# Update Alembic setup
import subprocess
try:
    subprocess.run(["alembic", "init", "migrations"], cwd="backend", check=True)
except Exception as e:
    print(f"Alembic init failed: {e}")

# We need to modify alembic.ini and env.py for SQLAlchemy setup
env_py_path = Path("backend/migrations/env.py")
if env_py_path.exists():
    with open(env_py_path, "r") as f:
        env_content = f.read()
    
    env_content = env_content.replace(
        "target_metadata = None",
        "import os\\nimport sys\\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\\nfrom app.db.base import Base\\nfrom app.core.config import settings\\ntarget_metadata = Base.metadata"
    )
    # We will override sqlalchemy.url from config in run_migrations_offline/online
    env_content = env_content.replace(
        "context.configure(",
        "context.configure(\\n        url=settings.DATABASE_URL,"
    )
    with open(env_py_path, "w") as f:
        f.write(env_content)

print("Backend models generated.")
