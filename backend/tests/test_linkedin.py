import pytest
import uuid
import json
import httpx
from unittest.mock import patch, MagicMock

from app.db.session import SessionLocal
from app.models.all_models import Workspace, Brand, User, Integration
from app.integrations.providers.linkedin import LinkedInProvider
from app.core.encryption import encrypt
from app.publishing.exceptions import AuthenticationError, PublishingError

@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def test_linkedin_validate_mocked():
    workspace_id = str(uuid.uuid4())
    
    creds = {
        "access_token": "mocked_token",
        "author_urn": "urn:li:person:123"
    }
    
    provider = LinkedInProvider()
    
    with patch.object(LinkedInProvider, '_get_credentials', return_value=creds):
        with patch("httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = provider.validate(workspace_id)
            assert result is True
            mock_get.assert_called_once()

def test_linkedin_publish_mocked():
    workspace_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    
    creds = {
        "access_token": "mocked_token",
        "author_urn": "urn:li:person:123"
    }
    
    provider = LinkedInProvider()
    
    content = {
        "brand_id": brand_id,
        "content_type": "LINKEDIN_POST",
        "body": "This is a test post"
    }
    
    with patch.object(LinkedInProvider, '_get_credentials', return_value=creds):
        with patch("httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.headers = {}
            mock_response.json.return_value = {"id": "urn:li:share:123"}
            mock_post.return_value = mock_response
            
            result = provider.publish(workspace_id, content)
            assert result["status"] == "success"
            assert result["external_id"] == "urn:li:share:123"

def test_linkedin_tenant_isolation():
    workspace1_id = str(uuid.uuid4())
    workspace2_id = str(uuid.uuid4())
    brand1_id = str(uuid.uuid4())
    
    provider = LinkedInProvider()
    
    content = {
        "brand_id": brand1_id,
        "content_type": "LINKEDIN_POST",
        "body": "This is a test post"
    }
    
    from app.publishing.exceptions import NotConfiguredError
    
    def mock_get_credentials(ws_id, b_id=None):
        if ws_id == workspace1_id:
            return {"access_token": "mocked", "author_urn": "urn"}
        raise NotConfiguredError()
        
    with patch.object(LinkedInProvider, '_get_credentials', side_effect=mock_get_credentials):
        with pytest.raises(NotConfiguredError):
            provider.publish(workspace2_id, content)
