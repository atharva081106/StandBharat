import pytest
import uuid
import datetime
import json
from unittest.mock import patch, MagicMock
from app.models.performance import PerformanceSnapshot
from app.models.all_models import Opportunity, Workspace, Brand, User
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
        
        # Mock ai_gateway.generate
        with patch("app.agents.specialized.performance_agent.ai_gateway") as mock_gateway:
            mock_res = MagicMock()
            mock_res.content = '{"signals": [{"type": "TEST", "confidence": "HIGH", "observation": "Obs", "interpretation": "Int", "recommendation": "Rec"}], "opportunities": [{"title": "Test Opp", "description": "Desc", "impact": "HIGH", "confidence": "HIGH", "effort": "LOW"}]}'
            mock_res.usage.prompt_tokens = 10
            mock_res.usage.completion_tokens = 20
            mock_gateway.generate.return_value = mock_res
            mock_gateway._get_provider.return_value.get_name.return_value = "mock_provider"
            mock_gateway._get_provider.return_value.default_model = "mock_model"
            
            result = agent.execute(context)
        
        assert result.status == "success"
        assert len(result.findings["signals"]) == 1
        assert result.findings["opportunities_created"] == 1
        
        # Verify deduplication
        with patch("app.agents.specialized.performance_agent.ai_gateway") as mock_gateway:
            mock_res = MagicMock()
            mock_res.content = '{"signals": [{"type": "TEST", "confidence": "HIGH", "observation": "Obs", "interpretation": "Int", "recommendation": "Rec"}], "opportunities": [{"title": "Test Opp", "description": "Desc", "impact": "HIGH", "confidence": "HIGH", "effort": "LOW"}]}'
            mock_gateway.generate.return_value = mock_res
            
            result2 = agent.execute(context)
            
        assert result2.findings["opportunities_created"] == 0 # Already exists
        
    finally:
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

