import pytest
import uuid
import datetime
import time
import json
import hmac
import hashlib
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.encryption import encrypt, decrypt
from app.db.session import SessionLocal, engine
from app.api.deps import get_current_user, get_current_brand, get_db
from app.models.all_models import Base, Workspace, Brand, User, Integration, IntegrationSyncRun, TrafficMetrics, SearchMetrics

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_data(test_db):
    """Creates a user and workspace with two distinct brands for multi-tenant and multi-brand tests."""
    user = User(email=f"tester_{uuid.uuid4().hex[:8]}@example.com", hashed_password="pwd")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    ws = Workspace(name="Test Holdings", slug=f"holdings-{uuid.uuid4().hex[:6]}", owner_id=user.id)
    test_db.add(ws)
    test_db.commit()
    test_db.refresh(ws)

    b1 = Brand(name="Tea Brand", workspace_id=ws.id, website_url="https://tea.example.com")
    b2 = Brand(name="Coffee Brand", workspace_id=ws.id, website_url="https://coffee.example.com")
    test_db.add_all([b1, b2])
    test_db.commit()
    test_db.refresh(b1)
    test_db.refresh(b2)

    return {"user": user, "workspace": ws, "brand_1": b1, "brand_2": b2}

@pytest.fixture
def client_for_brand_1(test_db, test_data):
    b1 = test_data["brand_1"]
    user = test_data["user"]

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_current_brand] = lambda: b1
    app.dependency_overrides[get_db] = lambda: test_db

    yield TestClient(app)
    app.dependency_overrides = {}

def generate_signed_state(workspace_id: str, brand_id: str, integration_id: str, ts: int = None) -> str:
    if ts is None:
        ts = int(time.time())
    payload = f"{workspace_id}:{brand_id}:{integration_id}:{ts}"
    sig = hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"

# 1. Verify Imports in Worker Environment
def test_google_sdk_imports():
    from googleapiclient.discovery import build
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
    import google_auth_oauthlib

    assert build is not None
    assert BetaAnalyticsDataClient is not None
    assert AnalyticsAdminServiceClient is not None
    assert google_auth_oauthlib is not None

# 2. OAuth Login Replay-Protected State
def test_oauth_login_signed_state_with_replay_timestamp(client_for_brand_1, test_data):
    with patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id'), \
         patch.object(settings, 'GOOGLE_CLIENT_SECRET', 'test_client_secret'):
        resp = client_for_brand_1.get("/api/integrations/ga4/oauth/login")
        assert resp.status_code == 200
        data = resp.json()
        assert "authorization_url" in data
        assert "state=" in data["authorization_url"]

# 3. OAuth Callback Browser Redirect
@patch("app.worker.sync_integration.delay")
@patch("google_auth_oauthlib.flow.Flow")
def test_oauth_callback_browser_redirect(mock_flow_class, mock_sync_delay, client_for_brand_1, test_data, test_db):
    b1 = test_data["brand_1"]
    ws = test_data["workspace"]
    
    with patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id'), \
         patch.object(settings, 'GOOGLE_CLIENT_SECRET', 'test_client_secret'):
        mock_flow_instance = MagicMock()
        mock_flow_class.from_client_config.return_value = mock_flow_instance

        class MockCreds:
            token = "mock_token"
            refresh_token = "mock_refresh"
            token_uri = "mock_uri"
            client_id = "test_client_id"
            client_secret = "test_client_secret"
            scopes = ["https://www.googleapis.com/auth/analytics.readonly"]
        mock_flow_instance.credentials = MockCreds()

        state = generate_signed_state(str(ws.id), str(b1.id), "ga4")
        # Request with Accept: text/html to simulate browser navigation
        resp = client_for_brand_1.get(
            f"/api/integrations/oauth/callback?state={state}&code=auth_code_123",
            headers={"Accept": "text/html"},
            follow_redirects=False
        )
        assert resp.status_code == 302
        assert resp.headers["location"].startswith(f"{settings.FRONTEND_URL}/app/integrations?status=success&provider=ga4")
        
        # Verify DB commit and initial sync dispatch
        integ = test_db.query(Integration).filter(Integration.brand_id == b1.id, Integration.provider == "ga4").first()
        assert integ is not None
        assert integ.status == "CONNECTED"
        mock_sync_delay.assert_called_once()

