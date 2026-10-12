import pytest
from unittest.mock import patch, MagicMock
from app.db.session import SessionLocal
from app.models.all_models import Workspace, Brand, StrategyDocument, WebsiteAnalysis
from app.workers.celery_worker import generate_foundational_documents
from app.ai.exceptions import AINotConfiguredException
import uuid
import json

def setup_test_data():
    from app.models.all_models import Base
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    from app.models.all_models import User
    user = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="pw")
    db.add(user)
    db.commit()
    
    workspace = Workspace(name=f"WS {uuid.uuid4()}", slug=f"test-{uuid.uuid4()}", owner_id=user.id)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    
    brand = Brand(name="Test Brand", workspace_id=workspace.id)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return db, workspace, brand

@pytest.fixture
def mock_ai_response():
    mock = MagicMock()
    mock.content = json.dumps({
        "title": "Generated Doc",
        "executive_summary": "Summary",
        "sections": [{"heading": "Section 1", "content": "Content 1"}]
    })
    return mock

def test_generate_documents_success(mock_ai_response):
    db, workspace, brand = setup_test_data()
    try:
        analysis = WebsiteAnalysis(
            workspace_id=workspace.id,
            brand_id=brand.id,
            status="COMPLETED",
            url="https://example.com",
            analysis_results={"description": "Test company"}
        )
        db.add(analysis)
        db.commit()

        with patch("app.ai.gateway.ai_gateway") as mock_ai:
            mock_ai.generate.return_value = mock_ai_response
            
            result = generate_foundational_documents(str(workspace.id), str(brand.id))
            assert result["status"] == "success"
            assert len(result["results"]) == 4
            for r in result["results"]:
                assert r["status"] == "success"
                
            docs = db.query(StrategyDocument).filter_by(brand_id=brand.id).all()
            assert len(docs) == 4
            
            # test retries - should skip
            result2 = generate_foundational_documents(str(workspace.id), str(brand.id))
            assert result2["status"] == "success"
            for r in result2["results"]:
                assert r["status"] == "skipped"
    finally:
        db.close()

def test_generate_documents_missing_research():
    db, workspace, brand = setup_test_data()
    try:
        result = generate_foundational_documents(str(workspace.id), str(brand.id))
        assert result["status"] == "partial"
        assert result["reason"] == "insufficient_research"
    finally:
        db.close()

def test_generate_documents_missing_ai_config():
    db, workspace, brand = setup_test_data()
    try:
        analysis = WebsiteAnalysis(
            workspace_id=workspace.id,
            brand_id=brand.id,
            status="COMPLETED",
            url="https://example.com",
            analysis_results={"description": "Test company"}
        )
        db.add(analysis)
        db.commit()

        with patch("app.ai.gateway.ai_gateway") as mock_ai:
            mock_ai._get_provider.side_effect = AINotConfiguredException("No AI")
            
            result = generate_foundational_documents(str(workspace.id), str(brand.id))
            assert result["status"] == "not_configured"
    finally:
        db.close()

def test_generate_documents_tenant_isolation(mock_ai_response):
    db1, workspace1, brand1 = setup_test_data()
    db2, workspace2, brand2 = setup_test_data()
    
    try:
        analysis = WebsiteAnalysis(
            workspace_id=workspace1.id,
            brand_id=brand1.id,
            status="COMPLETED",
            url="https://example.com",
            analysis_results={"description": "Test company"}
        )
        db1.add(analysis)
        db1.commit()

        with patch("app.ai.gateway.ai_gateway") as mock_ai:
            mock_ai.generate.return_value = mock_ai_response
            
            # pass wrong workspace id for brand2
            result = generate_foundational_documents(str(workspace1.id), str(brand2.id))
            assert result["status"] == "error"
    finally:
        db1.close()
        db2.close()
