import pytest
from fastapi.testclient import TestClient
from app.main import app
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

def test_command_center_api():
    client, ws_id, brand_id = setup_user_and_workspace()
    
    response = client.get("/api/dashboard/command-center", headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id})
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "opportunities" in data
    assert "recent_activity" in data
    
def test_opportunity_crud():
    client, ws_id, brand_id = setup_user_and_workspace()
    
    # Create
    opp_data = {
        "title": "Test Opp",
        "impact": "High",
        "confidence": "Medium",
        "effort": "Low"
    }
    create_resp = client.post(
        "/api/opportunities/", 
        json=opp_data,
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert create_resp.status_code == 200
    opp_id = create_resp.json()["id"]
    
    # Read
    get_resp = client.get(
        f"/api/opportunities/{opp_id}",
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Test Opp"
    
    # Update
    update_resp = client.patch(
        f"/api/opportunities/{opp_id}",
        json={"status": "IN_PROGRESS"},
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "IN_PROGRESS"
    
    # List
    list_resp = client.get(
        "/api/opportunities/",
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    
    # Delete
    del_resp = client.delete(
        f"/api/opportunities/{opp_id}",
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert del_resp.status_code == 200
    
def test_cross_workspace_opportunity_access():
    client1, ws1_id, brand1_id = setup_user_and_workspace()
    client2, ws2_id, brand2_id = setup_user_and_workspace()
    
    # client1 creates opp in ws1
    create_resp = client1.post(
        "/api/opportunities/", 
        json={"title": "Test Opp"},
        headers={"X-Workspace-ID": ws1_id, "X-Brand-ID": brand1_id}
    )
    opp_id = create_resp.json()["id"]
    
    # client2 tries to access opp_id pretending to be in ws1 (DENIED - no membership)
    get_resp = client2.get(
        f"/api/opportunities/{opp_id}",
        headers={"X-Workspace-ID": ws1_id, "X-Brand-ID": brand1_id}
    )
    assert get_resp.status_code == 403
    
    # client2 tries to access opp_id in ws2 (NOT FOUND - it belongs to ws1)
    get_resp = client2.get(
        f"/api/opportunities/{opp_id}",
        headers={"X-Workspace-ID": ws2_id, "X-Brand-ID": brand2_id}
    )
    assert get_resp.status_code == 404
