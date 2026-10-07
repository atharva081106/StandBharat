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

def test_brand_brain_get_context():
    client, ws_id, brand_id = setup_user_and_workspace()
    response = client.get(
        "/api/brand-brain/",
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert "brand" in data
    assert "audiences" in data
    
def test_brand_brain_voice_crud():
    client, ws_id, brand_id = setup_user_and_workspace()
    res = client.patch(
        "/api/brand-brain/voice",
        json={"tone": "Friendly"},
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert res.status_code == 200
    assert res.json()["tone"] == "Friendly"
    
    res2 = client.get(
        "/api/brand-brain/voice",
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert res2.status_code == 200
    assert res2.json()["tone"] == "Friendly"

def test_brand_brain_audience_crud():
    client, ws_id, brand_id = setup_user_and_workspace()
    res = client.post(
        "/api/brand-brain/audiences",
        json={"name": "Developers", "description": "People who code"},
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert res.status_code == 200
    aud_id = res.json()["id"]
    
    res = client.get(
        "/api/brand-brain/audiences",
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert res.status_code == 200
    assert len(res.json()) >= 1
    
    res = client.patch(
        f"/api/brand-brain/audiences/{aud_id}",
        json={"description": "Software Engineers"},
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert res.status_code == 200
    assert res.json()["description"] == "Software Engineers"
    
    res = client.delete(
        f"/api/brand-brain/audiences/{aud_id}",
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert res.status_code == 200

def test_brand_context_ai_cmo():
    client, ws_id, brand_id = setup_user_and_workspace()
    client.patch(
        "/api/brand-brain/voice",
        json={"tone": "Very formal"},
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    res = client.post(
        "/api/ai/cmo/chat",
        json={"message": "hello"},
        headers={"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    )
    assert res.status_code == 200
    assert "status" in res.json()