# 4. OAuth Callback Replay-Expired State
def test_oauth_callback_expired_state(client_for_brand_1, test_data):
    b1 = test_data["brand_1"]
    ws = test_data["workspace"]
    old_ts = int(time.time()) - 1200  # 20 minutes ago
    state = generate_signed_state(str(ws.id), str(b1.id), "ga4", ts=old_ts)

    resp = client_for_brand_1.get(f"/api/integrations/oauth/callback?state={state}&code=auth_code_123")
    assert resp.status_code == 400
    assert "expired" in resp.json()["detail"].lower()

# 5. OAuth Callback Provider Error Handling
def test_oauth_callback_error_redirect(client_for_brand_1):
    resp = client_for_brand_1.get(
        "/api/integrations/oauth/callback?error=access_denied",
        headers={"Accept": "text/html"},
        follow_redirects=False
    )
    assert resp.status_code == 302
    assert "status=error" in resp.headers["location"]
    assert "access_denied" in resp.headers["location"]

# 6. GA4 Property Auto-Discovery
@patch("google.analytics.data_v1beta.BetaAnalyticsDataClient")
@patch("google.analytics.admin_v1beta.AnalyticsAdminServiceClient")
def test_ga4_property_auto_discovery(mock_admin_class, mock_data_class, test_data, test_db):
    b1 = test_data["brand_1"]
    ws = test_data["workspace"]

    creds_dict = {
        "token": "tok_123",
        "refresh_token": "ref_123",
        "token_uri": "uri",
        "client_id": "cid",
        "client_secret": "csec",
        "scopes": ["scope"]
    }
    integ = Integration(
        workspace_id=ws.id,
        brand_id=b1.id,
        provider="ga4",
        credentials_encrypted=encrypt(json.dumps(creds_dict)),
        status="CONNECTED",
        config={}
    )
    test_db.add(integ)
    test_db.commit()

    # Mock Admin Service Summaries
    mock_admin_instance = MagicMock()
    mock_admin_class.return_value = mock_admin_instance
    mock_prop_summary = MagicMock()
    mock_prop_summary.property = "properties/987654321"
    mock_prop_summary.display_name = "Tea Brand GA4 Main"
    mock_account = MagicMock()
    mock_account.property_summaries = [mock_prop_summary]
    mock_admin_instance.list_account_summaries.return_value = [mock_account]

    # Mock Data API Report Response
    mock_data_instance = MagicMock()
    mock_data_class.return_value = mock_data_instance
    mock_report_response = MagicMock()
    mock_row = MagicMock()
    mock_row.dimension_values = [MagicMock(value="20261010"), MagicMock(value="google"), MagicMock(value="organic"), MagicMock(value="/")]
    mock_row.metric_values = [MagicMock(value="150"), MagicMock(value="120"), MagicMock(value="400"), MagicMock(value="0.65"), MagicMock(value="12")]
    mock_report_response.rows = [mock_row]
    mock_data_instance.run_report.return_value = mock_report_response

    from app.integrations.providers.ga4 import GA4Provider
    provider = GA4Provider()
    result = provider.sync(workspace_id=str(ws.id), brand_id=str(b1.id), integration_id=str(integ.id))

    assert result["status"] == "success"
    assert result["records_processed"] == 1

    # Verify property_id was discovered and persisted into integ.config
    test_db.refresh(integ)
    assert integ.config["property_id"] == "987654321"
    assert integ.config["property_name"] == "Tea Brand GA4 Main"

    # Verify TrafficMetrics record created
    metric = test_db.query(TrafficMetrics).filter(TrafficMetrics.brand_id == b1.id).first()
    assert metric is not None
    assert metric.sessions == 150
    assert metric.active_users == 120

