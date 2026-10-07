from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from app.models.all_models import WorkspaceMember

def check_workspace_role(db: Session, user_id: UUID, workspace_id: UUID, allowed_roles: list[str]):
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == user_id,
        WorkspaceMember.workspace_id == workspace_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
        
    if member.role.value not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient role permissions")
        
    return member
