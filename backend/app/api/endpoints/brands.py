from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.brand import BrandCreate, BrandResponse
from app.models.all_models import Brand, WorkspaceMember, User
import uuid

router = APIRouter()

@router.post("/", response_model=BrandResponse)
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(deps.get_db),
    context: dict = Depends(deps.get_current_workspace)
):
    if str(brand_in.workspace_id) != str(context["workspace"].id):
        raise HTTPException(status_code=400, detail="Brand workspace does not match context")
        
    brand = Brand(**brand_in.dict())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

@router.get("/", response_model=list[BrandResponse])
def get_brands(
    db: Session = Depends(deps.get_db),
    context: dict = Depends(deps.get_current_workspace)
):
    brands = db.query(Brand).filter(Brand.workspace_id == context["workspace"].id).all()
    return brands

@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand: Brand = Depends(deps.get_current_brand)
):
    return brand

@router.patch("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_in: dict, # Simplified for demo
    brand: Brand = Depends(deps.get_current_brand),
    db: Session = Depends(deps.get_db),
    context: dict = Depends(deps.require_role(["OWNER", "ADMIN"]))
):
    for field in ["name", "website_url", "description", "industry", "category", "location", "mission", "vision", "values", "tagline", "status"]:
        if field in brand_in:
            setattr(brand, field, brand_in[field])
    db.commit()
    db.refresh(brand)
    return brand
