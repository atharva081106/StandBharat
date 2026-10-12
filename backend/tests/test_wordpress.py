import pytest
import uuid
import json
import httpx
from unittest.mock import patch, MagicMock

from app.db.session import SessionLocal
from app.models.all_models import Workspace, Brand, User, Integration
from app.integrations.providers.wordpress import WordPressProvider
from app.core.encryption import encrypt
from app.publishing.exceptions import AuthenticationError, PublishingError
from app.services.website_analysis import SSRFProtectionError

@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def test_wordpress_connect_ssrf():
    provider = WordPressProvider()
    with pytest.raises(SSRFProtectionError):
        provider.connect(str(uuid.uuid4()), {
            "site_url": "http://127.0.0.1/wp",
            "username": "admin",
            "app_password": "password"
        })

@patch("httpx.get")
@patch("app.integrations.providers.wordpress.is_safe_url")
def test_wordpress_connect_success(mock_is_safe_url, mock_get):
    mock_is_safe_url.return_value = True
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    provider = WordPressProvider()
    result = provider.connect(str(uuid.uuid4()), {
        "site_url": "https://valid.example.com",
        "username": "admin",
        "app_password": "password"
    })
    
    assert result is True
    mock_get.assert_called_once()

@patch("httpx.post")
def test_wordpress_publish_success(mock_post, db_session):
    workspace = Workspace(name=f"WS {uuid.uuid4()}", slug=f"ws-{uuid.uuid4()}")
    db_session.add(workspace)
    db_session.commit()
    
    brand = Brand(workspace_id=workspace.id, name="Test Brand")
    db_session.add(brand)
    db_session.commit()
    
    creds = {
        "site_url": "https://valid.example.com",
        "username": "admin",
        "app_password": "password"
    }
    
    integ = Integration(
        workspace_id=workspace.id,
        brand_id=brand.id,
        provider="wordpress",
        credentials_encrypted=encrypt(json.dumps(creds)),
        status="CONNECTED"
    )
    db_session.add(integ)
    db_session.commit()
    
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 123, "link": "https://valid.example.com/post/123"}
    mock_post.return_value = mock_response
    
    provider = WordPressProvider()
    
    content_dict = {
        "brand_id": str(brand.id),
        "title": "Test Title",
        "body": "Test Body"
    }
    
    try:
        result = provider.publish(str(workspace.id), content_dict)
        
        assert result["status"] == "success"
        assert result["external_id"] == "123"
        assert result["url"] == "https://valid.example.com/post/123"
        mock_post.assert_called_once()
    finally:
        db_session.query(Integration).filter(Integration.id == integ.id).delete()
        db_session.query(Brand).filter(Brand.id == brand.id).delete()
        db_session.query(Workspace).filter(Workspace.id == workspace.id).delete()
        db_session.commit()
