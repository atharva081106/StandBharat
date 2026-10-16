import pytest
import uuid
import json
from unittest.mock import patch, MagicMock
from app.workers.celery_worker import generate_core_brand_strategy, generate_foundational_documents
from app.models.all_models import BrandStrategy, StrategyDocument, Workspace, Brand, User, WebsiteAnalysis, Base
from app.api import deps
from tests.test_workflow_status import auth_headers_and_data, client
from app.db.session import SessionLocal, engine

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def setup_db_for_reliability(test_db):
    user = User(email=f"{uuid.uuid4()}@example.com", hashed_password="pwd")
    test_db.add(user)
    test_db.commit()
    
    workspace = Workspace(name="Rel WS", slug=f"rel-{uuid.uuid4()}", owner_id=user.id)
    test_db.add(workspace)
    test_db.commit()
    
    brand = Brand(name="Rel Brand", workspace_id=workspace.id, website_url="http://test.com")
    test_db.add(brand)
    test_db.commit()
    test_db.refresh(brand)
    
    # Needs a completed website analysis
    analysis = WebsiteAnalysis(
        workspace_id=workspace.id,
        brand_id=brand.id,
        status="COMPLETED",
        url="http://test.com",
        analysis_results={"description": "Test data"}
    )
    test_db.add(analysis)
    test_db.commit()
    
    return test_db, workspace.id, brand.id

def test_malformed_ai_output_recovery(setup_db_for_reliability):
    db, ws_id, brand_id = setup_db_for_reliability
    
    # 1. Mock malformed AI response (not JSON)
    from app.ai.schemas import AIResponse
    malformed_response = AIResponse(content="This is not valid JSON", provider="mock", model="mock", input_tokens=0, output_tokens=0, total_tokens=0, info={"provider": "mock", "model": "mock"})
    
    with patch("app.ai.gateway.AIGateway._get_provider", return_value=MagicMock()), patch("app.ai.gateway.AIGateway.generate", return_value=malformed_response):
        res = generate_core_brand_strategy(str(ws_id), str(brand_id))
        assert res["status"] == "error"
        assert "Expecting value" in res["reason"] # json decode error
        
        db.expire_all()
        strategy = db.query(BrandStrategy).filter_by(brand_id=brand_id).first()
        assert strategy.business_strategy == "FAILED"
        
        # Test Foundational Docs also handle it
        doc_res = generate_foundational_documents(str(ws_id), str(brand_id))
        assert doc_res["status"] == "success"
        assert doc_res["results"][0]["status"] == "error"
        
        db.expire_all()
        docs = db.query(StrategyDocument).filter_by(brand_id=brand_id).all()
        assert len(docs) > 0
        assert docs[0].status == "FAILED"
        
    # 2. Recover with valid JSON
    valid_content = json.dumps({
        "business_strategy": "Recovered Business",
        "marketing_strategy": "Recovered Marketing",
        "content_strategy": "Content",
        "channel_strategy": "Channel",
        "growth_strategy": "Growth",
        "campaign_strategy": "Campaign",
        "title": "Recovered Title",
        "executive_summary": "Recovered Summary",
        "sections": []
    })
    valid_response = AIResponse(content=valid_content, provider="mock", model="mock", input_tokens=0, output_tokens=0, total_tokens=0, info={"provider": "mock", "model": "mock"})
    
    with patch("app.ai.gateway.AIGateway._get_provider", return_value=MagicMock()), patch("app.ai.gateway.AIGateway.generate", return_value=valid_response):
        res = generate_core_brand_strategy(str(ws_id), str(brand_id))
        assert res["status"] == "success"
        
        db.expire_all()
        strategy = db.query(BrandStrategy).filter_by(brand_id=brand_id).first()
        assert strategy.business_strategy == "Recovered Business" # State changed from FAILED to actual content
        
        doc_res = generate_foundational_documents(str(ws_id), str(brand_id))
        assert doc_res["status"] == "success"
        
        db.expire_all()
        docs = db.query(StrategyDocument).filter_by(brand_id=brand_id).all()
        assert docs[0].status == "ACTIVE"
        assert docs[0].content["title"] == "Recovered Title"
        
    # 3. Verify Idempotency - Next runs should SKIP and not modify data
    with patch("app.ai.gateway.AIGateway._get_provider", return_value=MagicMock()), patch("app.ai.gateway.AIGateway.generate", return_value=malformed_response):
        # Even with malformed response mocked, it shouldn't be called
        res = generate_core_brand_strategy(str(ws_id), str(brand_id))
        assert res["status"] == "skipped"
        
        doc_res = generate_foundational_documents(str(ws_id), str(brand_id))
        assert doc_res["status"] == "success"
        for dr in doc_res["results"]:
            assert dr["status"] == "skipped"
            
        db.expire_all()
        strategy = db.query(BrandStrategy).filter_by(brand_id=brand_id).first()
        assert strategy.business_strategy == "Recovered Business" # User edits / recovered data is not overwritten
        
