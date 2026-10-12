import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.services.website_analysis import WebsiteAnalysisService, SSRFProtectionError, is_safe_url
from app.models.all_models import WebsiteAnalysis

@pytest.mark.asyncio
async def test_ssrf_protection():
    # Should block internal IPs
    assert not is_safe_url("http://127.0.0.1")
    assert not is_safe_url("http://localhost")
    assert not is_safe_url("http://192.168.1.1")
    assert not is_safe_url("http://10.0.0.1")
    assert not is_safe_url("http://169.254.169.254")
    
    # Should allow external
    assert is_safe_url("https://www.example.com")
    assert is_safe_url("http://google.com")

from app.main import app
from unittest.mock import patch, MagicMock, AsyncMock
import json
from app.ai.exceptions import AINotConfiguredException

def get_client():
    return TestClient(app)

def unique_email():
    return f"test_{uuid4()}@example.com"

def setup_user_and_workspace():
    client = get_client()
    email = unique_email()
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "User"})
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login_resp.cookies.get("access_token")
    client.cookies.set("access_token", token)
    
    ws_resp = client.post("/api/workspaces/", json={"name": "Workspace", "domain": "a.com"})
    ws_id = ws_resp.json()["id"]
    
    brand_resp = client.post("/api/brands/", json={"name": "Brand", "workspace_id": ws_id, "website_url": "https://www.example.com"}, headers={"X-Workspace-ID": ws_id})
    brand = brand_resp.json()
    
    return client, token, ws_id, brand

def test_website_analysis_api_isolation():
    client, token, ws_id, brand = setup_user_and_workspace()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": str(ws_id),
        "X-Brand-Id": str(brand['id'])
    }
    
    # 1. Fetch initial status (should be NOT_ANALYZED)
    res = client.get(f"/api/brands/{brand['id']}/website-analysis", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "NOT_ANALYZED"
    assert data["url"] == brand.get("website_url")
    
    # 2. Trigger Analysis
    res = client.post(f"/api/brands/{brand['id']}/website-analysis", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["QUEUED", "RUNNING", "COMPLETED", "FAILED"]
    
    # 3. Test Isolation (Try to access with different brand id)
    fake_brand_id = uuid4()
    headers["X-Brand-Id"] = str(fake_brand_id)
    res = client.get(f"/api/brands/{fake_brand_id}/website-analysis", headers=headers)
    assert res.status_code == 403 # Depends(get_current_brand) should 403 since fake_brand_id doesn't exist

@pytest.mark.asyncio
async def test_analyze_url_success():
    with patch("app.services.website_analysis.httpx.AsyncClient.get") as mock_get, \
         patch("app.services.website_analysis.httpx.AsyncClient.head") as mock_head, \
         patch("app.services.website_analysis.ai_gateway") as mock_ai:
         
        mock_response = MagicMock()
        mock_response.content = b"<html><head><title>Test Title</title></head><body><h1>Welcome</h1><p>We build great software.</p></body></html>"
        mock_response.status_code = 200
        mock_response.url = "https://www.example.com"
        mock_get.return_value = mock_response
        
        mock_head_resp = MagicMock()
        mock_head_resp.status_code = 200
        mock_head.return_value = mock_head_resp
        
        mock_ai_resp = MagicMock()
        mock_ai_resp.content = '{"description": "A software company", "products_services": ["Software"], "target_audience": "Businesses", "value_proposition": "Great software", "positioning": "Premium", "brand_voice": "Professional", "inferred_topics": ["Tech"]}'
        mock_ai.generate.return_value = mock_ai_resp
        
        result = await WebsiteAnalysisService.analyze_url("https://www.example.com")
        
        assert result["metadata"]["title"] == "Test Title"
        assert result["analysis_results"]["description"] == "A software company"
        assert result["analysis_results"]["products_services"] == ["Software"]
        
        mock_ai.generate.assert_called_once()
        prompt_content = mock_ai.generate.call_args[1]["messages"][1].content
        assert "We build great software." in prompt_content

@pytest.mark.asyncio
async def test_analyze_url_malformed_ai_output():
    with patch("app.services.website_analysis.httpx.AsyncClient.get") as mock_get, \
         patch("app.services.website_analysis.httpx.AsyncClient.head") as mock_head, \
         patch("app.services.website_analysis.ai_gateway") as mock_ai:
         
        mock_response = MagicMock()
        mock_response.content = b"<html><body>Content</body></html>"
        mock_response.status_code = 200
        mock_response.url = "https://www.example.com"
        mock_get.return_value = mock_response
        
        mock_head_resp = MagicMock()
        mock_head_resp.status_code = 200
        mock_head.return_value = mock_head_resp
        
        mock_ai_resp = MagicMock()
        # Invalid JSON
        mock_ai_resp.content = 'This is not json'
        mock_ai.generate.return_value = mock_ai_resp
        
        result = await WebsiteAnalysisService.analyze_url("https://www.example.com")
        
        # It should fallback to nulls, not raise an error
        assert result["analysis_results"]["description"] is None
        assert result["analysis_results"]["products_services"] == []

@pytest.mark.asyncio
async def test_analyze_url_insufficient_content():
    with patch("app.services.website_analysis.httpx.AsyncClient.get") as mock_get, \
         patch("app.services.website_analysis.httpx.AsyncClient.head") as mock_head, \
         patch("app.services.website_analysis.ai_gateway") as mock_ai:
         
        mock_response = MagicMock()
        mock_response.content = b"<html><body></body></html>" # Empty body
        mock_response.status_code = 200
        mock_response.url = "https://www.example.com"
        mock_get.return_value = mock_response
        
        mock_head_resp = MagicMock()
        mock_head_resp.status_code = 200
        mock_head.return_value = mock_head_resp
        
        mock_ai_resp = MagicMock()
        # AI returns empty structures as requested when no evidence
        mock_ai_resp.content = '{"description": null, "products_services": [], "target_audience": null, "value_proposition": null, "positioning": null, "brand_voice": null, "inferred_topics": []}'
        mock_ai.generate.return_value = mock_ai_resp
        
        result = await WebsiteAnalysisService.analyze_url("https://www.example.com")
        
        assert result["analysis_results"]["description"] is None
        assert result["analysis_results"]["products_services"] == []

@pytest.mark.asyncio
async def test_analyze_url_missing_ai_config():
    with patch("app.services.website_analysis.httpx.AsyncClient.get") as mock_get, \
         patch("app.services.website_analysis.httpx.AsyncClient.head") as mock_head, \
         patch("app.services.website_analysis.ai_gateway") as mock_ai:
         
        mock_response = MagicMock()
        mock_response.content = b"<html><body>Content</body></html>"
        mock_response.status_code = 200
        mock_response.url = "https://www.example.com"
        mock_get.return_value = mock_response
        
        mock_head_resp = MagicMock()
        mock_head_resp.status_code = 200
        mock_head.return_value = mock_head_resp
        
        mock_ai._get_provider.side_effect = AINotConfiguredException("No provider")
        
        result = await WebsiteAnalysisService.analyze_url("https://www.example.com")
        
        # It should handle the exception and return nulls
        assert result["analysis_results"]["description"] is None
        assert result["analysis_results"]["products_services"] == []
        mock_ai.generate.assert_not_called()
