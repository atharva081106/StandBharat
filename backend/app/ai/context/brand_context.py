from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from app.models.all_models import Brand, BrandVoice, Audience, Product, Positioning, Goal, Competitor, BrandStrategy, BrandDocument, WebsiteAnalysis
from app.schemas.brand_brain import BrandContextResponse

class BrandContextService:
    def get_brand_context(self, db: Session, brand_id: UUID, workspace_id: UUID) -> BrandContextResponse:
        brand = db.query(Brand).filter(Brand.id == brand_id, Brand.workspace_id == workspace_id).first()
        if not brand:
            raise HTTPException(status_code=403, detail="Brand not found in this workspace")
            
        voice = db.query(BrandVoice).filter(BrandVoice.brand_id == brand.id).first()
        audiences = db.query(Audience).filter(Audience.brand_id == brand.id).all()
        products = db.query(Product).filter(Product.brand_id == brand.id).all()
        positioning = db.query(Positioning).filter(Positioning.brand_id == brand.id).first()
        goals = db.query(Goal).filter(Goal.brand_id == brand.id).all()
        competitors = db.query(Competitor).filter(Competitor.brand_id == brand.id).all()
        strategy = db.query(BrandStrategy).filter(BrandStrategy.brand_id == brand.id).first()
        documents = db.query(BrandDocument).filter(BrandDocument.brand_id == brand.id).all()
        website_analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.brand_id == brand.id).first()
        
        return BrandContextResponse(
            brand=brand,
            voice=voice,
            audiences=audiences,
            products=products,
            positioning=positioning,
            goals=goals,
            competitors=competitors,
            strategy=strategy,
            documents=documents,
            website_analysis=website_analysis
        )

brand_context_service = BrandContextService()