def test_missing_research_graceful_fail(setup_db_for_reliability):
    db, ws_id, brand_id = setup_db_for_reliability
    
    # Delete the analysis to simulate missing research
    db.query(WebsiteAnalysis).filter_by(brand_id=brand_id).delete()
    db.commit()
    
    res = generate_core_brand_strategy(str(ws_id), str(brand_id))
    assert res["status"] == "partial"
    assert res["reason"] == "insufficient_research"
    
    strategy = db.query(BrandStrategy).filter_by(brand_id=brand_id).first()
    assert strategy.business_strategy == "PARTIAL"

def test_queue_delay_maintains_processing(client, auth_headers_and_data, test_db):
    headers, workspace, brand, user = auth_headers_and_data
    
    analysis = WebsiteAnalysis(workspace_id=workspace.id, brand_id=brand.id, status="COMPLETED")
    strategy = BrandStrategy(brand_id=brand.id, business_strategy="QUEUED")
    
    test_db.add(analysis)
    test_db.add(strategy)
    test_db.commit()

    response = client.get(f"/api/brands/{brand.id}/workflow-status", headers=headers)
    assert response.status_code == 200
    assert response.json()["overall_status"] == "PROCESSING"

def test_missing_credentials_fails_gracefully(setup_db_for_reliability):
    db, ws_id, brand_id = setup_db_for_reliability
    
    from app.ai.exceptions import AINotConfiguredException
    with patch("app.ai.gateway.AIGateway._get_provider", side_effect=AINotConfiguredException("Missing API key")):
        res = generate_core_brand_strategy(str(ws_id), str(brand_id))
        assert res["status"] == "not_configured"
        assert res["reason"] == "ai_not_configured"
        
        db.expire_all()
        strategy = db.query(BrandStrategy).filter_by(brand_id=brand_id).first()
        assert strategy.business_strategy == "NOT_CONFIGURED"

import asyncio
from app.api.endpoints.website_analysis import _run_analysis_task

@pytest.mark.asyncio
async def test_dispatch_failure_reverts_queued_strategy(setup_db_for_reliability):
    db, ws_id, brand_id = setup_db_for_reliability
    
    # Pre-populate an analysis
    analysis = db.query(WebsiteAnalysis).filter_by(brand_id=brand_id).first()
    analysis.status = "PENDING"
    db.commit()

    with patch("app.api.endpoints.website_analysis.WebsiteAnalysisService.analyze_url", return_value={"metadata": {}, "analysis_results": {}}):
        with patch("app.api.endpoints.website_analysis.generate_core_brand_strategy.delay", side_effect=Exception("RabbitMQ down")):
            await _run_analysis_task(analysis.id, "http://test.com", db)
            
            db.expire_all()
            strategy = db.query(BrandStrategy).filter_by(brand_id=brand_id).first()
            assert strategy.business_strategy == "FAILED"
            assert analysis.status == "FAILED"

def test_successful_retry_preserves_active(setup_db_for_reliability):
    db, ws_id, brand_id = setup_db_for_reliability
    
    # Pre-populate active, manually edited strategy
    strategy = BrandStrategy(brand_id=brand_id, business_strategy="USER_EDITED_CONTENT")
    db.add(strategy)
    db.commit()
    
    # Run generator, it should skip due to existing valid content
    res = generate_core_brand_strategy(str(ws_id), str(brand_id))
    assert res["status"] == "skipped"
    assert res["reason"] == "already_exists"
    
    db.expire_all()
    db.expire_all()
    strategy = db.query(BrandStrategy).filter_by(brand_id=brand_id).first()
    assert strategy.business_strategy == "USER_EDITED_CONTENT"

