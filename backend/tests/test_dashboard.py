import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, engine
from app.models.all_models import Base, Brand, Workspace, User, WorkspaceMember, Integration, TrafficMetrics, SearchMetrics

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_client():
    return TestClient(app)

@pytest.fixture
def auth_headers_and_data(test_db):
    user = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="pwd")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    workspace = Workspace(name="Test Workspace", slug=f"test-{uuid.uuid4()}", owner_id=user.id)
    test_db.add(workspace)
    test_db.commit()
    test_db.refresh(workspace)
    
    member = WorkspaceMember(user_id=user.id, workspace_id=workspace.id, role="OWNER")
    test_db.add(member)
    
    brand = Brand(name="Test Brand", workspace_id=workspace.id, website_url="https://test.com")
    test_db.add(brand)
    test_db.commit()
    test_db.refresh(brand)
    
    # We login to get the access token cookie
    client = get_client()
    # Wait, the password is not hashed if we just put "pwd". Let's use the signup route.
    email = f"signup_{uuid.uuid4()}@example.com"
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "Test User"})
    
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = res.cookies.get("access_token")
    
    # Now we need the user's workspace and brand.
    # We can just create them via API to ensure they are properly associated.
    ws_res = client.post("/api/workspaces/", json={"name": "Api Workspace", "domain": "api.com"}, cookies={"access_token": token})
    ws_id = ws_res.json()["id"]
    
    brand_res = client.post("/api/brands/", json={"name": "Api Brand", "workspace_id": ws_id, "website_url": "https://example.com"}, headers={"X-Workspace-ID": ws_id}, cookies={"access_token": token})
    brand_id = brand_res.json()["id"]

    headers = {
        "X-Workspace-ID": str(ws_id),
        "X-Brand-ID": str(brand_id)
    }
    
    # Also fetch the actual DB models
    ws_model = test_db.query(Workspace).filter(Workspace.id == ws_id).first()
    brand_model = test_db.query(Brand).filter(Brand.id == brand_id).first()

    return client, test_db, headers, ws_model, brand_model, token

def test_dashboard_no_integrations(auth_headers_and_data):
    client, test_db, headers, workspace, brand, token = auth_headers_and_data
    response = client.get("/api/dashboard/command-center", headers=headers, cookies={"access_token": token})
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    
    leads_kpi = next((k for k in data["kpis"] if k["label"] == "Leads Generated"), None)
    assert leads_kpi is not None
    assert leads_kpi["value"] == "NOT_CONFIGURED"

def test_dashboard_with_integrations_no_data(auth_headers_and_data):
    client, test_db, headers, workspace, brand, token = auth_headers_and_data

    integration = Integration(brand_id=brand.id, workspace_id=workspace.id, provider="ga4", status="CONNECTED")
    test_db.add(integration)
    test_db.commit()
    
    response = client.get("/api/dashboard/command-center", headers=headers, cookies={"access_token": token})
    assert response.status_code == 200
    data = response.json()
    
    leads_kpi = next((k for k in data["kpis"] if k["label"] == "Leads Generated"), None)
    assert leads_kpi["value"] == "NO_DATA"

def test_dashboard_populated_data(auth_headers_and_data):
    client, test_db, headers, workspace, brand, token = auth_headers_and_data

    integration = Integration(brand_id=brand.id, workspace_id=workspace.id, provider="ga4", status="CONNECTED")
    test_db.add(integration)
    
    metrics = TrafficMetrics(brand_id=brand.id, workspace_id=workspace.id, conversions=150, sessions=1000)
    test_db.add(metrics)
    test_db.commit()
    
    response = client.get("/api/dashboard/command-center", headers=headers, cookies={"access_token": token})
    assert response.status_code == 200
    data = response.json()
    
    leads_kpi = next((k for k in data["kpis"] if k["label"] == "Leads Generated"), None)
    assert leads_kpi["value"] == "150"
    
    conv_kpi = next((k for k in data["kpis"] if k["label"] == "Avg Conversion Rate"), None)
    assert conv_kpi["value"] == "15.0%"

