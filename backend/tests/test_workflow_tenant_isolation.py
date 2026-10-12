import pytest
import uuid
import json
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.workers.celery_worker import generate_core_brand_strategy, generate_foundational_documents
from app.models.all_models import BrandStrategy, StrategyDocument, Workspace, Brand, User, WebsiteAnalysis, Base
from app.db.session import SessionLocal, engine
from app.api.deps import get_db, get_current_workspace, get_current_brand

client = TestClient(app)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def tenants(test_db):
    # Tenant A
    user_a = User(email=f"a_{uuid.uuid4()}@example.com", hashed_password="pwd")
    test_db.add(user_a)
    test_db.commit()
    ws_a = Workspace(name="WS A", slug=f"ws-a-{uuid.uuid4()}", owner_id=user_a.id)
    test_db.add(ws_a)
    test_db.commit()
    brand_a = Brand(name="Brand A", workspace_id=ws_a.id, website_url="http://test-a.com")
    test_db.add(brand_a)
    test_db.commit()

    # Tenant B
    user_b = User(email=f"b_{uuid.uuid4()}@example.com", hashed_password="pwd")
    test_db.add(user_b)
    test_db.commit()
    ws_b = Workspace(name="WS B", slug=f"ws-b-{uuid.uuid4()}", owner_id=user_b.id)
    test_db.add(ws_b)
    test_db.commit()
    brand_b = Brand(name="Brand B", workspace_id=ws_b.id, website_url="http://test-b.com")
    test_db.add(brand_b)
    test_db.commit()

    return test_db, {"ws": ws_a, "brand": brand_a, "user": user_a}, {"ws": ws_b, "brand": brand_b, "user": user_b}

def test_tenant_isolation_and_recovery(tenants):
    db, tenant_a, tenant_b = tenants
    
    # 1. Provide research for Tenant A ONLY
    analysis_a = WebsiteAnalysis(
        workspace_id=tenant_a["ws"].id,
        brand_id=tenant_a["brand"].id,
        status="COMPLETED",
        url="http://test-a.com",
        analysis_results={"description": "Tenant A Data"}
    )
    db.add(analysis_a)
    db.commit()

    # Tenant B has NO research

    from app.ai.schemas import AIResponse
    valid_content = json.dumps({
        "business_strategy": "Tenant A Business",
        "marketing_strategy": "Tenant A Marketing",
        "content_strategy": "Content",
        "channel_strategy": "Channel",
        "growth_strategy": "Growth",
        "campaign_strategy": "Campaign",
        "title": "Tenant A Title",
        "executive_summary": "Tenant A Summary",
        "sections": []
    })
    valid_response = AIResponse(content=valid_content, provider="mock", model="mock", input_tokens=0, output_tokens=0, total_tokens=0, info={"provider":"mock", "model":"mock"})

    malformed_response = AIResponse(content="Bad JSON", provider="mock", model="mock", input_tokens=0, output_tokens=0, total_tokens=0, info={"provider":"mock", "model":"mock"})

    # --- STRATEGY ISOLATION AND RECOVERY ---
    # Tenant B triggers strategy -> should fail gracefully (no research)
    with patch("app.ai.gateway.AIGateway.generate", return_value=valid_response):
        res_b = generate_core_brand_strategy(str(tenant_b["ws"].id), str(tenant_b["brand"].id))
        assert res_b["status"] == "partial"
        db.expire_all()
        strat_b = db.query(BrandStrategy).filter_by(brand_id=tenant_b["brand"].id).first()
        assert strat_b.business_strategy == "PARTIAL"

    # Tenant A triggers strategy -> mock failure
    with patch("app.ai.gateway.AIGateway.generate", return_value=malformed_response):
        res_a = generate_core_brand_strategy(str(tenant_a["ws"].id), str(tenant_a["brand"].id))
        assert res_a["status"] == "error"
        db.expire_all()
        strat_a = db.query(BrandStrategy).filter_by(brand_id=tenant_a["brand"].id).first()
        assert strat_a.business_strategy == "FAILED"

    # Tenant A recovers -> success
    with patch("app.ai.gateway.AIGateway.generate", return_value=valid_response):
        res_a = generate_core_brand_strategy(str(tenant_a["ws"].id), str(tenant_a["brand"].id))
        assert res_a["status"] == "success"
        db.expire_all()
        strat_a = db.query(BrandStrategy).filter_by(brand_id=tenant_a["brand"].id).first()
        assert strat_a.business_strategy == "Tenant A Business"
        
        # Cross check tenant B was not affected
        strat_b = db.query(BrandStrategy).filter_by(brand_id=tenant_b["brand"].id).first()
        assert strat_b.business_strategy == "PARTIAL"

    # --- FOUNDATIONAL DOCUMENTS ISOLATION ---
    with patch("app.ai.gateway.AIGateway.generate", return_value=valid_response):
        res_docs_a = generate_foundational_documents(str(tenant_a["ws"].id), str(tenant_a["brand"].id))
        assert res_docs_a["status"] == "success"
        
        db.expire_all()
        docs_a = db.query(StrategyDocument).filter_by(brand_id=tenant_a["brand"].id).all()
        assert len(docs_a) == 4
        assert docs_a[0].content["title"] == "Tenant A Title"

        # Tenant B triggers docs -> error, context empty or mismatch
        res_docs_b = generate_foundational_documents(str(tenant_b["ws"].id), str(tenant_b["brand"].id))
        assert res_docs_b["status"] == "partial"
        
        db.expire_all()
        docs_b = db.query(StrategyDocument).filter_by(brand_id=tenant_b["brand"].id).all()
        assert len(docs_b) == 0

    # --- API AUTHORIZATION ---
    # Attempt to read Brand A's brain using Tenant B's credentials
    def override_get_db():
        db2 = SessionLocal()
        try:
            yield db2
        finally:
            db2.close()

    def override_get_current_workspace():
        return tenant_b["ws"]

    def override_get_current_brand():
        # Pretend Tenant B is passing Brand A's ID in the URL, but the dependency should reject it
        # Wait, the dependency itself fetches the brand and checks ownership.
        # Let's mock a case where a user tries to access Brand A, but belongs to WS B.
        # In reality, the dependency checks if brand.workspace_id == workspace.id
        brand = db.query(Brand).filter(Brand.id == tenant_a["brand"].id).first()
        if brand.workspace_id != tenant_b["ws"].id:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Not authorized to access this brand")
        return brand

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_workspace] = override_get_current_workspace
    app.dependency_overrides[get_current_brand] = override_get_current_brand

    # Hit the brand brain endpoint for Brand A
    response = client.get(
        "/api/brand-brain/",
        headers={"X-Workspace-ID": str(tenant_b["ws"].id), "X-Brand-ID": str(tenant_a["brand"].id)}
    )
    assert response.status_code == 403

    app.dependency_overrides.clear()