def test_stale_workflow_recovery(client, auth_headers_and_data, test_db):
    headers, workspace, brand, user = auth_headers_and_data
    from datetime import datetime, timedelta, timezone
    
    # Pre-populate an analysis and strategy stuck in RUNNING 20 mins ago
    stale_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=20)
    
    analysis = WebsiteAnalysis(
        workspace_id=workspace.id, 
        brand_id=brand.id, 
        status="RUNNING",
        updated_at=stale_time
    )
    test_db.add(analysis)
    
    strategy = BrandStrategy(
        brand_id=brand.id, 
        business_strategy="QUEUED",
        updated_at=stale_time
    )
    test_db.add(strategy)
    test_db.commit()

    # The workflow-status endpoint should auto-heal them to FAILED
    response = client.get(f"/api/brands/{brand.id}/workflow-status", headers=headers)
    assert response.status_code == 200
    
    test_db.expire_all()
    analysis_refreshed = test_db.query(WebsiteAnalysis).filter_by(brand_id=brand.id).first()
    strategy_refreshed = test_db.query(BrandStrategy).filter_by(brand_id=brand.id).first()
    
    assert analysis_refreshed.status == "FAILED"
    assert "timed out" in analysis_refreshed.errors["message"]
    assert strategy_refreshed.business_strategy == "FAILED"
    
    # Endpoint should return FAILED
    assert response.json()["overall_status"] == "FAILED"

def test_recent_workflow_not_marked_stale(client, auth_headers_and_data, test_db):
    headers, workspace, brand, user = auth_headers_and_data
    from datetime import datetime, timedelta, timezone
    
    # Pre-populate an analysis and strategy stuck in RUNNING only 2 mins ago
    recent_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=2)
    
    analysis = WebsiteAnalysis(
        workspace_id=workspace.id, 
        brand_id=brand.id, 
        status="RUNNING",
        updated_at=recent_time
    )
    test_db.add(analysis)
    
    strategy = BrandStrategy(
        brand_id=brand.id, 
        business_strategy="QUEUED",
        updated_at=recent_time
    )
    test_db.add(strategy)
    test_db.commit()

    # The workflow-status endpoint should NOT auto-heal them
    response = client.get(f"/api/brands/{brand.id}/workflow-status", headers=headers)
    assert response.status_code == 200
    
    test_db.expire_all()
    analysis_refreshed = test_db.query(WebsiteAnalysis).filter_by(brand_id=brand.id).first()
    strategy_refreshed = test_db.query(BrandStrategy).filter_by(brand_id=brand.id).first()
    
    assert analysis_refreshed.status == "RUNNING"
    assert strategy_refreshed.business_strategy == "QUEUED"
    
    # Endpoint should return PROCESSING
    assert response.json()["overall_status"] == "PROCESSING"

def test_completed_analysis_skipped_on_retry(client, auth_headers_and_data, test_db):
    headers, workspace, brand, user = auth_headers_and_data
    
    # Pre-populate a COMPLETED analysis but no strategy
    analysis = WebsiteAnalysis(
        workspace_id=workspace.id, 
        brand_id=brand.id, 
        status="COMPLETED",
        url="http://test.com",
        analysis_results={"foo": "bar"}
    )
    test_db.add(analysis)
    test_db.commit()

    # Trigger generation
    with patch("app.api.endpoints.website_analysis.generate_core_brand_strategy.delay") as mock_delay:
        response = client.post(f"/api/brands/{brand.id}/website-analysis", headers=headers)
        assert response.status_code == 200
        
        # It should immediately trigger the celery task for the strategy
        mock_delay.assert_called_once()
        
        test_db.expire_all()
        strategy = test_db.query(BrandStrategy).filter_by(brand_id=brand.id).first()
        assert strategy is not None
        assert strategy.business_strategy == "QUEUED"
        
        # Analysis should REMAIN COMPLETED, not change to QUEUED
        analysis_refreshed = test_db.query(WebsiteAnalysis).filter_by(brand_id=brand.id).first()
        assert analysis_refreshed.status == "COMPLETED"
