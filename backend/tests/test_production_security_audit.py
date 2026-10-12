import os
import time
import uuid
import hmac
import hashlib
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import Settings, settings
from app.core.security import verify_password, get_password_hash, sanitize_error_message
from app.db.session import SessionLocal
from app.models.all_models import User, Workspace, Brand, WorkspaceMember, BrandDocument, ContentProject, ContentDraft, ContentApproval
from app.publishing.models import Publication, PublisherConnection
from tests.test_isolation_business_overview import setup_user_and_workspace

def get_client():
    return TestClient(app)

def unique_email():
    return f"sec_test_{uuid.uuid4().hex[:8]}@example.com"

# ==============================================================================
# 1. SECRET KEY & CORS VALIDATION IN PRODUCTION
# ==============================================================================

def test_production_rejects_weak_secret_key():
    """Verify that Settings raises a validation error if SECRET_KEY is weak in production."""
    with pytest.raises(ValueError, match="CRITICAL SECURITY DEFECT: In production, SECRET_KEY"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="dev-secret-key-change-in-production"
        )

    with pytest.raises(ValueError, match="CRITICAL SECURITY DEFECT: In production, SECRET_KEY"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="short-key-123" # < 32 chars
        )

def test_production_rejects_wildcard_cors():
    """Verify that Settings raises a validation error if CORS_ORIGINS contains '*' in production."""
    with pytest.raises(ValueError, match="CRITICAL SECURITY DEFECT: In production with credentials enabled, CORS_ORIGINS must not contain wildcard"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a" * 64,
            CORS_ORIGINS=["*"]
        )

def test_production_accepts_strong_secrets_and_specific_cors():
    """Verify that strong secret key and specific origins pass validation in production."""
    valid_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 64,
        CORS_ORIGINS=["https://app.standbharat.com"]
    )
    assert valid_settings.ENVIRONMENT == "production"
    assert valid_settings.SECURE_COOKIES is True
    assert valid_settings.CORS_ORIGINS == ["https://app.standbharat.com"]

# ==============================================================================
# 2. PASSWORD HASHING & 72-BYTE TRUNCATION SAFETY
# ==============================================================================

def test_password_hashing_and_verification():
    pw = "SuperSecurePassword987!"
    h = get_password_hash(pw)
    assert h.startswith("$2b$") or h.startswith("$2a$")
    assert verify_password(pw, h) is True
    assert verify_password("wrong-password", h) is False

def test_password_longer_than_72_bytes_safe_handling():
    """Bcrypt has a 72-byte max password length. Confirm truncation safety without crash."""
    long_pw = "A" * 120
    h = get_password_hash(long_pw)
    assert verify_password(long_pw, h) is True
    assert verify_password("A" * 72, h) is True # Equivalent due to 72-byte truncation
    assert verify_password("B" * 120, h) is False

# ==============================================================================
# 3. SENSITIVE LOG & ERROR SANITIZATION
# ==============================================================================

def test_sensitive_error_sanitization():
    # Database connection string with password
    db_err = "psycopg2.OperationalError: password authentication failed for user 'standbharat_user' at postgresql://standbharat_user:super_secret_pw@db.prod.internal:5432/standbharat_db"
    sanitized_db = sanitize_error_message(db_err)
    assert "super_secret_pw" not in sanitized_db
    assert "[REDACTED]" in sanitized_db

    # Bearer token
    token_err = "Failed request with header Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy_token_payload"
    sanitized_token = sanitize_error_message(token_err)
    assert "dummy_token_payload" not in sanitized_token
    assert "[REDACTED]" in sanitized_token

    # API key query param
    url_err = "Request to https://api.provider.com/v1/posts?access_token=secret_token_12345&client_secret=super_secret_client_key failed"
    sanitized_url = sanitize_error_message(url_err)
    assert "secret_token_12345" not in sanitized_url
    assert "super_secret_client_key" not in sanitized_url

# ==============================================================================
# 4. CROSS-TENANT AUTHORIZATION AUDIT (ACROSS DOMAINS)
# ==============================================================================

def setup_two_tenants():
    client_a, ws_a, brand_a, token_a = setup_user_and_workspace()
    client_b, ws_b, brand_b, token_b = setup_user_and_workspace()
    headers_a = {"Authorization": f"Bearer {token_a}", "X-Workspace-Id": str(ws_a), "X-Brand-Id": str(brand_a)}
    headers_b = {"Authorization": f"Bearer {token_b}", "X-Workspace-Id": str(ws_b), "X-Brand-Id": str(brand_b)}
    return client_a, headers_a, ws_a, brand_a, client_b, headers_b, ws_b, brand_b

