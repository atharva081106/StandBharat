import pytest
import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.all_models import (
    User, Workspace, Brand, WorkspaceMember, ContentProject, ContentDraft, ContentApproval
)
from app.publishing.models import Publication, PublicationAttempt, PublisherConnection
from app.publishing.service import PublishingService
from app.publishing.tasks import execute_publishing_task

def get_client():
    return TestClient(app)

def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

def setup_tenant(role="OWNER"):
    client = get_client()
    email = unique_email()
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "User"})
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login_resp.cookies.get("access_token")
    client.cookies.set("access_token", token)

    ws_resp = client.post("/api/workspaces/", json={"name": f"WS-{uuid.uuid4().hex[:6]}", "domain": "example.com"})
    ws_id = ws_resp.json()["id"]

    brand_resp = client.post(
        "/api/brands/",
        json={"name": "Brand A", "workspace_id": ws_id},
        headers={"X-Workspace-ID": ws_id}
    )
    brand_id = brand_resp.json()["id"]

    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    user_id = str(user.id)
    if role != "OWNER":
        member = db.query(WorkspaceMember).filter_by(workspace_id=uuid.UUID(ws_id), user_id=user.id).first()
        if member:
            member.role = role
            db.commit()
    db.close()

    headers = {"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}
    return client, ws_id, brand_id, headers, user_id

def create_project_and_draft(client, headers):
    # 1. Project
    p_resp = client.post("/api/content/projects", json={"title": "Test Project"}, headers=headers)
    assert p_resp.status_code == 200
    project_id = p_resp.json()["id"]

    # 2. Add draft via DB directly or API
    db = SessionLocal()
    ws_id = uuid.UUID(headers["X-Workspace-ID"])
    brand_id = uuid.UUID(headers["X-Brand-ID"])
    draft = ContentDraft(
        content_project_id=uuid.UUID(project_id),
        workspace_id=ws_id,
        brand_id=brand_id,
        content_type="BLOG_POST",
        title="Draft Title",
        body="This is real draft content ready for review.",
        status="DRAFT"
    )
    db.add(draft)
    db.commit()
    draft_id = str(draft.id)
    db.close()

    return project_id, draft_id


# =========================================================================
# 1. APPROVE & REJECT WORKFLOWS
# =========================================================================

def test_approve_content_workflow():
    client, ws_id, brand_id, headers, user_id = setup_tenant("OWNER")
    project_id, draft_id = create_project_and_draft(client, headers)

    # Submit for review
    submit_res = client.post(
        f"/api/approvals/projects/{project_id}/submit-review",
        json={"content_draft_id": draft_id},
        headers=headers
    )
    assert submit_res.status_code == 200
    approval = submit_res.json()
    approval_id = approval["id"]
    assert approval["status"] == "PENDING"
    assert approval["draft_title"] == "Draft Title"

    # Verify listing shows pending approval
    list_res = client.get("/api/approvals", headers=headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(i["id"] == approval_id and i["status"] == "PENDING" for i in items)

    # Approve content
    approve_res = client.post(f"/api/approvals/{approval_id}/approve", headers=headers)
    assert approve_res.status_code == 200
    approved_data = approve_res.json()
    assert approved_data["status"] == "APPROVED"
    assert approved_data["reviewed_by"] is not None
    assert approved_data["reviewed_at"] is not None

    # Verify draft status updated to APPROVED
    draft_res = client.get(f"/api/content/drafts/{draft_id}", headers=headers)
    assert draft_res.status_code == 200
    assert draft_res.json()["status"] == "APPROVED"


def test_reject_content_workflow():
    client, ws_id, brand_id, headers, user_id = setup_tenant("ADMIN")
    project_id, draft_id = create_project_and_draft(client, headers)

    # Submit for review
    submit_res = client.post(
        f"/api/approvals/projects/{project_id}/submit-review",
        json={"content_draft_id": draft_id},
        headers=headers
    )
    assert submit_res.status_code == 200
    approval_id = submit_res.json()["id"]

    # Reject content with comment
    reject_res = client.post(
        f"/api/approvals/{approval_id}/reject",
        json={"review_comment": "Tone does not match brand guidelines."},
        headers=headers
    )
    assert reject_res.status_code == 200
    rejected_data = reject_res.json()
    assert rejected_data["status"] == "REJECTED"
    assert rejected_data["review_comment"] == "Tone does not match brand guidelines."

    # Verify draft status updated to REJECTED
    draft_res = client.get(f"/api/content/drafts/{draft_id}", headers=headers)
    assert draft_res.status_code == 200
    assert draft_res.json()["status"] == "REJECTED"


# =========================================================================
# 2. INVALID APPROVAL STATE TRANSITIONS
# =========================================================================

def test_invalid_approval_state_transitions():
    client, ws_id, brand_id, headers, user_id = setup_tenant("OWNER")
    project_id, draft_id = create_project_and_draft(client, headers)

    # Submit for review
    submit_res = client.post(
        f"/api/approvals/projects/{project_id}/submit-review",
        json={"content_draft_id": draft_id},
        headers=headers
    )
    approval_id = submit_res.json()["id"]

    # Prevent duplicate pending approval submission
    dup_res = client.post(
        f"/api/approvals/projects/{project_id}/submit-review",
        json={"content_draft_id": draft_id},
        headers=headers
    )
    assert dup_res.status_code == 400
    assert "already pending" in dup_res.json()["detail"]

    # Approve it
    approve_res = client.post(f"/api/approvals/{approval_id}/approve", headers=headers)
    assert approve_res.status_code == 200

    # Cannot approve already approved
    re_approve = client.post(f"/api/approvals/{approval_id}/approve", headers=headers)
    assert re_approve.status_code == 400
    assert "already approved" in re_approve.json()["detail"]

    # Cannot reject already approved
    reject_approved = client.post(f"/api/approvals/{approval_id}/reject", json={}, headers=headers)
    assert reject_approved.status_code == 400
    assert "Cannot transition approval from APPROVED to REJECTED" in reject_approved.json()["detail"]

    # Cannot request changes on approved
    changes_approved = client.post(f"/api/approvals/{approval_id}/request-changes", json={}, headers=headers)
    assert changes_approved.status_code == 400


# =========================================================================
# 3. UNAUTHORIZED ACCESS & CROSS-TENANT ISOLATION
# =========================================================================

def test_unauthorized_role_cannot_review():
    client_owner, ws_id, brand_id, headers_owner, owner_id = setup_tenant("OWNER")
    project_id, draft_id = create_project_and_draft(client_owner, headers_owner)

    # Submit for review
    sub_res = client_owner.post(
        f"/api/approvals/projects/{project_id}/submit-review",
        json={"content_draft_id": draft_id},
        headers=headers_owner
    )
    assert sub_res.status_code == 200
    app_id = sub_res.json()["id"]

    # Create viewer client in the same workspace
    client_viewer = get_client()
    viewer_email = unique_email()
    client_viewer.post("/api/auth/signup", json={"email": viewer_email, "password": "password123", "name": "Viewer"})
    login_resp = client_viewer.post("/api/auth/login", json={"email": viewer_email, "password": "password123"})
    token = login_resp.cookies.get("access_token")
    client_viewer.cookies.set("access_token", token)

    db = SessionLocal()
    viewer_user = db.query(User).filter_by(email=viewer_email).first()
    db.add(WorkspaceMember(
        workspace_id=uuid.UUID(ws_id),
        user_id=viewer_user.id,
        role="VIEWER"
    ))
    db.commit()
    db.close()

    headers_viewer = {"X-Workspace-ID": ws_id, "X-Brand-ID": brand_id}

    # VIEWER cannot approve
    res = client_viewer.post(f"/api/approvals/{app_id}/approve", headers=headers_viewer)
    assert res.status_code == 403

    # VIEWER cannot reject
    res2 = client_viewer.post(f"/api/approvals/{app_id}/reject", json={}, headers=headers_viewer)
    assert res2.status_code == 403


def test_cross_tenant_isolation():
    # Tenant A
    client_a, ws_a, brand_a, headers_a, user_a = setup_tenant("OWNER")
    proj_a, draft_a = create_project_and_draft(client_a, headers_a)

    sub_res = client_a.post(
        f"/api/approvals/projects/{proj_a}/submit-review",
        json={"content_draft_id": draft_a},
        headers=headers_a
    )
    app_a_id = sub_res.json()["id"]

    # Tenant B
    client_b, ws_b, brand_b, headers_b, user_b = setup_tenant("OWNER")

    # Tenant B tries to get Tenant A's approval -> 404
    get_res = client_b.get(f"/api/approvals/{app_a_id}", headers=headers_b)
    assert get_res.status_code == 404

    # Tenant B tries to approve Tenant A's draft -> 404
    app_res = client_b.post(f"/api/approvals/{app_a_id}/approve", headers=headers_b)
    assert app_res.status_code == 404

    # Tenant B tries to view Tenant A's draft -> 404
    draft_res = client_b.get(f"/api/content/drafts/{draft_a}", headers=headers_b)
    assert draft_res.status_code == 404


# =========================================================================
# 4. PUBLISHING REQUIRES VALID PERSISTED APPROVAL
# =========================================================================

def test_publishing_without_valid_approval_blocked():
    client, ws_id, brand_id, headers, user_id = setup_tenant("OWNER")
    project_id, draft_id = create_project_and_draft(client, headers)

    # 1. No approval record at all
    res = client.post(f"/api/content/drafts/{draft_id}/publish?platform=linkedin", headers=headers)
    assert res.status_code == 409
    assert "Content is not approved for publishing" in res.json()["detail"]

    # 2. PENDING approval
    sub = client.post(f"/api/approvals/projects/{project_id}/submit-review", json={"content_draft_id": draft_id}, headers=headers)
    app_id = sub.json()["id"]

    res_pending = client.post(f"/api/content/drafts/{draft_id}/publish?platform=linkedin", headers=headers)
    assert res_pending.status_code == 409
    assert "Content is not approved for publishing" in res_pending.json()["detail"]

    # 3. REJECTED approval
    client.post(f"/api/approvals/{app_id}/reject", json={"review_comment": "No"}, headers=headers)
    res_rejected = client.post(f"/api/content/drafts/{draft_id}/publish?platform=linkedin", headers=headers)
    assert res_rejected.status_code == 409
    assert "Content is not approved for publishing" in res_rejected.json()["detail"]


# =========================================================================
# 5. WORKER-SIDE APPROVAL REVALIDATION SAFETY
# =========================================================================

def test_worker_revalidation_blocks_unapproved_publication():
    db = SessionLocal()
    try:
        user = User(email=unique_email(), hashed_password="pw")
        db.add(user)
        db.commit()

        ws = Workspace(name="WS", slug=f"ws-{uuid.uuid4().hex[:6]}")
        db.add(ws)
        db.commit()

        brand = Brand(workspace_id=ws.id, name="Brand")
        db.add(brand)
        db.commit()

        proj = ContentProject(workspace_id=ws.id, brand_id=brand.id, title="P", created_by=user.id)
        db.add(proj)
        db.commit()

        draft = ContentDraft(
            content_project_id=proj.id,
            workspace_id=ws.id,
            brand_id=brand.id,
            title="D",
            body="B",
            status="DRAFT"
        )
        db.add(draft)
        db.commit()

        # Notice: NO APPROVED ContentApproval created!
        pub = Publication(
            workspace_id=ws.id,
            brand_id=brand.id,
            content_project_id=proj.id,
            content_draft_id=draft.id,
            platform="linkedin",
            status="QUEUED",
            idempotency_key=f"{ws.id}:{brand.id}:{draft.id}:linkedin",
            created_by=user.id
        )
        db.add(pub)
        db.commit()

        # Invoke worker task directly
        execute_publishing_task(str(pub.id))

        db.refresh(pub)
        assert pub.status == "BLOCKED"
        assert pub.error_code == "APPROVAL_REQUIRED"
    finally:
        db.close()


# =========================================================================
# 6. RECONCILIATION WORKFLOW & BLIND RETRY GUARDS
# =========================================================================

def test_reconciliation_workflow_endpoints():
    client, ws_id, brand_id, headers, user_id = setup_tenant("OWNER")
    project_id, draft_id = create_project_and_draft(client, headers)

    # Approve draft
    sub = client.post(f"/api/approvals/projects/{project_id}/submit-review", json={"content_draft_id": draft_id}, headers=headers)
    app_id = sub.json()["id"]
    client.post(f"/api/approvals/{app_id}/approve", headers=headers)

    # Create a connected publisher connection and a publication marked RECONCILIATION_REQUIRED
    db = SessionLocal()
    conn = PublisherConnection(
        workspace_id=uuid.UUID(ws_id),
        brand_id=uuid.UUID(brand_id),
        platform="linkedin",
        status="CONNECTED"
    )
    db.add(conn)
    pub = Publication(
        workspace_id=uuid.UUID(ws_id),
        brand_id=uuid.UUID(brand_id),
        content_project_id=uuid.UUID(project_id),
        content_draft_id=uuid.UUID(draft_id),
        platform="linkedin",
        status="RECONCILIATION_REQUIRED",
        idempotency_key=f"{ws_id}:{brand_id}:{draft_id}:linkedin",
        created_by=uuid.UUID(user_id)
    )
    db.add(pub)
    db.commit()
    pub_id = str(pub.id)
    db.close()

    # Blind retry via enqueue_publish must be blocked!
    blind_retry = client.post(f"/api/content/drafts/{draft_id}/publish?platform=linkedin", headers=headers)
    assert blind_retry.status_code == 409
    assert "requires reconciliation" in blind_retry.json()["detail"]

    # Reconcile missing external_post_id when PUBLISHED -> HTTP 400
    rec_bad = client.post(
        f"/api/publications/{pub_id}/reconcile",
        json={"resolution": "PUBLISHED"},
        headers=headers
    )
    assert rec_bad.status_code == 400
    assert "external_post_id is required" in rec_bad.json()["detail"]

    # Reconcile with valid external_post_id -> SUCCESS
    rec_ok = client.post(
        f"/api/publications/{pub_id}/reconcile",
        json={"resolution": "PUBLISHED", "external_post_id": "urn:li:share:987654"},
        headers=headers
    )
    assert rec_ok.status_code == 200
    data = rec_ok.json()
    assert data["status"] == "PUBLISHED"
    assert data["external_post_id"] == "urn:li:share:987654"


# =========================================================================
# 7. MISSING DRAFTS & API FAILURES
# =========================================================================

def test_missing_draft_and_api_failures():
    client, ws_id, brand_id, headers, user_id = setup_tenant("OWNER")
    random_id = str(uuid.uuid4())

    # Get non-existent draft
    res_draft = client.get(f"/api/content/drafts/{random_id}", headers=headers)
    assert res_draft.status_code == 404

    # Publish non-existent draft
    res_pub = client.post(f"/api/content/drafts/{random_id}/publish?platform=linkedin", headers=headers)
    assert res_pub.status_code == 404

    # Get non-existent approval
    res_app = client.get(f"/api/approvals/{random_id}", headers=headers)
    assert res_app.status_code == 404


# =========================================================================
# 8. PHASE 34: COMPLETE END-TO-END WORKFLOW & RELIABILITY
# =========================================================================

def test_end_to_end_content_workflow_draft_to_published():
    """
    Traces the complete real database-backed workflow:
    Draft -> Submit Review -> Approve -> Publish -> Queue -> Worker -> Publication Attempt -> Published
    """
    client, ws_id, brand_id, headers, user_id = setup_tenant("OWNER")
    project_id, draft_id = create_project_and_draft(client, headers)

    # 1. Ensure connected publisher
    db = SessionLocal()
    conn = PublisherConnection(
        workspace_id=uuid.UUID(ws_id),
        brand_id=uuid.UUID(brand_id),
        platform="linkedin",
        status="CONNECTED",
        encrypted_credentials="enc"
    )
    db.add(conn)
    db.commit()
    db.close()

    # 2. Submit for Review
    sub_res = client.post(
        f"/api/approvals/projects/{project_id}/submit-review",
        json={"content_draft_id": draft_id},
        headers=headers
    )
    assert sub_res.status_code == 200
    approval_id = sub_res.json()["id"]

    # Verify Draft is IN_REVIEW
    d_review = client.get(f"/api/content/drafts/{draft_id}", headers=headers)
    assert d_review.json()["status"] == "IN_REVIEW"

    # 3. Approve Draft
    app_res = client.post(f"/api/approvals/{approval_id}/approve", headers=headers)
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "APPROVED"

    # Verify Draft is APPROVED
    d_app = client.get(f"/api/content/drafts/{draft_id}", headers=headers)
    assert d_app.json()["status"] == "APPROVED"

    # 4. Publish Draft
    with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
        pub_res = client.post(f"/api/content/drafts/{draft_id}/publish?platform=linkedin", headers=headers)
        assert pub_res.status_code == 200
        pub_data = pub_res.json()
        assert pub_data["status"] == "QUEUED"
        pub_id = pub_data["id"]
        mock_delay.assert_called_once_with(pub_id)

    # 5. Worker execution with mocked external provider
    mock_connector = patch("app.publishing.registry.PublisherRegistry.get_connector").start()
    mock_instance = mock_connector.return_value
    mock_instance.publish.return_value = {"external_id": "urn:li:share:11223344", "status": "CONFIRMED"}

    try:
        execute_publishing_task(pub_id)

        # 6. Verify final published state in database
        db = SessionLocal()
        final_pub = db.query(Publication).filter_by(id=uuid.UUID(pub_id)).first()
        assert final_pub.status == "PUBLISHED"
        assert final_pub.external_post_id == "urn:li:share:11223344"
        assert final_pub.published_at is not None

        # Verify attempt record
        assert len(final_pub.attempts) == 1
        att = final_pub.attempts[0]
        assert att.status == "SUCCESS"
        assert att.response_metadata["external_id"] == "urn:li:share:11223344"
        db.close()
    finally:
        patch.stopall()


def test_concurrent_publish_idempotency():
    client, ws_id, brand_id, headers, user_id = setup_tenant("OWNER")
    project_id, draft_id = create_project_and_draft(client, headers)

    # Approve draft
    sub_res = client.post(f"/api/approvals/projects/{project_id}/submit-review", json={"content_draft_id": draft_id}, headers=headers)
    app_id = sub_res.json()["id"]
    client.post(f"/api/approvals/{app_id}/approve", headers=headers)

    # Add connected publisher
    db = SessionLocal()
    conn = PublisherConnection(
        workspace_id=uuid.UUID(ws_id),
        brand_id=uuid.UUID(brand_id),
        platform="linkedin",
        status="CONNECTED"
    )
    db.add(conn)
    db.commit()
    db.close()

    with patch("app.publishing.tasks.execute_publishing_task.delay"):
        # First publish call
        res1 = client.post(f"/api/content/drafts/{draft_id}/publish?platform=linkedin", headers=headers)
        assert res1.status_code == 200
        pub1 = res1.json()

        # Second publish call (concurrent / repeated idempotency check)
        res2 = client.post(f"/api/content/drafts/{draft_id}/publish?platform=linkedin", headers=headers)
        assert res2.status_code == 200
        pub2 = res2.json()

        # Both return identical publication ID and do not duplicate
        assert pub1["id"] == pub2["id"]
        assert pub1["idempotency_key"] == pub2["idempotency_key"]


def test_sensitive_error_sanitization():
    from app.core.security import sanitize_error_message
    
    # 1. Unit check for sanitizer
    leak1 = "OAuth failed with Bearer ya29.a0AfH6SMD_very_secret_token_12345"
    sanitized1 = sanitize_error_message(leak1)
    assert "ya29.a0AfH6SMD" not in sanitized1
    assert "Bearer [REDACTED]" in sanitized1

    leak2 = "Request URL: https://api.linkedin.com/v2/shares?access_token=secret_token_abcdef12345&client_secret=my_secret_9988"
    sanitized2 = sanitize_error_message(leak2)
    assert "secret_token_abcdef12345" not in sanitized2
    assert "my_secret_9988" not in sanitized2
    assert "[REDACTED]" in sanitized2

    # 2. Worker execution masks sensitive errors when exception is raised
    db = SessionLocal()
    try:
        user = User(email=unique_email(), hashed_password="pw")
        db.add(user)
        db.commit()

        ws = Workspace(name="WS", slug=f"ws-{uuid.uuid4().hex[:6]}")
        db.add(ws)
        db.commit()

        brand = Brand(workspace_id=ws.id, name="Brand")
        db.add(brand)
        db.commit()

        proj = ContentProject(workspace_id=ws.id, brand_id=brand.id, title="P", created_by=user.id)
        db.add(proj)
        db.commit()

        draft = ContentDraft(
            content_project_id=proj.id,
            workspace_id=ws.id,
            brand_id=brand.id,
            title="D",
            body="B",
            status="APPROVED"
        )
        db.add(draft)
        db.commit()

        app = ContentApproval(
            content_project_id=proj.id,
            content_draft_id=draft.id,
            workspace_id=ws.id,
            brand_id=brand.id,
            requested_by=user.id,
            status="APPROVED"
        )
        db.add(app)
        db.commit()

        conn = PublisherConnection(
            workspace_id=ws.id,
            brand_id=brand.id,
            platform="linkedin",
            status="CONNECTED"
        )
        db.add(conn)
        db.commit()

        pub = Publication(
            workspace_id=ws.id,
            brand_id=brand.id,
            content_project_id=proj.id,
            content_draft_id=draft.id,
            platform="linkedin",
            status="QUEUED",
            idempotency_key=f"{ws.id}:{brand.id}:{draft.id}:linkedin",
            created_by=user.id
        )
        db.add(pub)
        db.commit()

        mock_conn = patch("app.publishing.registry.PublisherRegistry.get_connector").start()
        mock_instance = mock_conn.return_value
        mock_instance.publish.side_effect = Exception("HTTP 401: Invalid Bearer secret_live_jwt_token_1234567890")

        execute_publishing_task(str(pub.id))

        db.refresh(pub)
        assert pub.status == "FAILED"
        assert "secret_live_jwt_token_1234567890" not in pub.error_message
        assert "[REDACTED]" in pub.error_message
    finally:
        patch.stopall()
        db.close()

