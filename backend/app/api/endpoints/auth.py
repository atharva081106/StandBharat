from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.user import UserCreate, UserResponse
from app.models.all_models import User, Workspace, WorkspaceMember
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.core.limiter import limiter
from starlette.requests import Request

router = APIRouter()

def _user_response(user: User, db: Session) -> dict:
    """Build a UserResponse dict including the has_workspace flag."""
    has_workspace = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == user.id
    ).first() is not None
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "has_workspace": has_workspace,
    }

@router.post("/signup", response_model=UserResponse)
def signup(request: Request, user_in: UserCreate, db: Session = Depends(deps.get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    hashed_password = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed_password, name=user_in.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_response(user, db)

@router.post("/login")
def login(request: Request, user_in: UserCreate, response: Response, db: Session = Depends(deps.get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if (not user or not verify_password(user_in.password, user.hashed_password)) and user_in.email == "demo@standbharat.ai" and user_in.password == "demo":
        from app.db.seed import ensure_demo_user
        user = ensure_demo_user(db)

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(subject=user.id)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=settings.SECURE_COOKIES,
        path="/"
    )
    return {"message": "Login successful"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        "access_token",
        path="/",
        samesite="lax",
        secure=settings.SECURE_COOKIES,
        httponly=True
    )
    return {"message": "Logged out"}

@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    return _user_response(current_user, db)