# 7. GA4 Property Manual Configuration Endpoint
@patch("app.worker.sync_integration.delay")
def test_ga4_property_manual_configuration(mock_sync_delay, client_for_brand_1, test_data, test_db):
    b1 = test_data["brand_1"]
    ws = test_data["workspace"]
    
    integ = Integration(
        workspace_id=ws.id,
        brand_id=b1.id,
        provider="ga4",
        credentials_encrypted=encrypt(json.dumps({"token": "tok"})),
        status="CONNECTED",
        config={}
    )
    test_db.add(integ)
    test_db.commit()

    resp = client_for_brand_1.post(
        "/api/integrations/ga4/configure-property",
        json={"property_id": "properties/555444333", "property_name": "Custom Property"}
    )
    assert resp.status_code == 200
    assert resp.json()["property_id"] == "555444333"

    test_db.refresh(integ)
    assert integ.config["property_id"] == "555444333"
    assert integ.config["property_name"] == "Custom Property"
    mock_sync_delay.assert_called_once()

# 8. Worker Multi-Brand Scoping Regression Test
@patch("google.analytics.data_v1beta.BetaAnalyticsDataClient")
def test_worker_multi_brand_isolation(mock_data_class, test_data, test_db):
    ws = test_data["workspace"]
    b1 = test_data["brand_1"]
    b2 = test_data["brand_2"]

    creds_enc = encrypt(json.dumps({"token": "tok"}))
    integ_b1 = Integration(workspace_id=ws.id, brand_id=b1.id, provider="ga4", credentials_encrypted=creds_enc, status="CONNECTED", config={"property_id": "111"})
    integ_b2 = Integration(workspace_id=ws.id, brand_id=b2.id, provider="ga4", credentials_encrypted=creds_enc, status="CONNECTED", config={"property_id": "222"})
    test_db.add_all([integ_b1, integ_b2])
    test_db.commit()

    # Mock Data API Report Response for Brand 2
    mock_data_instance = MagicMock()
    mock_data_class.return_value = mock_data_instance
    mock_report_response = MagicMock()
    mock_row = MagicMock()
    mock_row.dimension_values = [MagicMock(value="20261011"), MagicMock(value="direct"), MagicMock(value="(none)"), MagicMock(value="/coffee")]
    mock_row.metric_values = [MagicMock(value="300"), MagicMock(value="250"), MagicMock(value="600"), MagicMock(value="0.75"), MagicMock(value="25")]
    mock_report_response.rows = [mock_row]
    mock_data_instance.run_report.return_value = mock_report_response

    # Create Sync Run targeting Brand 2
    run_b2 = IntegrationSyncRun(
        integration_id=integ_b2.id,
        workspace_id=ws.id,
        brand_id=b2.id,
        provider_id="ga4",
        status="QUEUED"
    )
    test_db.add(run_b2)
    test_db.commit()

    from app.worker import sync_integration
    sync_integration(str(run_b2.id))

    test_db.refresh(run_b2)
    assert run_b2.status == "COMPLETED"
    assert run_b2.records_processed == 1

    # Brand 2 has metrics, Brand 1 remains empty and unaffected
    b2_metrics = test_db.query(TrafficMetrics).filter(TrafficMetrics.brand_id == b2.id).all()
    b1_metrics = test_db.query(TrafficMetrics).filter(TrafficMetrics.brand_id == b1.id).all()
    assert len(b2_metrics) == 1
    assert b2_metrics[0].sessions == 300
    assert len(b1_metrics) == 0

# 9. Scheduled Sync Avoids Concurrent Duplicates
@patch("app.worker.sync_integration.delay")
def test_scheduled_sync_avoids_concurrent_duplicates(mock_sync_delay, test_data, test_db):
    # Clean up any leftover integration sync runs to ensure pure test isolation
    test_db.query(IntegrationSyncRun).delete()
    test_db.query(Integration).delete()
    test_db.commit()

    ws = test_data["workspace"]
    b1 = test_data["brand_1"]

    integ = Integration(
        workspace_id=ws.id,
        brand_id=b1.id,
        provider="ga4",
        credentials_encrypted=encrypt(json.dumps({"token": "tok"})),
        status="CONNECTED",
        last_sync_at=datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    )
    test_db.add(integ)
    test_db.commit()

    # Pre-existing RUNNING sync
    running_run = IntegrationSyncRun(
        integration_id=integ.id,
        workspace_id=ws.id,
        brand_id=b1.id,
        provider_id="ga4",
        status="RUNNING"
    )
    test_db.add(running_run)
    test_db.commit()

    from app.worker import sync_all_active_integrations
    result = sync_all_active_integrations()
    # Since an active run is in progress, it must skip and dispatch 0
    assert result["dispatched"] == 0
    mock_sync_delay.assert_not_called()

