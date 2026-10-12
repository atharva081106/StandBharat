import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.config import settings

from app.api.deps import get_current_user, get_current_brand
import hmac
import hashlib

def generate_signed_state(workspace_id: str, brand_id: str, integration_id: str) -> str:
    payload = f"{workspace_id}:{brand_id}:{integration_id}"
    sig = hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"

@pytest.fixture
def client():
    # Setup overrides
    def override_get_current_user():
        user = MagicMock()
        user.id = "user-123"
        return user
        
    def override_get_current_brand():
        brand = MagicMock()
        brand.id = "brand-123"
        brand.workspace_id = "workspace-123"
        return brand
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_brand] = override_get_current_brand
    
    yield TestClient(app)
    
    # Teardown overrides
    app.dependency_overrides = {}

def test_oauth_login_missing_config(client):
    # Ensure settings are None
    with patch.object(settings, 'GOOGLE_CLIENT_ID', None), \
         patch.object(settings, 'GOOGLE_CLIENT_SECRET', None):
        
        response = client.get("/api/integrations/ga4/oauth/login")
        assert response.status_code == 500
        assert "Google OAuth configuration is missing" in response.json()["detail"]

def test_oauth_login_success(client):
    with patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id'), \
         patch.object(settings, 'GOOGLE_CLIENT_SECRET', 'test_client_secret'):
        
        response = client.get("/api/integrations/ga4/oauth/login")
        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "accounts.google.com/o/oauth2/auth" in data["authorization_url"]
        assert "client_id=test_client_id" in data["authorization_url"]

def test_oauth_callback_invalid_state(client):
    response = client.get("/api/integrations/oauth/callback?state=invalid&code=12345")
    assert response.status_code == 400
    assert "Invalid state parameter format" in response.json()["detail"]

def test_oauth_callback_tampered_state(client):
    # Valid payload, invalid signature
    state = "workspace-1:brand-2:ga4:invalidsignature123"
    response = client.get(f"/api/integrations/oauth/callback?state={state}&code=12345")
    assert response.status_code == 403
    assert "Cross-tenant access or tampered state denied" in response.json()["detail"]

@patch("google_auth_oauthlib.flow.Flow")
def test_oauth_callback_google_success(mock_flow_class, client):
    # Mock settings
    with patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id'), \
         patch.object(settings, 'GOOGLE_CLIENT_SECRET', 'test_client_secret'):
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        from app.api.deps import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Mock Flow instance
        mock_flow_instance = MagicMock()
        mock_flow_class.from_client_config.return_value = mock_flow_instance
        
        class MockCredentials:
            token = "mock_token"
            refresh_token = "mock_refresh"
            token_uri = "mock_uri"
            client_id = "test_client_id"
            client_secret = "test_client_secret"
            scopes = ["mock_scope"]
            
        mock_flow_instance.credentials = MockCredentials()

        state = generate_signed_state("11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222", "ga4")
        response = client.get(f"/api/integrations/oauth/callback?state={state}&code=auth_code_123")
        
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"
        mock_flow_instance.fetch_token.assert_called_once_with(code="auth_code_123")
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
        app.dependency_overrides.pop(get_db, None)
def test_oauth_callback_missing_config(client):
    with patch.object(settings, 'GOOGLE_CLIENT_ID', None), \
         patch.object(settings, 'GOOGLE_CLIENT_SECRET', None):
        
        state = generate_signed_state("11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222", "ga4")
        response = client.get(f"/api/integrations/oauth/callback?state={state}&code=123")
        
        assert response.status_code == 500
        assert "Google OAuth configuration is missing" in response.json()["detail"]
