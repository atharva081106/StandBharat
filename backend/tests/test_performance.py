import pytest
import uuid
import datetime
import json
from unittest.mock import patch, MagicMock
from app.models.performance import PerformanceSnapshot
from app.models.all_models import Opportunity, Workspace, Brand, User, TrafficMetrics, SearchMetrics
from app.services.performance.service import PerformanceService
from app.db.session import SessionLocal

def setup_test_data():
    db_session = SessionLocal()
    user = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="pw")
    db_session.add(user)
    db_session.commit()
    
    workspace = Workspace(name="Test WS", slug=f"test-{uuid.uuid4()}", owner_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    
    brand = Brand(name="Test Brand", workspace_id=workspace.id)
    db_session.add(brand)
    db_session.commit()
    
    return db_session, user, workspace, brand

@pytest.mark.asyncio
async def test_performance_agent_process():
    db_session, user, workspace, brand = setup_test_data()
    
    try:
        from app.agents.specialized.performance_agent import PerformanceAgent
        from app.agents.context import AgentContext
        
        # Need snapshot data
        snapshot = PerformanceSnapshot(
            workspace_id=workspace.id,
            brand_id=brand.id,
            channel="linkedin",
            source="linkedin_api",
            source_status="SUCCESS",
            impressions=2000
        )
        db_session.add(snapshot)
        db_session.commit()
        
        agent = PerformanceAgent()
        
        context = AgentContext(
            task_id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            workspace_id=workspace.id,
            brand_id=brand.id,
            user_id=user.id,
            input_data={}
        )
        with patch("app.agents.specialized.performance_agent.ai_gateway") as mock_gateway:
            mock_res = MagicMock()
            mock_res.content = '{"signals": [{"type": "TEST", "confidence": "HIGH", "observation": "Obs", "interpretation": "Int", "recommendation": "Rec"}], "opportunities": [{"title": "Test Opp", "description": "Desc", "impact": "HIGH", "confidence": "HIGH", "effort": "LOW"}]}'
            mock_res.usage.prompt_tokens = 10
            mock_res.usage.completion_tokens = 20
            mock_gateway._get_provider.return_value.get_name.return_value = "mock_provider"
            mock_gateway._get_provider.return_value.default_model = "mock_model"
            mock_gateway.generate.return_value = mock_res
            
            result = agent.execute(context)
        
        assert result.status == "SUCCESS"
        assert len(result.output_data["findings"]["signals"]) == 1
        assert result.output_data["findings"]["opportunities_created"] == 1
        
        # Verify deduplication
        with patch("app.agents.specialized.performance_agent.ai_gateway") as mock_gateway:
            mock_res = MagicMock()
            mock_res.content = '{"signals": [{"type": "TEST", "confidence": "HIGH", "observation": "Obs", "interpretation": "Int", "recommendation": "Rec"}], "opportunities": [{"title": "Test Opp", "description": "Desc", "impact": "HIGH", "confidence": "HIGH", "effort": "LOW"}]}'
            mock_res.usage.prompt_tokens = 10
            mock_res.usage.completion_tokens = 20
            mock_gateway._get_provider.return_value.get_name.return_value = "mock_provider"
            mock_gateway._get_provider.return_value.default_model = "mock_model"
            mock_gateway.generate.return_value = mock_res
            
            result2 = agent.execute(context)
            
        assert result2.output_data["findings"]["opportunities_created"] == 0 # Already exists
        
    finally:
        from app.models.all_models import AIUsageEvent
        db_session.query(AIUsageEvent).filter(AIUsageEvent.workspace_id == workspace.id).delete()
        db_session.query(Opportunity).filter(Opportunity.workspace_id == workspace.id).delete()
        db_session.query(PerformanceSnapshot).filter(PerformanceSnapshot.workspace_id == workspace.id).delete()
        db_session.query(Brand).filter(Brand.id == brand.id).delete()
        db_session.query(Workspace).filter(Workspace.id == workspace.id).delete()
        db_session.query(User).filter(User.id == user.id).delete()
        db_session.commit()
        db_session.close()

def test_performance_api_summary_with_data():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api.deps import get_db, get_current_user
    
    db_session, user, workspace, brand = setup_test_data()
    
    # Needs a member record
    from app.models.all_models import WorkspaceMember
    member = WorkspaceMember(user_id=user.id, workspace_id=workspace.id, role="OWNER")
    db_session.add(member)
    db_session.commit()
    
    # Insert test snapshot
    snapshot = PerformanceSnapshot(
        workspace_id=workspace.id,
        brand_id=brand.id,
        channel="linkedin",
        source="linkedin_api",
        source_status="SUCCESS",
        impressions=1000,
        engagements=50
    )
    db_session.add(snapshot)
    db_session.commit()

    def override_get_db():
        yield db_session
        
    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    client = TestClient(app)
    
    try:
        response = client.get(f"/api/performance/{workspace.id}/{brand.id}/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "AVAILABLE"
        assert "linkedin" in data["channels"]
        assert data["metrics"]["total_impressions"] == 1000
        assert data["metrics"]["total_engagements"] == 50
    finally:
        app.dependency_overrides.clear()
        db_session.query(WorkspaceMember).filter(WorkspaceMember.user_id == user.id).delete()
        db_session.query(PerformanceSnapshot).filter(PerformanceSnapshot.id == snapshot.id).delete()
        db_session.query(Brand).filter(Brand.id == brand.id).delete()
        db_session.query(Workspace).filter(Workspace.id == workspace.id).delete()
        db_session.query(User).filter(User.id == user.id).delete()
        db_session.commit()
        db_session.close()

@pytest.mark.asyncio
async def test_performance_agent_with_traffic_and_search():
    db_session, user, workspace, brand = setup_test_data()
    
    try:
        from app.agents.specialized.performance_agent import PerformanceAgent
        from app.agents.context import AgentContext
        
        # Add traffic metrics
        today = datetime.datetime.utcnow()
        traffic = TrafficMetrics(
            workspace_id=workspace.id,
            brand_id=brand.id,
            date=today,
            sessions=100,
            pageviews=200,
            engagement_rate=0.5,
            conversions=5
        )
        db_session.add(traffic)
        
        # Add search metrics
        search = SearchMetrics(
            workspace_id=workspace.id,
            brand_id=brand.id,
            date=today,
            clicks=50,
            impressions=1000,
            ctr=0.05,
            position=12.5
        )
        db_session.add(search)
        db_session.commit()
        
        agent = PerformanceAgent()
        context = AgentContext(
            task_id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            workspace_id=workspace.id,
            brand_id=brand.id,
            user_id=user.id,
            input_data={}
        )
        
        with patch("app.agents.specialized.performance_agent.ai_gateway") as mock_gateway:
            mock_res = MagicMock()
            mock_res.content = '{"signals": [{"type": "TRAFFIC_SPIKE", "confidence": "HIGH", "observation": "Obs", "interpretation": "Int", "recommendation": "Rec"}], "opportunities": []}'
            mock_res.usage.prompt_tokens = 10
            mock_res.usage.completion_tokens = 20
            mock_gateway._get_provider.return_value.get_name.return_value = "mock_provider"
            mock_gateway._get_provider.return_value.default_model = "mock_model"
            mock_gateway.generate.return_value = mock_res
            
            result = agent.execute(context)
            
            assert result.status == "SUCCESS"
            # Ensure the LLM prompt was actually provided with the real traffic/search metrics
            call_args = mock_gateway.generate.call_args[1]["messages"]
            prompt_content = call_args[1].content
            
            assert "Website Traffic Data (Last 7 Days):" in prompt_content
            assert "100" in prompt_content # sessions
            assert "Search Console Data (Last 7 Days):" in prompt_content
            assert "1000" in prompt_content # impressions

    finally:
        db_session.query(TrafficMetrics).filter(TrafficMetrics.workspace_id == workspace.id).delete()
        db_session.query(SearchMetrics).filter(SearchMetrics.workspace_id == workspace.id).delete()
        from app.models.all_models import AIUsageEvent
        db_session.query(AIUsageEvent).filter(AIUsageEvent.workspace_id == workspace.id).delete()
        db_session.query(Brand).filter(Brand.id == brand.id).delete()
        db_session.query(Workspace).filter(Workspace.id == workspace.id).delete()
        db_session.query(User).filter(User.id == user.id).delete()
        db_session.commit()
        db_session.close()

@pytest.mark.asyncio
async def test_performance_agent_tenant_isolation_and_date_filtering():
    db_session, user, workspace, brand = setup_test_data()
    # Create another workspace and brand to test isolation
    other_workspace = Workspace(name="Other WS", slug=f"other-{uuid.uuid4()}", owner_id=user.id)
    db_session.add(other_workspace)
    db_session.commit()
    other_brand = Brand(name="Other Brand", workspace_id=other_workspace.id)
    db_session.add(other_brand)
    db_session.commit()
    
    try:
        from app.agents.specialized.performance_agent import PerformanceAgent
        from app.agents.context import AgentContext
        
        today = datetime.datetime.utcnow()
        stale_date = today - datetime.timedelta(days=10)
        
        # Traffic for OTHER brand
        traffic_other = TrafficMetrics(
            workspace_id=other_workspace.id,
            brand_id=other_brand.id,
            date=today,
            sessions=9999,
            pageviews=9999,
            engagement_rate=0.9,
            conversions=999
        )
        db_session.add(traffic_other)
        
        # Stale traffic for CURRENT brand
        traffic_stale = TrafficMetrics(
            workspace_id=workspace.id,
            brand_id=brand.id,
            date=stale_date,
            sessions=555,
            pageviews=555,
            engagement_rate=0.5,
            conversions=55
        )
        db_session.add(traffic_stale)
        db_session.commit()
        
        agent = PerformanceAgent()
        context = AgentContext(
            task_id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            workspace_id=workspace.id,
            brand_id=brand.id,
            user_id=user.id,
            input_data={}
        )
        
        with patch("app.agents.specialized.performance_agent.ai_gateway") as mock_gateway:
            mock_res = MagicMock()
            mock_res.content = '{"signals": [], "opportunities": []}'
            mock_gateway._get_provider.return_value.get_name.return_value = "mock_provider"
            mock_gateway._get_provider.return_value.default_model = "mock_model"
            mock_gateway.generate.return_value = mock_res
            
            result = agent.execute(context)
            
            # Since the only data for this brand is stale (>7 days), and other brand data is isolated, 
            # it should report no data
            assert result.status == "SUCCESS"
            assert "No performance, traffic, or search data available" in result.output_data["findings"]["message"]
            
            # Ensure LLM was not called at all since there was no data
            mock_gateway.generate.assert_not_called()

    finally:
        db_session.query(TrafficMetrics).filter(TrafficMetrics.id.in_([traffic_other.id, traffic_stale.id])).delete()
        db_session.query(Brand).filter(Brand.id.in_([brand.id, other_brand.id])).delete()
        db_session.query(Workspace).filter(Workspace.id.in_([workspace.id, other_workspace.id])).delete()
        db_session.query(User).filter(User.id == user.id).delete()
        db_session.commit()
        db_session.close()