def test_cross_tenant_document_isolation():
    client_a, headers_a, ws_a, brand_a, client_b, headers_b, ws_b, brand_b = setup_two_tenants()
    
    # Tenant A uploads a document
    r = client_a.post(
        "/api/brand-brain/documents",
        headers=headers_a,
        files={"file": ("confidential.txt", b"Top Secret Brand Strategy", "text/plain")},
        data={"category": "Strategy"}
    )
    assert r.status_code == 200
    doc_id = r.json()["id"]

    # Tenant B tries to delete Tenant A's document -> 404 or 403
    del_res = client_b.delete(f"/api/brand-brain/documents/{doc_id}", headers=headers_b)
    assert del_res.status_code in (403, 404)

    # Tenant B attempts to manipulate headers with Tenant A's workspace/brand IDs -> 403
    spoofed_headers = {**headers_b, "X-Workspace-Id": str(ws_a), "X-Brand-Id": str(brand_a)}
    spoofed_res = client_b.get("/api/brand-brain/documents", headers=spoofed_headers)
    assert spoofed_res.status_code == 403

def test_cross_tenant_approval_and_publishing_isolation():
    client_a, headers_a, ws_a, brand_a, client_b, headers_b, ws_b, brand_b = setup_two_tenants()

    # Create project and draft for Tenant A
    db = SessionLocal()
    u_a = db.query(WorkspaceMember).filter_by(workspace_id=ws_a).first()
    proj = ContentProject(workspace_id=ws_a, brand_id=brand_a, title="Project A", created_by=u_a.user_id)
    db.add(proj)
    db.commit()

    draft = ContentDraft(
        content_project_id=proj.id,
        workspace_id=ws_a,
        brand_id=brand_a,
        content_type="POST",
        title="Draft A",
        body="Body A",
        status="DRAFT"
    )
    db.add(draft)
    db.commit()
    draft_id = str(draft.id)
    proj_id = str(proj.id)
    db.close()

    # Submit for review
    sub_res = client_a.post(
        f"/api/approvals/projects/{proj_id}/submit-review",
        json={"content_draft_id": draft_id},
        headers=headers_a
    )
    assert sub_res.status_code == 200
    app_id = sub_res.json()["id"]

    # Tenant B tries to view Tenant A's approval -> 404
    assert client_b.get(f"/api/approvals/{app_id}", headers=headers_b).status_code == 404

    # Tenant B tries to approve Tenant A's draft -> 404
    assert client_b.post(f"/api/approvals/{app_id}/approve", headers=headers_b).status_code == 404

    # Tenant B tries to publish Tenant A's draft -> 404
    assert client_b.post(f"/api/content/drafts/{draft_id}/publish?platform=linkedin", headers=headers_b).status_code == 404

def test_cross_tenant_brand_brain_endpoints():
    client_a, headers_a, ws_a, brand_a, client_b, headers_b, ws_b, brand_b = setup_two_tenants()

    # Tenant A creates an audience
    r_aud = client_a.post(
        "/api/brand-brain/audiences",
        json={"name": "Enterprise CTOs", "pain_points": "Legacy infrastructure"},
        headers=headers_a
    )
    assert r_aud.status_code == 200
    aud_id = r_aud.json()["id"]

    # Tenant B tries to delete Tenant A's audience -> 404
    del_aud = client_b.delete(f"/api/brand-brain/audiences/{aud_id}", headers=headers_b)
    assert del_aud.status_code == 404

# ==============================================================================
# 5. OAUTH STATE SIGNATURE & EXPIRATION VERIFICATION
# ==============================================================================

def test_oauth_callback_tampered_state_rejected():
    client = get_client()
    # Random untrusted state
    r = client.get("/api/integrations/oauth/callback?state=fake_state_123&code=sample_code")
    assert r.status_code in (400, 403)

def test_oauth_callback_expired_timestamp_rejected():
    client = get_client()
    ws_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    integration_id = "google_analytics"
    expired_ts = str(int(time.time()) - 3600) # 1 hour ago
    payload = f"{ws_id}:{brand_id}:{integration_id}:{expired_ts}"
    sig = hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    expired_state = f"{payload}:{sig}"

    r = client.get(f"/api/integrations/oauth/callback?state={expired_state}&code=sample_code")
    assert r.status_code == 400
    assert "expired" in r.json()["detail"].lower()
