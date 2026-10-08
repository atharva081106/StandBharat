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
    
    return client, ws_id, brand_id, token

def test_business_overview_isolation():
    client_a, ws_id_a, brand_id_a, token_a = setup_user_and_workspace()
    client_b, ws_id_b, brand_id_b, token_b = setup_user_and_workspace()

    # User A tries to modify Brand B
    response = client_a.patch(
        f"/api/brands/{brand_id_b}",
        json={"name": "Hacked Brand B"},
        headers={"X-Workspace-ID": ws_id_b, "X-Brand-ID": brand_id_b}
    )
    # Should be forbidden/unauthorized because User A is not in Workspace B
    assert response.status_code in [401, 403, 404]

    # User A tries to modify Brand B by passing their own workspace
    response2 = client_a.patch(
        f"/api/brands/{brand_id_b}",
        json={"name": "Hacked Brand B"},
        headers={"X-Workspace-ID": ws_id_a, "X-Brand-ID": brand_id_b}
    )
    assert response2.status_code in [400, 401, 403, 404]

    # User B modifies Brand B correctly
    response3 = client_b.patch(
        f"/api/brands/{brand_id_b}",
        json={"name": "Updated Brand B", "category": "New Category"},
        headers={"X-Workspace-ID": ws_id_b, "X-Brand-ID": brand_id_b}
    )
    assert response3.status_code == 200
    assert response3.json()["name"] == "Updated Brand B"
    assert response3.json()["category"] == "New Category"
