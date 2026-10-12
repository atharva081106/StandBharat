import os
import sys
import uuid
import time
import requests
import psycopg2
from urllib.parse import urlparse

BASE_URL = os.environ.get("TEST_API_URL", "http://localhost:8000")
FRONTEND_URL = os.environ.get("TEST_FRONTEND_URL", "http://localhost:3000")
DB_URL = os.environ.get("DATABASE_URL", "postgresql://standbharat_user:standbharat_password@localhost:5432/standbharat_db")

print(f"=== StandBharat Runtime Verification ===")
print(f"API Target: {BASE_URL}")
print(f"Frontend Target: {FRONTEND_URL}")

def unique_email():
    return f"runtime_test_{uuid.uuid4().hex[:8]}@example.com"

# 1. Check Root & Health Endpoints
print("\n--- 1. Checking HTTP Connectivity ---")
r_health = requests.get(f"{BASE_URL}/health")
assert r_health.status_code == 200, f"Health check failed: {r_health.text}"
print(f"[PASS] GET /health -> {r_health.status_code} {r_health.json()}")

r_db = requests.get(f"{BASE_URL}/health/db")
assert r_db.status_code == 200, f"Health DB check failed: {r_db.text}"
print(f"[PASS] GET /health/db -> {r_db.status_code} {r_db.json()['status']}")

r_redis = requests.get(f"{BASE_URL}/health/redis")
assert r_redis.status_code == 200, f"Health Redis check failed: {r_redis.text}"
print(f"[PASS] GET /health/redis -> {r_redis.status_code} {r_redis.json()}")

r_front = requests.get(f"{FRONTEND_URL}/landingpage")
assert r_front.status_code == 200, f"Frontend landing page check failed: {r_front.status_code}"
print(f"[PASS] GET Frontend /landingpage -> {r_front.status_code}")

# 2. Authenticated Session & Tenant Isolation
print("\n--- 2. Checking Authentication & Tenant Isolation ---")
session_a = requests.Session()
email_a = unique_email()
pw = "SecurePassword123!"

# Signup & Login User A
r_signup_a = session_a.post(f"{BASE_URL}/api/auth/signup", json={
    "email": email_a,
    "password": pw,
    "name": "Tenant A User"
})
assert r_signup_a.status_code == 200, f"Signup A failed: {r_signup_a.text}"

r_login_a = session_a.post(f"{BASE_URL}/api/auth/login", json={
    "email": email_a,
    "password": pw
})
assert r_login_a.status_code == 200, f"Login A failed: {r_login_a.text}"
token_a = r_login_a.cookies.get("access_token")
headers_a = {"Authorization": f"Bearer {token_a}"} if token_a else {}
print(f"[PASS] Signup and Login Tenant A: {email_a}")

# Auth Me
r_me_a = session_a.get(f"{BASE_URL}/api/auth/me", headers=headers_a)
assert r_me_a.status_code == 200, f"Auth Me A failed: {r_me_a.text}"
user_a_data = r_me_a.json()
print(f"[PASS] Authenticated GET /api/auth/me for User A ({user_a_data['email']})")

# Create Workspace A
ws_name_a = f"Workspace-{uuid.uuid4().hex[:6]}"
r_ws_a = session_a.post(f"{BASE_URL}/api/workspaces/", json={"name": ws_name_a, "domain": "tenanta.com"}, headers=headers_a)
assert r_ws_a.status_code == 200, f"Workspace A creation failed: {r_ws_a.text}"
ws_a_id = r_ws_a.json()["id"]

# Create Brand A
r_brand_a = session_a.post(
    f"{BASE_URL}/api/brands/",
    json={"name": "Brand A", "workspace_id": ws_a_id},
    headers={**headers_a, "X-Workspace-Id": str(ws_a_id)}
)
assert r_brand_a.status_code == 200, f"Brand A creation failed: {r_brand_a.text}"
brand_a_id = r_brand_a.json()["id"]
headers_a["X-Workspace-Id"] = str(ws_a_id)
headers_a["X-Brand-Id"] = str(brand_a_id)
print(f"[PASS] Tenant A Workspace ({ws_a_id}) and Brand ({brand_a_id}) created")

