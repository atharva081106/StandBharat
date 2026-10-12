import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, engine
from app.models.all_models import Base, Workspace, Brand, User, WebsiteAnalysis, BrandStrategy, StrategyDocument
import uuid
import json

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers_and_data(test_db, client):
    email = f"signup_{uuid.uuid4()}@example.com"
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "Test User"})
    
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = res.cookies.get("access_token")
    
    ws_res = client.post("/api/workspaces/", json={"name": "Api Workspace", "domain": "api.com"}, cookies={"access_token": token})
    ws_id = ws_res.json()["id"]
    
    brand_res = client.post("/api/brands/", json={"name": "Api Brand", "workspace_id": ws_id, "website_url": "https://example.com"}, headers={"X-Workspace-ID": ws_id}, cookies={"access_token": token})
    brand_id = brand_res.json()["id"]

    headers = {
        "X-Workspace-ID": str(ws_id),
        "X-Brand-ID": str(brand_id)
    }
    
    # We need to return the workspace and brand objects so we can attach db items to them
    workspace = test_db.query(Workspace).filter_by(id=ws_id).first()
    brand = test_db.query(Brand).filter_by(id=brand_id).first()
    user = test_db.query(User).filter_by(email=email).first()
    
    # For making authenticated requests inside tests
    client.cookies.set("access_token", token)
    
    return headers, workspace, brand, user

def test_workflow_status_not_started(client, auth_headers_and_data):
    headers, workspace, brand, user = auth_headers_and_data
    response = client.get(f"/api/brands/{brand.id}/workflow-status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "NOT_STARTED"
    assert data["website_analysis"] == "NOT_CONFIGURED"
    assert data["brand_strategy"] == "NOT_CONFIGURED"

def test_workflow_status_processing(client, auth_headers_and_data, test_db):
    headers, workspace, brand, user = auth_headers_and_data
    analysis = WebsiteAnalysis(workspace_id=workspace.id, brand_id=brand.id, status="RUNNING")
    test_db.add(analysis)
    test_db.commit()

    response = client.get(f"/api/brands/{brand.id}/workflow-status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "PROCESSING"

def test_workflow_status_completed(client, auth_headers_and_data, test_db):
    headers, workspace, brand, user = auth_headers_and_data
    analysis = WebsiteAnalysis(workspace_id=workspace.id, brand_id=brand.id, status="COMPLETED")
    strategy = BrandStrategy(brand_id=brand.id, business_strategy="Strategy JSON")
    doc1 = StrategyDocument(workspace_id=workspace.id, brand_id=brand.id)
    
    test_db.add(analysis)
    test_db.add(strategy)
    test_db.add(doc1)
    test_db.commit()

    response = client.get(f"/api/brands/{brand.id}/workflow-status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "COMPLETED"
    assert data["documents_generated"] == 1

def test_workflow_status_failed(client, auth_headers_and_data, test_db):
    headers, workspace, brand, user = auth_headers_and_data
    analysis = WebsiteAnalysis(workspace_id=workspace.id, brand_id=brand.id, status="COMPLETED")
    strategy = BrandStrategy(brand_id=brand.id, business_strategy="FAILED")
    
    test_db.add(analysis)
    test_db.add(strategy)
    test_db.commit()

    response = client.get(f"/api/brands/{brand.id}/workflow-status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "FAILED"

def test_workflow_status_partial(client, auth_headers_and_data, test_db):
    headers, workspace, brand, user = auth_headers_and_data
    analysis = WebsiteAnalysis(workspace_id=workspace.id, brand_id=brand.id, status="COMPLETED")
    strategy = BrandStrategy(brand_id=brand.id, business_strategy="PARTIAL")
    
    test_db.add(analysis)
    test_db.add(strategy)
    test_db.commit()

    response = client.get(f"/api/brands/{brand.id}/workflow-status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["brand_strategy"] == "PARTIAL"
    assert data["overall_status"] != "FAILED"

def test_workflow_status_cross_tenant(client, auth_headers_and_data, test_db):
    headers, workspace, brand, user = auth_headers_and_data
    
    # Create another workspace and brand by signing up another user
    email2 = f"signup_{uuid.uuid4()}@example.com"
    client.post("/api/auth/signup", json={"email": email2, "password": "password123", "name": "Test User 2"})
    res2 = client.post("/api/auth/login", json={"email": email2, "password": "password123"})
    token2 = res2.cookies.get("access_token")
    
    ws_res = client.post("/api/workspaces/", json={"name": "Workspace 2", "domain": "api2.com"}, cookies={"access_token": token2})
    ws_id2 = ws_res.json()["id"]
    
    brand_res = client.post("/api/brands/", json={"name": "Brand 2", "workspace_id": ws_id2, "website_url": "https://example.com"}, headers={"X-Workspace-ID": ws_id2}, cookies={"access_token": token2})
    brand_id2 = brand_res.json()["id"]
    
    # Use headers for workspace 1 but try to access brand 2
    # Client already has token 1 in cookies
    response = client.get(f"/api/brands/{brand_id2}/workflow-status", headers=headers)
    assert response.status_code == 403

def test_workflow_status_restarting(client, auth_headers_and_data, test_db):
    headers, workspace, brand, user = auth_headers_and_data
    
    # Analysis is complete, but strategy is processing
    analysis = WebsiteAnalysis(workspace_id=workspace.id, brand_id=brand.id, status="COMPLETED")
    strategy = BrandStrategy(brand_id=brand.id, business_strategy="QUEUED")
    
    test_db.add(analysis)
    test_db.add(strategy)
    test_db.commit()

    response = client.get(f"/api/brands/{brand.id}/workflow-status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "PROCESSING"

