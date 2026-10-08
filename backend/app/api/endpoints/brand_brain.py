from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_brand, get_current_user
from app.models.all_models import Brand, BrandVoice, Audience, Product, Positioning, Goal, Competitor, BrandStrategy, BrandDocument, User
from app.schemas.brand_brain import (
    BrandVoiceUpdate, BrandVoiceResponse,
    AudienceCreate, AudienceUpdate, AudienceResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    PositioningUpdate, PositioningResponse,
    GoalCreate, GoalUpdate, GoalResponse,
    CompetitorCreate, CompetitorUpdate, CompetitorResponse,
    StrategyUpdate, StrategyResponse,
    BrandDocumentResponse,
    BrandContextResponse
)

router = APIRouter()

# ----------------- BRAND BRAIN CONTEXT -----------------
@router.get("/", response_model=BrandContextResponse)
def get_brand_brain(
    db: Session = Depends(get_db),
    brand: Brand = Depends(get_current_brand),
    current_user: User = Depends(get_current_user)
):
    voice = db.query(BrandVoice).filter(BrandVoice.brand_id == brand.id).first()
    audiences = db.query(Audience).filter(Audience.brand_id == brand.id).all()
    products = db.query(Product).filter(Product.brand_id == brand.id).all()
    positioning = db.query(Positioning).filter(Positioning.brand_id == brand.id).first()
    goals = db.query(Goal).filter(Goal.brand_id == brand.id).all()
    competitors = db.query(Competitor).filter(Competitor.brand_id == brand.id).all()
    strategy = db.query(BrandStrategy).filter(BrandStrategy.brand_id == brand.id).first()
    documents = db.query(BrandDocument).filter(BrandDocument.brand_id == brand.id).all()
    
    return {
        "brand": brand,
        "voice": voice,
        "audiences": audiences,
        "products": products,
        "positioning": positioning,
        "goals": goals,
        "competitors": competitors,
        "strategy": strategy,
        "documents": documents
    }

