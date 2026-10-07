from typing import Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.all_models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/auth/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        # Fallback to header for testing
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_workspace(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    workspace_id = request.headers.get("X-Workspace-ID")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header is missing")
    
    from app.models.all_models import WorkspaceMember, Workspace
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == current_user.id,
        WorkspaceMember.workspace_id == workspace_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not authorized to access this workspace")
        
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    return {"workspace": workspace, "member": member}

def require_role(allowed_roles: list[str]):
    def role_checker(context: dict = Depends(get_current_workspace)):
        if context["member"].role.value not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return context
    return role_checker

def get_current_brand(
    request: Request,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_workspace)
):
    brand_id = request.headers.get("X-Brand-ID")
    if not brand_id:
        raise HTTPException(status_code=400, detail="X-Brand-ID header is missing")
        
    from app.models.all_models import Brand
    brand = db.query(Brand).filter(
        Brand.id == brand_id,
        Brand.workspace_id == context["workspace"].id
    ).first()
    
    if not brand:
        raise HTTPException(status_code=403, detail="Not authorized to access this brand")
        
    return brand