def test_dashboard_cross_tenant_access(auth_headers_and_data):
    client, test_db, headers, workspace, brand, token = auth_headers_and_data
    
    # Create another user via API
    email = f"signup_{uuid.uuid4()}@example.com"
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "Other User"})
    res2 = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token2 = res2.cookies.get("access_token")
    
    ws_res = client.post("/api/workspaces/", json={"name": "Other WS", "domain": "other.com"}, cookies={"access_token": token2})
    other_ws_id = ws_res.json()["id"]

    # Try to access first user's brand with second user's workspace
    bad_headers = {
        "X-Workspace-ID": str(other_ws_id),
        "X-Brand-ID": str(brand.id)
    }
    
    # Second user token, other ws, first user brand
    response = client.get("/api/dashboard/command-center", headers=bad_headers, cookies={"access_token": token2})
    assert response.status_code == 403

def test_website_analytics_not_configured(auth_headers_and_data):
    client, test_db, headers, workspace, brand, token = auth_headers_and_data
    response = client.get("/api/dashboard/website-analytics", headers=headers, cookies={"access_token": token})
    assert response.status_code == 200
    data = response.json()
    assert data["ga4"]["status"] == "NOT_CONFIGURED"
    assert data["gsc"]["status"] == "NOT_CONFIGURED"
    assert data["ga4"]["metrics"]["sessions"] == 0
    assert data["gsc"]["metrics"]["clicks"] == 0

def test_website_analytics_connected_no_data(auth_headers_and_data):
    client, test_db, headers, workspace, brand, token = auth_headers_and_data
    
    ga4_integ = Integration(brand_id=brand.id, workspace_id=workspace.id, provider="ga4", status="CONNECTED")
    gsc_integ = Integration(brand_id=brand.id, workspace_id=workspace.id, provider="gsc", status="CONNECTED")
    test_db.add_all([ga4_integ, gsc_integ])
    test_db.commit()

    response = client.get("/api/dashboard/website-analytics", headers=headers, cookies={"access_token": token})
    assert response.status_code == 200
    data = response.json()
    assert data["ga4"]["status"] == "NO_DATA"
    assert data["gsc"]["status"] == "NO_DATA"

def test_website_analytics_populated_data(auth_headers_and_data):
    client, test_db, headers, workspace, brand, token = auth_headers_and_data

    ga4_integ = Integration(brand_id=brand.id, workspace_id=workspace.id, provider="ga4", status="CONNECTED")
    gsc_integ = Integration(brand_id=brand.id, workspace_id=workspace.id, provider="gsc", status="CONNECTED")
    test_db.add_all([ga4_integ, gsc_integ])

    traffic = TrafficMetrics(
        brand_id=brand.id,
        workspace_id=workspace.id,
        sessions=540,
        active_users=410,
        pageviews=1280,
        engagement_rate=0.68,
        conversions=45
    )
    search = SearchMetrics(
        brand_id=brand.id,
        workspace_id=workspace.id,
        clicks=230,
        impressions=4500,
        ctr=0.051,
        position=8.4,
        query="organic loose leaf tea",
        page="/products/assam"
    )
    test_db.add_all([traffic, search])
    test_db.commit()

    response = client.get("/api/dashboard/website-analytics", headers=headers, cookies={"access_token": token})
    assert response.status_code == 200
    data = response.json()
    assert data["ga4"]["status"] == "AVAILABLE"
    assert data["ga4"]["metrics"]["sessions"] == 540
    assert data["ga4"]["metrics"]["active_users"] == 410
    assert data["ga4"]["metrics"]["pageviews"] == 1280
    assert data["ga4"]["metrics"]["conversions"] == 45
    assert data["ga4"]["metrics"]["engagement_rate"] == 0.68

    assert data["gsc"]["status"] == "AVAILABLE"
    assert data["gsc"]["metrics"]["clicks"] == 230
    assert data["gsc"]["metrics"]["impressions"] == 4500
    assert data["gsc"]["metrics"]["position"] == 8.4
    assert len(data["gsc"]["top_queries"]) >= 1
    assert data["gsc"]["top_queries"][0]["query"] == "organic loose leaf tea"