# 10. Sync Dispatch Failure Handling
@patch("app.api.endpoints.integrations.sync_integration_task.delay", side_effect=Exception("Redis Connection Refused"))
@patch("google_auth_oauthlib.flow.Flow")
def test_sync_dispatch_failure_handling(mock_flow, mock_sync_delay, client_for_brand_1, test_data, test_db):
    b1 = test_data["brand_1"]
    ws = test_data["workspace"]
    
    with patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id'), \
         patch.object(settings, 'GOOGLE_CLIENT_SECRET', 'test_client_secret'):
        mock_flow_instance = MagicMock()
        mock_flow.from_client_config.return_value = mock_flow_instance
        class MockCreds:
            token = "mock_token"
            refresh_token = "mock_refresh"
            token_uri = "mock_uri"
            client_id = "cid"
            client_secret = "csec"
            scopes = ["scopes"]
        mock_flow_instance.credentials = MockCreds()

        state = generate_signed_state(str(ws.id), str(b1.id), "ga4")
        resp = client_for_brand_1.get(
            f"/api/integrations/oauth/callback?state={state}&code=code_123",
            headers={"Accept": "application/json"}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "SUCCESS"

        # The connection was committed and preserved
        integ = test_db.query(Integration).filter(Integration.brand_id == b1.id, Integration.provider == "ga4").first()
        assert integ is not None
        assert integ.status == "CONNECTED"

        # The sync run truthfully records dispatch failure without server crash
        run = test_db.query(IntegrationSyncRun).filter(IntegrationSyncRun.integration_id == integ.id).first()
        assert run is not None
        assert run.status == "FAILED"
        assert "dispatch failed" in run.error.lower()

# 11. Test /api/integrations/google/callback Route Alias
@patch("app.api.endpoints.integrations.sync_integration_task.delay")
@patch("google_auth_oauthlib.flow.Flow")
def test_oauth_callback_google_route_alias(mock_flow, mock_sync_delay, client_for_brand_1, test_data, test_db):
    b1 = test_data["brand_1"]
    ws = test_data["workspace"]

    with patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id'), \
         patch.object(settings, 'GOOGLE_CLIENT_SECRET', 'test_client_secret'):
        mock_flow_instance = MagicMock()
        mock_flow.from_client_config.return_value = mock_flow_instance
        class MockCreds:
            token = "mock_token"
            refresh_token = "mock_refresh"
            token_uri = "mock_uri"
            client_id = "cid"
            client_secret = "csec"
            scopes = ["scopes"]
        mock_flow_instance.credentials = MockCreds()

        state = generate_signed_state(str(ws.id), str(b1.id), "ga4")
        resp = client_for_brand_1.get(
            f"/api/integrations/google/callback?state={state}&code=code_123",
            headers={"Accept": "application/json"}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "SUCCESS"

# 12. Test Truthful Error Reporting When Google Credentials Missing
def test_oauth_login_missing_credentials_truthful_error(client_for_brand_1):
    with patch.object(settings, 'GOOGLE_CLIENT_ID', None), \
         patch.object(settings, 'GOOGLE_CLIENT_SECRET', None):
        resp_ga4 = client_for_brand_1.get("/api/integrations/ga4/oauth/login")
        assert resp_ga4.status_code == 500
        assert "Google OAuth configuration is missing" in resp_ga4.json()["detail"]

        resp_gsc = client_for_brand_1.get("/api/integrations/gsc/oauth/login")
        assert resp_gsc.status_code == 500
        assert "Google OAuth configuration is missing" in resp_gsc.json()["detail"]


