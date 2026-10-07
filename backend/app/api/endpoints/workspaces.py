from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from app.models.all_models import Workspace, WorkspaceMember, UserRole, User
import uuid

router = APIRouter()

@router.post("/", response_model=WorkspaceResponse)
def create_workspace(
    workspace_in: WorkspaceCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # simple slug generation
    slug = workspace_in.name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8]
    workspace = Workspace(name=workspace_in.name, slug=slug, owner_id=current_user.id)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    
    # create member record
    member = WorkspaceMember(user_id=current_user.id, workspace_id=workspace.id, role=UserRole.OWNER)
    db.add(member)
    db.commit()
    
    return workspace

@router.get("/", response_model=list[WorkspaceResponse])
def get_workspaces(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    workspaces = db.query(Workspace).join(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).all()
    return workspaces

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: uuid.UUID,
    context: dict = Depends(deps.get_current_workspace)
):
    return context["workspace"]

@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: uuid.UUID,
    workspace_in: dict, # Simplified for demo, should be Pydantic schema
    db: Session = Depends(deps.get_db),
    context: dict = Depends(deps.require_role(["OWNER", "ADMIN"]))
):
    workspace = context["workspace"]
    if "name" in workspace_in:
        workspace.name = workspace_in["name"]
    db.commit()
    db.refresh(workspace)
    return workspace
