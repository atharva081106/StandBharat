import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.agents.registry import agent_registry
import uuid

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

def test_registry_has_specialized_agents():
    assert agent_registry.get_agent("analytics").name == "Analytics Agent"
    assert agent_registry.get_agent("competitor").name == "Competitor Agent"
    assert agent_registry.get_agent("growth").name == "Growth Agent"

def test_agent_run_api():
    client, ws_id, brand_id = setup_user_and_workspace()
    
    # Test triggering analytics agent
    res = client.post(
        "/api/agents/analytics/run",
        json={"input_data": {}},
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert "run_id" in data
    
    run_id = data["run_id"]
    
    # Check agent run status
    res = client.get(
        f"/api/agent-runs/{run_id}",
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert res.status_code == 200
    run_data = res.json()
    assert run_data["agent_id"] == "analytics"
    assert run_data["status"] in ["RUNNING", "COMPLETED", "SUCCESS", "FAILED"]