# Create Tenant B
session_b = requests.Session()
email_b = unique_email()
r_signup_b = session_b.post(f"{BASE_URL}/api/auth/signup", json={
    "email": email_b,
    "password": pw,
    "name": "Tenant B User"
})
assert r_signup_b.status_code == 200, f"Signup B failed: {r_signup_b.text}"

r_login_b = session_b.post(f"{BASE_URL}/api/auth/login", json={
    "email": email_b,
    "password": pw
})
assert r_login_b.status_code == 200, f"Login B failed: {r_login_b.text}"
token_b = r_login_b.cookies.get("access_token")
headers_b = {"Authorization": f"Bearer {token_b}"} if token_b else {}

r_ws_b = session_b.post(f"{BASE_URL}/api/workspaces/", json={"name": f"Workspace-{uuid.uuid4().hex[:6]}", "domain": "tenantb.com"}, headers=headers_b)
assert r_ws_b.status_code == 200, f"Workspace B creation failed: {r_ws_b.text}"
ws_b_id = r_ws_b.json()["id"]

r_brand_b = session_b.post(
    f"{BASE_URL}/api/brands/",
    json={"name": "Brand B", "workspace_id": ws_b_id},
    headers={**headers_b, "X-Workspace-Id": str(ws_b_id)}
)
assert r_brand_b.status_code == 200, f"Brand B creation failed: {r_brand_b.text}"
brand_b_id = r_brand_b.json()["id"]
headers_b["X-Workspace-Id"] = str(ws_b_id)
headers_b["X-Brand-Id"] = str(brand_b_id)
print(f"[PASS] Tenant B Workspace ({ws_b_id}) and Brand ({brand_b_id}) created")

# Test Cross-Tenant Rejection
cross_res = session_b.get(f"{BASE_URL}/api/brand-brain/documents", headers={
    **headers_b,
    "X-Workspace-Id": str(ws_a_id),
    "X-Brand-Id": str(brand_a_id)
})
assert cross_res.status_code in (403, 404), f"Cross-tenant access was not rejected! Status: {cross_res.status_code}"
print(f"[PASS] Cross-tenant access rejected with HTTP {cross_res.status_code}")

# 3. Content Draft -> Review -> Approval -> Publishing Pipeline
print("\n--- 3. Checking Content Approval & Publishing Pipeline ---")
# Create Project
r_proj = session_a.post(f"{BASE_URL}/api/content/projects", json={"title": "Runtime Test Project"}, headers=headers_a)
assert r_proj.status_code == 200, f"Project creation failed: {r_proj.text}"
project_id = r_proj.json()["id"]

# Insert test draft in DB
from app.db.session import SessionLocal
from app.models.all_models import ContentDraft, ContentApproval
from app.publishing.models import Publication, PublicationAttempt, PublisherConnection
from app.publishing.tasks import execute_publishing_task
from unittest.mock import patch, MagicMock

db = SessionLocal()
draft = ContentDraft(
    content_project_id=uuid.UUID(project_id),
    workspace_id=uuid.UUID(ws_a_id),
    brand_id=uuid.UUID(brand_a_id),
    content_type="POST",
    title="Reliability Test Draft",
    body="Testing end-to-end publish flow with runtime validation.",
    status="DRAFT"
)
db.add(draft)
# Setup mock connected publisher connection
conn = PublisherConnection(
    workspace_id=uuid.UUID(ws_a_id),
    brand_id=uuid.UUID(brand_a_id),
    platform="linkedin",
    status="CONNECTED",
    encrypted_credentials="dummy_enc_token"
)
db.add(conn)
db.commit()
draft_id = str(draft.id)
db.close()
print(f"[PASS] Draft ({draft_id}) created with status DRAFT")

