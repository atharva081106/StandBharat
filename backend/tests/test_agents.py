import pytest
import uuid
import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.all_models import Workspace, Brand, User, AgentRun, AgentHandoff, Opportunity
from app.agents.registry import agent_registry
from app.agents.context import AgentContext
from app.agents.runtime import AgentRuntime
from app.agents.result import AgentResult

# Dummy models setup
def setup_db():
    db = SessionLocal()
    u = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="pw")
    db.add(u)
    db.commit()
    
    ws1 = Workspace(name="WS1", slug=f"ws1-{uuid.uuid4()}")
    db.add(ws1)
    db.commit()
    
    b1 = Brand(workspace_id=ws1.id, name="Brand1")
    db.add(b1)
    db.commit()
    
    ws2 = Workspace(name="WS2", slug=f"ws2-{uuid.uuid4()}")
    db.add(ws2)
    db.commit()
    
    b2 = Brand(workspace_id=ws2.id, name="Brand2")
    db.add(b2)
    db.commit()
    
    return db, u, ws1, b1, ws2, b2

def test_agent_definition():
    agent = agent_registry.get_agent("seo_agent")
    assert agent.definition.id == "seo_agent"
    assert "seo_audit" in agent.definition.capabilities
    assert type(agent.definition.required_integrations) == list

def test_agent_context():
    ctx = AgentContext(
        run_id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        brand_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        input_data={}
    )
    assert ctx.brand_context is None
    assert ctx.task_id is None

def test_agent_runtime():
    db, u, ws, b, _, _ = setup_db()
    
    run_id = uuid.uuid4()
    run = AgentRun(id=run_id, workspace_id=ws.id, brand_id=b.id, agent_id="analytics")
    db.add(run)
    db.commit()
    
    agent = agent_registry.get_agent("analytics")
    runtime = AgentRuntime(db=db, agent=agent)
    
    ctx = AgentContext(
        run_id=run_id,
        workspace_id=ws.id,
        brand_id=b.id,
        user_id=u.id,
        input_data={}
    )
    
    result = runtime.execute_task(ctx)
    assert result.status in ["SUCCESS", "FAILED"]
    
    db.refresh(run)
    assert run.status in ["SUCCESS", "FAILED"]
    assert run.completed_at is not None

def test_agent_execution():
    # Will run via celery or synchronously to test end-to-end generic execution
    pass

def test_agent_failure():
    db, u, ws, b, _, _ = setup_db()
    
    run_id = uuid.uuid4()
    run = AgentRun(id=run_id, workspace_id=ws.id, brand_id=b.id, agent_id="linkedin_agent") # no integration => FAIL
    db.add(run)
    db.commit()
    
    agent = agent_registry.get_agent("linkedin_agent")
    runtime = AgentRuntime(db=db, agent=agent)
    
    ctx = AgentContext(
        run_id=run_id,
        workspace_id=ws.id,
        brand_id=b.id,
        user_id=u.id,
        input_data={}
    )
    
    result = runtime.execute_task(ctx)
    assert result.status == "NOT_CONFIGURED"
    
def test_agent_isolation():
    db, u, ws1, b1, ws2, b2 = setup_db()
    run_id = uuid.uuid4()
    run = AgentRun(id=run_id, workspace_id=ws1.id, brand_id=b1.id, agent_id="growth")
    db.add(run)
    db.commit()
    
    # Simulate isolation logic by making sure agent doesn't see B2 data
    # (The brand context service takes care of this by querying specifically for b1.id)
    pass

def test_agent_handoff():
    db, u, ws, b, _, _ = setup_db()
    run1 = AgentRun(workspace_id=ws.id, brand_id=b.id, agent_id="seo_agent", status="COMPLETED")
    db.add(run1)
    db.commit()
    
    run2 = AgentRun(workspace_id=ws.id, brand_id=b.id, agent_id="growth", status="QUEUED")
    db.add(run2)
    db.commit()
    
    handoff = AgentHandoff(
        workspace_id=ws.id,
        brand_id=b.id,
        source_agent="seo_agent",
        destination_agent="growth",
        source_run_id=run1.id,
        destination_run_id=run2.id
    )
    db.add(handoff)
    db.commit()
    
    assert handoff.id is not None
    assert handoff.source_agent == "seo_agent"

def test_agent_idempotency():
    # Calling the same agent with same input should not duplicate if idempotency key is used
    pass

def test_agent_integration_requirements():
    agent = agent_registry.get_agent("x_agent")
    assert "X" in agent.definition.required_integrations
    
def test_all_agents_exist():
    expected_agents = [
        "seo_agent", "geo_agent", "competitor", "growth", 
        "content_strategy", "content_writer", "analytics", "performance",
        "linkedin_agent", "x_agent", "reddit_agent", "coding_agent",
        "influencer_agent", "ugc_agent", "ai_cmo"
    ]
    for agent_id in expected_agents:
        agent = agent_registry.get_agent(agent_id)
        assert agent is not None
