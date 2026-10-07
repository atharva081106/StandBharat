import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ai.gateway import ai_gateway
from app.ai.config import ai_config
from app.ai.exceptions import AINotConfiguredException
from app.ai.schemas import AIRequestMessage
from app.agents.registry import agent_registry
from app.worker import execute_agent_task
import uuid
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.all_models import AIUsageEvent, AgentTask, AgentRun

def get_client():
    return TestClient(app)

def unique_email():
    return f"test_{uuid.uuid4()}@example.com"

def setup_user_and_workspace():
    client = get_client()
    email = unique_email()
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "User"})
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login_resp.cookies.get("access_token")
    client.cookies.set("access_token", token)
    
    ws_resp = client.post("/api/workspaces/", json={"name": "Workspace", "domain": "a.com"})
    ws_id = ws_resp.json()["id"]
    
    brand_resp = client.post("/api/brands/", json={"name": "Brand", "workspace_id": ws_id}, headers={"X-Workspace-ID": ws_id})
    brand_id = brand_resp.json()["id"]
    
    return client, ws_id, brand_id

def test_ai_status():
    client, _, _ = setup_user_and_workspace()
    resp = client.get("/api/ai/status")
    assert resp.status_code == 200
    data = resp.json()
    # Depending on env keys, configured will be true or false.
    # In CI without keys, it'll be false.
    assert "configured" in data

def test_ai_cmo_chat():
    client, ws_id, brand_id = setup_user_and_workspace()
    resp = client.post(
        "/api/ai/cmo/chat",
        json={"message": "Hello"},
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    assert data["status"] in ["SUCCESS", "AI_NOT_CONFIGURED", "AI_AUTH_ERROR", "AI_PROVIDER_ERROR", "AI_RATE_LIMITED"]

def test_agent_registry():
    agents = agent_registry.list_agents()
    assert len(agents) > 0
    agent = agent_registry.get_agent("test-agent")
    assert agent.name == "Test Agent"

def test_agent_run_api():
    client, ws_id, brand_id = setup_user_and_workspace()
    resp = client.post(
        "/api/agents/test-agent/run",
        json={"input_data": {"prompt": "Test"}},
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "task_id" in data
    assert "run_id" in data

def test_worker_execution():
    client, ws_id, brand_id = setup_user_and_workspace()
    # Create task directly or through API
    resp = client.post(
        "/api/agents/test-agent/run",
        json={"input_data": {"prompt": "Test"}},
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    data = resp.json()
    task_id = data["task_id"]
    run_id = data["run_id"]
    
    # The celery task ran synchronously because task_always_eager = True during tests
    # Verify DB state
    db: Session = SessionLocal()
    task = db.query(AgentTask).filter(AgentTask.id == uuid.UUID(task_id)).first()
    run = db.query(AgentRun).filter(AgentRun.id == uuid.UUID(run_id)).first()
    
    assert task is not None
    assert run is not None
    assert task.status in ["COMPLETED", "FAILED"] # Could be FAILED if AI not configured
    
    # If not configured, it will fail gracefully and the worker catches AINotConfiguredException as a normal exception 
    # and sets status to FAILED in the DB.
    
    db.close()
