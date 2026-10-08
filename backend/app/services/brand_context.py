from typing import Dict, Any, Optional
import uuid
from sqlalchemy.orm import Session
from app.models.all_models import (
    Brand, BrandVoice, Audience, Product, Positioning, Competitor, WebsiteAnalysis, BrandDocument
)

class BrandContextService:
    @staticmethod
    def get_unified_context(db: Session, workspace_id: uuid.UUID, brand_id: uuid.UUID) -> Dict[str, Any]:
        """
        Gathers all available context for a brand into a single normalized dictionary.
        This represents the 'Brand Brain' and single source of truth for the AI CMO and agents.
        """
        
        # 1. Fetch Core Brand & Business Overview
        brand = db.query(Brand).filter_by(workspace_id=workspace_id, id=brand_id).first()
        if not brand:
            raise ValueError("Brand not found in this workspace")
            
        context = {
            "business_overview": {
                "name": brand.name,
                "website_url": brand.website_url,
                "industry": brand.industry,
                "description": brand.description,
                "mission": brand.mission,
                "target_audience_summary": brand.target_audience
            },
            "website_analysis": {},
            "brand_voice": {},
            "audiences": [],
            "products": [],
            "competitors": [],
            "positioning": {}
        }
        
        # 2. Fetch Website Analysis
        website_analysis = db.query(WebsiteAnalysis).filter_by(workspace_id=workspace_id, brand_id=brand_id).first()
        if website_analysis and website_analysis.status == "COMPLETED":
            context["website_analysis"] = website_analysis.analysis_results or {}
            
        # 3. Fetch Brand Voice
        brand_voice = db.query(BrandVoice).filter_by(brand_id=brand_id).first()
        if brand_voice:
            context["brand_voice"] = {
                "tone": brand_voice.tone,
                "personality": brand_voice.personality,
                "writing_style": brand_voice.writing_style,
                "preferred_language": brand_voice.preferred_language,
                "messaging_rules": brand_voice.messaging_rules,
                "words_to_use": brand_voice.words_to_use,
                "words_to_avoid": brand_voice.words_to_avoid
            }
            
        # 4. Fetch Audiences
        audiences = db.query(Audience).filter_by(brand_id=brand_id).all()
        context["audiences"] = [
            {
                "name": a.name,
                "description": a.description,
                "pain_points": a.pain_points,
                "needs": a.needs,
                "buying_triggers": a.buying_triggers
            } for a in audiences
        ]
        
        # 5. Fetch Products
        products = db.query(Product).filter_by(brand_id=brand_id, status="active").all()
        context["products"] = [
            {
                "name": p.name,
                "description": p.description,
                "value_proposition": p.value_proposition,
                "features": p.features,
                "benefits": p.benefits,
                "target_audience": p.target_audience
            } for p in products
        ]
        
        # 6. Fetch Competitors
        competitors = db.query(Competitor).filter_by(brand_id=brand_id, status="active").all()
        context["competitors"] = [
            {
                "name": c.name,
                "website": c.website,
                "positioning": c.positioning,
                "strengths": c.strengths,
                "weaknesses": c.weaknesses
            } for c in competitors
        ]
        
        # 7. Fetch Positioning
        positioning = db.query(Positioning).filter_by(brand_id=brand_id).first()
        if positioning:
            context["positioning"] = {
                "positioning_statement": positioning.positioning_statement,
                "unique_value_proposition": positioning.unique_value_proposition,
                "differentiators": positioning.differentiators,
                "key_messages": positioning.key_messages
            }

        # 8. Fetch Strategy Documents
        from app.models.all_models import StrategyDocument
        strategy_docs = db.query(StrategyDocument).filter_by(
            workspace_id=workspace_id, 
            brand_id=brand_id, 
            status="ACTIVE"
        ).all()
        
        context["strategy"] = {}
        for doc in strategy_docs:
            context["strategy"][doc.type] = doc.content

        return context
