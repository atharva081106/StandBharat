import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

def get_client():
    return TestClient(app)

def unique_email():
    return f"test_{uuid.uuid4()}@example.com"

def test_signup_success():
    client = get_client()
    email = unique_email()
    response = client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "Test User"})
    assert response.status_code == 200
    assert response.json()["email"] == email

def test_duplicate_signup():
    client = get_client()
    email = unique_email()
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "Test User"})
    response = client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "Test User"})
    assert response.status_code == 400

def test_invalid_signup():
    client = get_client()
    response = client.post("/api/auth/signup", json={"email": "not-an-email", "password": "password123"})
    assert response.status_code == 422

def test_login_success():
    client = get_client()
    email = unique_email()
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "Test User"})
    response = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.cookies

def test_invalid_login():
    client = get_client()
    email = unique_email()
    response = client.post("/api/auth/login", json={"email": email, "password": "wrong"})
    assert response.status_code == 400

def test_auth_me_authenticated():
    client = get_client()
    email = unique_email()
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "Test User"})
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login_resp.cookies.get("access_token")
    
    response = client.get("/api/auth/me", cookies={"access_token": token})
    assert response.status_code == 200
    assert response.json()["email"] == email

def test_auth_me_unauthenticated():
    client = get_client()
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_logout():
    client = get_client()
    email = unique_email()
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "Test User"})
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login_resp.cookies.get("access_token")
    
    logout_resp = client.post("/api/auth/logout", cookies={"access_token": token})
    assert logout_resp.status_code == 200
    assert "access_token" not in client.cookies

def test_protected_endpoint_without_auth():
    client = get_client()
    response = client.get("/api/workspaces")
    assert response.status_code == 401

def test_workspace_and_brand_isolation():
    client = get_client()
    # User A
    email_a = unique_email()
    client.post("/api/auth/signup", json={"email": email_a, "password": "password123", "name": "User A"})
    login_a = client.post("/api/auth/login", json={"email": email_a, "password": "password123"})
    cookies_a = {"access_token": login_a.cookies.get("access_token")}
    
    # User B
    client2 = get_client()
    email_b = unique_email()
    client2.post("/api/auth/signup", json={"email": email_b, "password": "password123", "name": "User B"})
    login_b = client2.post("/api/auth/login", json={"email": email_b, "password": "password123"})
    cookies_b = {"access_token": login_b.cookies.get("access_token")}
    
    # User A creates Workspace A
    ws_a_resp = client.post("/api/workspaces/", json={"name": "Workspace A", "domain": "a.com"})
    assert ws_a_resp.status_code == 200
    ws_a_id = ws_a_resp.json()["id"]
    
    # User B creates Workspace B
    ws_b_resp = client2.post("/api/workspaces/", json={"name": "Workspace B", "domain": "b.com"})
    assert ws_b_resp.status_code == 200
    ws_b_id = ws_b_resp.json()["id"]
    
    # User A tries to get Workspace A (PASS)
    assert client.get(f"/api/workspaces/{ws_a_id}", headers={"X-Workspace-ID": ws_a_id}).status_code == 200
    
    # User A tries to get Workspace B (DENIED)
    assert client.get(f"/api/workspaces/{ws_b_id}", headers={"X-Workspace-ID": ws_b_id}).status_code == 403
    
    # User A creates Brand A in Workspace A
    brand_a_resp = client.post("/api/brands/", json={"name": "Brand A", "workspace_id": ws_a_id}, headers={"X-Workspace-ID": ws_a_id})
    assert brand_a_resp.status_code == 200
    brand_a_id = brand_a_resp.json()["id"]
    
    # User A tries to create Brand B in Workspace B (DENIED)
    assert client.post("/api/brands/", json={"name": "Brand B", "workspace_id": ws_b_id}, headers={"X-Workspace-ID": ws_b_id}).status_code == 403
    
    # User A tries to get Brand A (PASS)
    assert client.get(f"/api/brands/{brand_a_id}", headers={"X-Workspace-ID": ws_a_id, "X-Brand-ID": brand_a_id}).status_code == 200
    
    # User B tries to get Brand A (DENIED)
    assert client2.get(f"/api/brands/{brand_a_id}", headers={"X-Workspace-ID": ws_a_id, "X-Brand-ID": brand_a_id}).status_code == 403

def test_role_authorization():
    client = get_client()
    email_a = unique_email()
    client.post("/api/auth/signup", json={"email": email_a, "password": "password123", "name": "User A"})
    login_a = client.post("/api/auth/login", json={"email": email_a, "password": "password123"})
    cookies_a = {"access_token": login_a.cookies.get("access_token")}
    
    ws_a_resp = client.post("/api/workspaces/", json={"name": "Workspace A", "domain": "a.com"}, cookies=cookies_a)
    ws_a_id = ws_a_resp.json()["id"]
    
    # User A patches Workspace A (PASS - OWNER)
    assert client.patch(f"/api/workspaces/{ws_a_id}", json={"name": "Workspace A updated"}, headers={"X-Workspace-ID": ws_a_id}, cookies=cookies_a).status_code == 200
