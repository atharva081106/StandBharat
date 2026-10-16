import pytest
import uuid
from unittest.mock import patch, MagicMock
from app.models.all_models import Workspace, Brand, User, WebsiteAnalysis, BrandStrategy, StrategyDocument
from app.db.session import SessionLocal

def setup_test_data():
    from app.models.all_models import Base
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="pw")
    db.add(user)
    db.commit()
    
    workspace = Workspace(name="Test WS", slug=f"test-{uuid.uuid4()}", owner_id=user.id)
    db.add(workspace)
    db.commit()
    
    brand = Brand(name="Test Brand", workspace_id=workspace.id, website_url="https://example.com")
    db.add(brand)
    db.commit()
    
    return db, user, workspace, brand

@pytest.fixture
def mock_ai_response():
    resp = MagicMock()
    resp.content = """{
        "business_strategy": "Grow 10x",
        "marketing_strategy": "Content marketing",
        "content_strategy": "Blog posts",
        "channel_strategy": "LinkedIn",
        "growth_strategy": "SEO",
        "campaign_strategy": "Q1 Launch"
    }"""
    return resp

def test_generate_strategy_success(mock_ai_response):
    db, user, workspace, brand = setup_test_data()
    try:
        # Add website analysis
        analysis = WebsiteAnalysis(
            workspace_id=workspace.id,
            brand_id=brand.id,
            status="COMPLETED",
            url="https://example.com",
            analysis_results={"description": "Test company"}
        )
        db.add(analysis)
        db.commit()

        from app.workers.celery_worker import generate_core_brand_strategy
        
        with patch("app.ai.gateway.ai_gateway") as mock_ai:
            mock_ai.generate.return_value = mock_ai_response
            
            result = generate_core_brand_strategy(str(workspace.id), str(brand.id))
            assert result["status"] == "success"
            
            strategy = db.query(BrandStrategy).filter_by(brand_id=brand.id).first()
            assert strategy is not None
            assert strategy.business_strategy == "Grow 10x"
            assert strategy.marketing_strategy == "Content marketing"

            # Test Retry Idempotence / Skip overwrite
            result2 = generate_core_brand_strategy(str(workspace.id), str(brand.id))
            assert result2["status"] == "skipped"
            
    finally:
        db.query(StrategyDocument).filter_by(brand_id=brand.id).delete()
        db.query(BrandStrategy).filter_by(brand_id=brand.id).delete()
        db.query(WebsiteAnalysis).filter_by(brand_id=brand.id).delete()
        db.query(Brand).filter_by(id=brand.id).delete()
        db.query(Workspace).filter_by(id=workspace.id).delete()
        db.query(User).filter_by(id=user.id).delete()
        db.commit()
        db.close()

def test_generate_strategy_insufficient_research():
    db, user, workspace, brand = setup_test_data()
    try:
        from app.workers.celery_worker import generate_core_brand_strategy
        
        with patch("app.ai.gateway.ai_gateway") as mock_ai:
            result = generate_core_brand_strategy(str(workspace.id), str(brand.id))
            assert result["status"] == "partial"
            
            strategy = db.query(BrandStrategy).filter_by(brand_id=brand.id).first()
            assert strategy is not None
            assert strategy.business_strategy == "PARTIAL"
            
    finally:
        db.query(BrandStrategy).filter_by(brand_id=brand.id).delete()
        db.query(Brand).filter_by(id=brand.id).delete()
        db.query(Workspace).filter_by(id=workspace.id).delete()
        db.query(User).filter_by(id=user.id).delete()
        db.commit()
        db.close()

def test_generate_strategy_missing_ai_config():
    db, user, workspace, brand = setup_test_data()
    try:
        # Add website analysis
        analysis = WebsiteAnalysis(
            workspace_id=workspace.id,
            brand_id=brand.id,
            status="COMPLETED",
            url="https://example.com",
            analysis_results={"description": "Test company"}
        )
        db.add(analysis)
        db.commit()

        from app.workers.celery_worker import generate_core_brand_strategy
        from app.ai.exceptions import AINotConfiguredException
        
        with patch("app.ai.gateway.ai_gateway") as mock_ai:
            mock_ai._get_provider.side_effect = AINotConfiguredException("No provider")
            result = generate_core_brand_strategy(str(workspace.id), str(brand.id))
            assert result["status"] == "not_configured"
            
            strategy = db.query(BrandStrategy).filter_by(brand_id=brand.id).first()
            assert strategy is not None
            assert strategy.business_strategy == "NOT_CONFIGURED"
            
    finally:
        db.query(StrategyDocument).filter_by(brand_id=brand.id).delete()
        db.query(BrandStrategy).filter_by(brand_id=brand.id).delete()
        db.query(WebsiteAnalysis).filter_by(brand_id=brand.id).delete()
        db.query(Brand).filter_by(id=brand.id).delete()
        db.query(Workspace).filter_by(id=workspace.id).delete()
        db.query(User).filter_by(id=user.id).delete()
        db.commit()
        db.close()

def test_generate_strategy_tenant_isolation(mock_ai_response):
    db1, user, workspace, brand = setup_test_data()
    db2, user2, workspace2, brand2 = setup_test_data()
    try:
        # Add website analysis to brand1
        analysis = WebsiteAnalysis(
            workspace_id=workspace.id,
            brand_id=brand.id,
            status="COMPLETED",
            url="https://example.com",
            analysis_results={"description": "Test company"}
        )
        db1.add(analysis)
        db1.commit()

        from app.workers.celery_worker import generate_core_brand_strategy
        
        with patch("app.ai.gateway.ai_gateway") as mock_ai:
            mock_ai.generate.return_value = mock_ai_response
            
            # If we pass correct workspace and brand, it works
            result = generate_core_brand_strategy(str(workspace.id), str(brand.id))
            assert result["status"] == "success"
            
            # If we pass mismatched workspace and brand (e.g. workspace1 with brand2)
            # The BrandContextService should raise ValueError, because brand2 is not in workspace1
            result2 = generate_core_brand_strategy(str(workspace.id), str(brand2.id))
            assert result2["status"] == "error"
            
    finally:
        db1.query(StrategyDocument).filter(StrategyDocument.brand_id.in_([brand.id, brand2.id])).delete()
        db1.query(BrandStrategy).filter(BrandStrategy.brand_id.in_([brand.id, brand2.id])).delete()
        db1.query(WebsiteAnalysis).filter(WebsiteAnalysis.brand_id.in_([brand.id, brand2.id])).delete()
        db1.query(Brand).filter(Brand.id.in_([brand.id, brand2.id])).delete()
        db1.query(Workspace).filter(Workspace.id.in_([workspace.id, workspace2.id])).delete()
        db1.query(User).filter(User.id.in_([user.id, user2.id])).delete()
        db1.commit()
        db1.close()
        db2.close()
