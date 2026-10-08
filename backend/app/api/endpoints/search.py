from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_brand
from app.models.all_models import Brand, BrandVoice, Audience, Product, Competitor, Opportunity, AgentRun, ContentProject, Integration
from typing import List, Dict, Any

router = APIRouter()

@router.get("/")
def global_search(
    q: str = Query(..., min_length=2),
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    search_term = f"%{q}%"
    results = []

    # 1. Audiences
    audiences = db.query(Audience).filter(Audience.brand_id == brand.id, Audience.name.ilike(search_term)).limit(5).all()
    for a in audiences:
        results.append({"id": str(a.id), "type": "Audience", "title": a.name, "description": a.description or "", "url": f"/app/brand-brain"})

    # 2. Products
    products = db.query(Product).filter(Product.brand_id == brand.id, Product.name.ilike(search_term)).limit(5).all()
    for p in products:
        results.append({"id": str(p.id), "type": "Product", "title": p.name, "description": p.description or "", "url": f"/app/brand-brain"})

    # 3. Competitors
    competitors = db.query(Competitor).filter(Competitor.brand_id == brand.id, Competitor.name.ilike(search_term)).limit(5).all()
    for c in competitors:
        results.append({"id": str(c.id), "type": "Competitor", "title": c.name, "description": c.positioning or "", "url": f"/app/brand-brain"})

    # 4. Opportunities
    opportunities = db.query(Opportunity).filter(Opportunity.brand_id == brand.id, Opportunity.title.ilike(search_term)).limit(5).all()
    for o in opportunities:
        results.append({"id": str(o.id), "type": "Opportunity", "title": o.title, "description": o.description or "", "url": f"/app/opportunities"})

    # 5. AgentRuns
    runs = db.query(AgentRun).filter(AgentRun.workspace_id == brand.workspace_id, AgentRun.status.ilike(search_term)).limit(5).all()
    for r in runs:
        results.append({"id": str(r.id), "type": "AgentRun", "title": f"Run {r.id}", "description": f"Status: {r.status}", "url": f"/app/agents"})

    # 6. Content Projects
    projects = db.query(ContentProject).filter(ContentProject.brand_id == brand.id, ContentProject.title.ilike(search_term)).limit(5).all()
    for p in projects:
        results.append({"id": str(p.id), "type": "Content", "title": p.title, "description": p.status, "url": f"/app/content"})

    return results