# ----------------- VOICE -----------------
@router.get("/voice", response_model=BrandVoiceResponse)
def get_voice(db: Session = Depends(get_db), brand: Brand = Depends(get_current_brand)):
    voice = db.query(BrandVoice).filter(BrandVoice.brand_id == brand.id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    return voice

@router.patch("/voice", response_model=BrandVoiceResponse)
def update_voice(
    voice_in: BrandVoiceUpdate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    voice = db.query(BrandVoice).filter(BrandVoice.brand_id == brand.id).first()
    if not voice:
        voice = BrandVoice(brand_id=brand.id)
        db.add(voice)
        
    for field, value in voice_in.model_dump(exclude_unset=True).items():
        setattr(voice, field, value)
        
    db.commit()
    db.refresh(voice)
    return voice

# ----------------- AUDIENCES -----------------
@router.get("/audiences", response_model=List[AudienceResponse])
def get_audiences(db: Session = Depends(get_db), brand: Brand = Depends(get_current_brand)):
    return db.query(Audience).filter(Audience.brand_id == brand.id).all()

@router.post("/audiences", response_model=AudienceResponse)
def create_audience(
    audience_in: AudienceCreate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    audience = Audience(**audience_in.model_dump(), brand_id=brand.id)
    db.add(audience)
    db.commit()
    db.refresh(audience)
    return audience

@router.patch("/audiences/{id}", response_model=AudienceResponse)
def update_audience(
    id: UUID, 
    audience_in: AudienceUpdate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    audience = db.query(Audience).filter(Audience.id == id, Audience.brand_id == brand.id).first()
    if not audience:
        raise HTTPException(status_code=404, detail="Audience not found")
    
    for field, value in audience_in.model_dump(exclude_unset=True).items():
        setattr(audience, field, value)
        
    db.commit()
    db.refresh(audience)
    return audience

@router.delete("/audiences/{id}")
def delete_audience(
    id: UUID, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    audience = db.query(Audience).filter(Audience.id == id, Audience.brand_id == brand.id).first()
    if not audience:
        raise HTTPException(status_code=404, detail="Audience not found")
    db.delete(audience)
    db.commit()
    return {"status": "ok"}

# ----------------- PRODUCTS -----------------
@router.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db), brand: Brand = Depends(get_current_brand)):
    return db.query(Product).filter(Product.brand_id == brand.id).all()

@router.post("/products", response_model=ProductResponse)
def create_product(
    product_in: ProductCreate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    product = Product(**product_in.model_dump(), brand_id=brand.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.patch("/products/{id}", response_model=ProductResponse)
def update_product(
    id: UUID, 
    product_in: ProductUpdate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    product = db.query(Product).filter(Product.id == id, Product.brand_id == brand.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
        
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{id}")
def delete_product(
    id: UUID, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    product = db.query(Product).filter(Product.id == id, Product.brand_id == brand.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"status": "ok"}

# ----------------- POSITIONING -----------------
@router.get("/positioning", response_model=PositioningResponse)
def get_positioning(db: Session = Depends(get_db), brand: Brand = Depends(get_current_brand)):
    positioning = db.query(Positioning).filter(Positioning.brand_id == brand.id).first()
    if not positioning:
        raise HTTPException(status_code=404, detail="Positioning not found")
    return positioning

@router.patch("/positioning", response_model=PositioningResponse)
def update_positioning(
    pos_in: PositioningUpdate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    positioning = db.query(Positioning).filter(Positioning.brand_id == brand.id).first()
    if not positioning:
        positioning = Positioning(brand_id=brand.id)
        db.add(positioning)
        
    for field, value in pos_in.model_dump(exclude_unset=True).items():
        setattr(positioning, field, value)
        
    db.commit()
    db.refresh(positioning)
    return positioning

# ----------------- GOALS -----------------
@router.get("/goals", response_model=List[GoalResponse])
def get_goals(db: Session = Depends(get_db), brand: Brand = Depends(get_current_brand)):
    return db.query(Goal).filter(Goal.brand_id == brand.id).all()

@router.post("/goals", response_model=GoalResponse)
def create_goal(
    goal_in: GoalCreate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    goal = Goal(**goal_in.model_dump(), brand_id=brand.id)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

@router.patch("/goals/{id}", response_model=GoalResponse)
def update_goal(
    id: UUID, 
    goal_in: GoalUpdate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    goal = db.query(Goal).filter(Goal.id == id, Goal.brand_id == brand.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for field, value in goal_in.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
        
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/goals/{id}")
def delete_goal(
    id: UUID, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    goal = db.query(Goal).filter(Goal.id == id, Goal.brand_id == brand.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"status": "ok"}

# ----------------- COMPETITORS -----------------
@router.get("/competitors", response_model=List[CompetitorResponse])
def get_competitors(db: Session = Depends(get_db), brand: Brand = Depends(get_current_brand)):
    return db.query(Competitor).filter(Competitor.brand_id == brand.id).all()

@router.post("/competitors", response_model=CompetitorResponse)
def create_competitor(
    comp_in: CompetitorCreate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    competitor = Competitor(**comp_in.model_dump(), brand_id=brand.id)
    db.add(competitor)
    db.commit()
    db.refresh(competitor)
    return competitor

@router.patch("/competitors/{id}", response_model=CompetitorResponse)
def update_competitor(
    id: UUID, 
    comp_in: CompetitorUpdate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    competitor = db.query(Competitor).filter(Competitor.id == id, Competitor.brand_id == brand.id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    for field, value in comp_in.model_dump(exclude_unset=True).items():
        setattr(competitor, field, value)
        
    db.commit()
    db.refresh(competitor)
    return competitor

@router.delete("/competitors/{id}")
def delete_competitor(
    id: UUID, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    competitor = db.query(Competitor).filter(Competitor.id == id, Competitor.brand_id == brand.id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    db.delete(competitor)
    db.commit()
    return {"status": "ok"}

# ----------------- STRATEGY -----------------
@router.get("/strategy", response_model=StrategyResponse)
def get_strategy(db: Session = Depends(get_db), brand: Brand = Depends(get_current_brand)):
    strategy = db.query(BrandStrategy).filter(BrandStrategy.brand_id == brand.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@router.patch("/strategy", response_model=StrategyResponse)
def update_strategy(
    strat_in: StrategyUpdate, 
    db: Session = Depends(get_db), 
    brand: Brand = Depends(get_current_brand)
):
    strategy = db.query(BrandStrategy).filter(BrandStrategy.brand_id == brand.id).first()
    if not strategy:
        strategy = BrandStrategy(brand_id=brand.id)
        db.add(strategy)
        
    for field, value in strat_in.model_dump(exclude_unset=True).items():
        setattr(strategy, field, value)
        
    db.commit()
    db.refresh(strategy)
    return strategy

# ----------------- DOCUMENTS -----------------
import os
import shutil
import uuid
from fastapi import UploadFile, File, Form, BackgroundTasks, HTTPException
from typing import Optional

from app.api import deps
from app.services.document_processor import process_document

STORAGE_DIR = "storage/documents"

@router.get("/documents", response_model=List[BrandDocumentResponse])
def get_documents(db: Session = Depends(get_db), brand: Brand = Depends(get_current_brand)):
    return db.query(BrandDocument).filter(BrandDocument.brand_id == brand.id).order_by(BrandDocument.created_at.desc()).all()

@router.post("/documents", response_model=BrandDocumentResponse)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: Optional[str] = Form("Uncategorized"),
    db: Session = Depends(get_db),
    brand: Brand = Depends(get_current_brand),
    current_user: User = Depends(deps.get_current_user)
):
    # Validate extension
    allowed_extensions = ['.pdf', '.docx', '.txt', '.md', '.csv']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file format. Supported formats: {', '.join(allowed_extensions)}")
        
    # Secure filename and paths
    # Using uuid for storage filename to prevent path traversal and arbitrary overwrites
    safe_filename = f"{uuid.uuid4()}{ext}"
    brand_storage_dir = os.path.join(STORAGE_DIR, str(brand.workspace_id), str(brand.id))
    os.makedirs(brand_storage_dir, exist_ok=True)
    
    file_path = os.path.join(brand_storage_dir, safe_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    file_size = os.path.getsize(file_path)
    
    # Create DB record
    doc = BrandDocument(
        id=uuid.uuid4(),
        workspace_id=brand.workspace_id,
        brand_id=brand.id,
        name=file.filename,
        type=file.content_type or ext,
        source="upload",
        file_path=file_path,
        file_size=file_size,
        category=category,
        processing_status="UPLOADED",
        retrieval_status="NOT_CONFIGURED",
        uploaded_by=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Trigger processing
    background_tasks.add_task(process_document, db, str(doc.id))
    
    return doc

@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    brand: Brand = Depends(get_current_brand)
):
    doc = db.query(BrandDocument).filter(BrandDocument.id == document_id, BrandDocument.brand_id == brand.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Cleanup file
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"Warning: Failed to delete file {doc.file_path}: {str(e)}")
            
    # Remove from DB
    db.delete(doc)
    db.commit()
    
    return {"message": "Document deleted successfully"}