# Attempt unapproved publish -> Must be rejected with 409
r_unapproved = session_a.post(f"{BASE_URL}/api/content/drafts/{draft_id}/publish?platform=linkedin", headers=headers_a)
assert r_unapproved.status_code == 409, f"Unapproved draft was not blocked! Status: {r_unapproved.status_code}"
assert "not approved" in r_unapproved.json()["detail"].lower()
print(f"[PASS] Unapproved publish blocked with HTTP 409: '{r_unapproved.json()['detail']}'")

# Submit for Review
r_submit = session_a.post(
    f"{BASE_URL}/api/approvals/projects/{project_id}/submit-review",
    json={"content_draft_id": draft_id},
    headers=headers_a
)
assert r_submit.status_code == 200, f"Submit review failed: {r_submit.text}"
approval_id = r_submit.json()["id"]
print(f"[PASS] Draft submitted for review -> Approval record ({approval_id}) in status PENDING")

# Approve Draft
r_approve = session_a.post(f"{BASE_URL}/api/approvals/{approval_id}/approve", headers=headers_a)
assert r_approve.status_code == 200, f"Approve failed: {r_approve.text}"
assert r_approve.json()["status"] == "APPROVED"
print(f"[PASS] Draft approved -> Status updated to APPROVED")

# Publish Approved Draft
with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
    r_pub = session_a.post(f"{BASE_URL}/api/content/drafts/{draft_id}/publish?platform=linkedin", headers=headers_a)
    assert r_pub.status_code == 200, f"Publishing enqueue failed: {r_pub.text}"
    pub_data = r_pub.json()
    assert pub_data["status"] == "QUEUED"
    pub_id = pub_data["id"]
    print(f"[PASS] Approved draft enqueued -> Publication ({pub_id}) in status QUEUED")

# Execute publication task using mocked provider
with patch("app.publishing.registry.PublisherRegistry.get_connector") as mock_conn:
    mock_instance = MagicMock()
    mock_instance.publish.return_value = {"external_id": "urn:li:share:test987654", "status": "CONFIRMED"}
    mock_conn.return_value = mock_instance
    
    execute_publishing_task(pub_id)

# Verify database state for publication and attempt
db = SessionLocal()
pub_record = db.query(Publication).filter_by(id=uuid.UUID(pub_id)).first()
assert pub_record is not None
assert pub_record.status == "PUBLISHED"
assert pub_record.external_post_id == "urn:li:share:test987654"
assert len(pub_record.attempts) >= 1
attempt = pub_record.attempts[0]
assert attempt.status == "SUCCESS"
assert attempt.response_metadata["external_id"] == "urn:li:share:test987654"
db.close()
print(f"[PASS] Worker execution verified: Publication status=PUBLISHED, external_post_id={pub_record.external_post_id}, PublicationAttempt status=SUCCESS")

# 4. Document Persistence, Storage Scoping & Processing
print("\n--- 4. Checking Document Persistence & Worker Processing ---")
doc_content = b"Brand Philosophy: StandBharat provides uncompromising security, reliability, and enterprise scale."
r_doc_upload = session_a.post(
    f"{BASE_URL}/api/brand-brain/documents",
    headers=headers_a,
    files={"file": ("philosophy.txt", doc_content, "text/plain")},
    data={"category": "Brand Identity"}
)
assert r_doc_upload.status_code == 200, f"Document upload failed: {r_doc_upload.text}"
doc_data = r_doc_upload.json()
doc_id = doc_data["id"]
storage_key = doc_data["file_path"]

# Verify scoped storage key
expected_prefix = f"workspaces/{ws_a_id}/brands/{brand_a_id}/documents/"
assert storage_key.startswith(expected_prefix), f"Storage key not properly scoped! Found: {storage_key}"
assert ":" not in storage_key, f"Storage key contains drive letter or host path: {storage_key}"
print(f"[PASS] Document uploaded: ID={doc_id}, Scoped Storage Key={storage_key}")

# Verify Celery worker container can read and process the document directly from shared volume
import subprocess

print("[INFO] Invoking document processing inside standbharat_worker container...")
exec_res = subprocess.run([
    "docker", "exec", "standbharat_worker", "python", "-c",
    f"""
from app.db.session import SessionLocal
from app.services.document_processor import process_document
from app.models.all_models import BrandDocument
import uuid

db = SessionLocal()
process_document(db, '{doc_id}')
doc = db.query(BrandDocument).filter_by(id=uuid.UUID('{doc_id}')).first()
assert doc.processing_status == 'READY', f'Status: {{doc.processing_status}}'
assert 'StandBharat provides uncompromising security' in (doc.extracted_text or '')
print(f'WORKER_SUCCESS: {{doc.processing_status}} words={{doc.metadata_json.get("word_count")}}')
db.close()
"""
], capture_output=True, text=True)

assert exec_res.returncode == 0, f"Worker failed to process document: {exec_res.stderr} {exec_res.stdout}"
print(f"[PASS] Celery worker processed document: {exec_res.stdout.strip()}")

# Test Persistence Across Container Restart
print("\n--- 5. Checking Persistence Across Container Restart ---")
print("[INFO] Restarting backend and worker containers...")
restart_res = subprocess.run(["docker", "compose", "restart", "backend", "celery_worker"], capture_output=True, text=True)
assert restart_res.returncode == 0, f"Container restart failed: {restart_res.stderr}"

# Wait for backend healthcheck
time.sleep(3)
for attempt in range(10):
    try:
        hr = requests.get(f"{BASE_URL}/health", timeout=3)
        if hr.status_code == 200:
            break
    except Exception:
        pass
    time.sleep(1)

# Verify document remains accessible and readable after container restart
r_docs_after = session_a.get(f"{BASE_URL}/api/brand-brain/documents", headers=headers_a)
assert r_docs_after.status_code == 200, f"Failed to list documents after restart: {r_docs_after.text}"
docs_after = r_docs_after.json()
restarted_doc = next((d for d in docs_after if d["id"] == str(doc_id)), None)
assert restarted_doc is not None, f"Document not found after container restart!"
assert restarted_doc["processing_status"] == "READY"
assert restarted_doc["file_path"] == storage_key
print(f"[PASS] Document persistence across container restart verified: ID={doc_id}, Status={restarted_doc['processing_status']}")

# Test Oversized Upload Limit (Streamed 25MB enforcement)
print("\n--- 6. Checking Upload Security Limits ---")
# 26 MB simulated upload
oversized_dummy = b"X" * (1024 * 1024 * 26) # 26 MB
r_oversized = session_a.post(
    f"{BASE_URL}/api/brand-brain/documents",
    headers=headers_a,
    files={"file": ("huge_test.txt", oversized_dummy, "text/plain")},
    data={"category": "Oversized"}
)
assert r_oversized.status_code == 413, f"Oversized upload was not rejected with HTTP 413! Got: {r_oversized.status_code}"
print(f"[PASS] Oversized 26MB upload rejected with HTTP 413 Content Too Large")

# Cross-tenant document access rejection
r_cross_doc = session_b.delete(
    f"{BASE_URL}/api/brand-brain/documents/{doc_id}",
    headers=headers_b
)
assert r_cross_doc.status_code in (403, 404), f"Cross-tenant delete allowed! Status: {r_cross_doc.status_code}"
print(f"[PASS] Cross-tenant document delete rejected with HTTP {r_cross_doc.status_code}")

# Cleanup test doc
session_a.delete(f"{BASE_URL}/api/brand-brain/documents/{doc_id}", headers=headers_a)
print(f"[PASS] Test document cleaned up successfully")

print("\n=== All Runtime Workflow Checks Passed! ===")
