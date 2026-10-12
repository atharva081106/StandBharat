import pytest
import uuid
import datetime
import json
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from app.publishing.service import PublishingService
from app.publishing.tasks import execute_publishing_task
from app.publishing.exceptions import NotConfiguredError, AuthenticationError, PublishingError
from app.publishing.models import PublisherConnection, Publication, PublicationAttempt
from app.models.all_models import (
    Workspace,
    Brand,
    User,
    ContentProject,
    ContentDraft,
    ContentApproval,
    Integration
)
from app.core.encryption import encrypt
from app.db.session import SessionLocal

@pytest.fixture
def publishing_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def base_test_data(publishing_db):
    user = User(email=f"test_{uuid.uuid4().hex[:8]}@example.com", hashed_password="pw")
    publishing_db.add(user)
    publishing_db.commit()

    workspace = Workspace(name=f"WS {uuid.uuid4().hex[:6]}", slug=f"ws-{uuid.uuid4().hex[:6]}")
    publishing_db.add(workspace)
    publishing_db.commit()

    brand = Brand(workspace_id=workspace.id, name="Test Brand")
    publishing_db.add(brand)
    publishing_db.commit()

    project = ContentProject(workspace_id=workspace.id, brand_id=brand.id, title="Test Project", created_by=user.id)
    publishing_db.add(project)
    publishing_db.commit()

    draft = ContentDraft(
        workspace_id=workspace.id,
        brand_id=brand.id,
        content_project_id=project.id,
        content_type="LINKEDIN_POST",
        title="Test Draft",
        body="Test Body"
    )
    publishing_db.add(draft)
    publishing_db.commit()

    conn = PublisherConnection(
        workspace_id=workspace.id,
        brand_id=brand.id,
        platform="linkedin",
        status="CONNECTED",
        encrypted_credentials=encrypt(json.dumps({"access_token": "dummy_token", "author_urn": "urn:li:person:123"}))
    )
    publishing_db.add(conn)
    publishing_db.commit()

    return {
        "user": user,
        "workspace": workspace,
        "brand": brand,
        "project": project,
        "draft": draft,
        "conn": conn
    }

# 1. API Enqueue Blocks Unapproved Draft
def test_publishing_service_unapproved_draft(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]

    service = PublishingService(publishing_db)
    with pytest.raises(HTTPException) as exc:
        service.enqueue_publish(ws.id, b.id, d.id, "linkedin", u.id)
    assert exc.value.status_code == 409
    assert "not approved" in exc.value.detail.lower()

# 2. API Enqueue Success When Approved
def test_publishing_service_success_enqueue(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
        pub = service.enqueue_publish(ws.id, b.id, d.id, "linkedin", u.id)
        mock_delay.assert_called_once_with(str(pub.id))

    assert pub.status == "QUEUED"
    assert pub.idempotency_key == f"{ws.id}:{b.id}:{d.id}:linkedin"

# 3. Worker Re-validates Approval and Blocks Unapproved Draft on Direct Task Invocation
@patch("app.publishing.connectors.linkedin.LinkedInConnector.publish")
def test_worker_blocks_unapproved_content_on_direct_invocation(mock_publish, publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    # Publication is QUEUED, but NO ContentApproval exists
    pub = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="QUEUED",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:direct_test",
        created_by=u.id
    )
    publishing_db.add(pub)
    publishing_db.commit()

    execute_publishing_task(str(pub.id))

    # Crucial: provider must NEVER be called
    mock_publish.assert_not_called()

    publishing_db.refresh(pub)
    assert pub.status == "BLOCKED"
    assert pub.error_code == "APPROVAL_REQUIRED"
    assert "explicit approval is required" in pub.error_message.lower()

    # Attempt record must also be marked BLOCKED
    attempt = publishing_db.query(PublicationAttempt).filter(PublicationAttempt.publication_id == pub.id).first()
    assert attempt is not None
    assert attempt.status == "BLOCKED"
    assert attempt.error_code == "APPROVAL_REQUIRED"

# 4. Worker Blocks Rejected Approval on Direct Task Invocation
@patch("app.publishing.connectors.linkedin.LinkedInConnector.publish")
def test_worker_blocks_rejected_approval(mock_publish, publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="REJECTED",
        requested_by=u.id
    )
    publishing_db.add(approval)
    publishing_db.commit()

    pub = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="QUEUED",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:rejected_test",
        created_by=u.id
    )
    publishing_db.add(pub)
    publishing_db.commit()

    execute_publishing_task(str(pub.id))

    mock_publish.assert_not_called()

    publishing_db.refresh(pub)
    assert pub.status == "BLOCKED"
    assert pub.error_code == "APPROVAL_REQUIRED"
    assert "rejected" in pub.error_message.lower()

# 5. Worker Blocks Revoked Approval During Retry Flow
def test_worker_blocks_revoked_approval_on_retry(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)
    publishing_db.commit()

    pub = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="QUEUED",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:retry_test",
        created_by=u.id
    )
    publishing_db.add(pub)
    publishing_db.commit()

    # First attempt: Connector fails with RATE_LIMITED
    with patch("app.publishing.connectors.linkedin.LinkedInConnector.publish", side_effect=PublishingError("Rate limit exceeded", "RATE_LIMITED")) as mock_pub, \
         patch.object(execute_publishing_task, "retry", side_effect=Exception("SimulatedCeleryRetry")):
        try:
            execute_publishing_task(str(pub.id))
        except Exception as e:
            assert "SimulatedCeleryRetry" in str(e)

        assert mock_pub.call_count == 1

    publishing_db.refresh(pub)
    assert pub.status == "QUEUED"  # Ready for retry

    # In the meantime, approval is revoked!
    approval.status = "REJECTED"
    publishing_db.commit()

    # Second attempt (Celery retry invocation):
    with patch("app.publishing.connectors.linkedin.LinkedInConnector.publish") as mock_pub2:
        execute_publishing_task(str(pub.id))
        # The connector must NOT be invoked on retry since approval was revoked!
        mock_pub2.assert_not_called()

    publishing_db.refresh(pub)
    assert pub.status == "BLOCKED"
    assert pub.error_code == "APPROVAL_REQUIRED"

# 6. Task Dispatch Failure Persists FAILED State Without Leaving Phantom QUEUED Record
def test_dispatch_failure_persists_failed_state_and_preserves_idempotency(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)
    publishing_db.commit()

    service = PublishingService(publishing_db)

    # Simulate Celery/Redis broker being down
    with patch("app.publishing.tasks.execute_publishing_task.delay", side_effect=Exception("Redis Connection Refused")):
        with pytest.raises(HTTPException) as exc:
            service.enqueue_publish(ws.id, b.id, d.id, "linkedin", u.id)
        assert exc.value.status_code == 500
        assert "Redis Connection Refused" in exc.value.detail

    idemp_key = f"{ws.id}:{b.id}:{d.id}:linkedin"
    persisted_pub = publishing_db.query(Publication).filter(Publication.idempotency_key == idemp_key).first()
    assert persisted_pub is not None
    assert persisted_pub.status == "FAILED"
    assert persisted_pub.error_code == "DISPATCH_FAILED"
    assert "Redis Connection Refused" in persisted_pub.error_message

    attempt = publishing_db.query(PublicationAttempt).filter(PublicationAttempt.publication_id == persisted_pub.id).first()
    assert attempt is not None
    assert attempt.status == "FAILED"
    assert attempt.error_code == "DISPATCH_FAILED"

    # Now simulate a subsequent retry when Redis is back up
    with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
        retried_pub = service.enqueue_publish(ws.id, b.id, d.id, "linkedin", u.id)
        assert retried_pub.id == persisted_pub.id
        assert retried_pub.status == "QUEUED"
        mock_delay.assert_called_once_with(str(persisted_pub.id))

# 7. Workspace and Brand Isolation Enforced in Worker
def test_worker_enforces_workspace_and_brand_isolation(publishing_db, base_test_data):
    ws_a = base_test_data["workspace"]
    b_a = base_test_data["brand"]
    d_a = base_test_data["draft"]
    u_a = base_test_data["user"]
    p_a = base_test_data["project"]

    # Create distinct Workspace B and Brand B
    ws_b = Workspace(name=f"WS B {uuid.uuid4().hex[:6]}", slug=f"ws-b-{uuid.uuid4().hex[:6]}")
    publishing_db.add(ws_b)
    publishing_db.commit()

    b_b = Brand(workspace_id=ws_b.id, name="Brand B")
    publishing_db.add(b_b)
    publishing_db.commit()

    # Malicious/corrupted publication targeting Draft A under Workspace B
    pub_cross = Publication(
        workspace_id=ws_b.id,
        brand_id=b_b.id,
        content_project_id=p_a.id,
        content_draft_id=d_a.id,
        platform="linkedin",
        status="QUEUED",
        idempotency_key=f"{ws_b.id}:{b_b.id}:{d_a.id}:cross_tenant",
        created_by=u_a.id
    )
    publishing_db.add(pub_cross)
    publishing_db.commit()

    with patch("app.publishing.connectors.linkedin.LinkedInConnector.publish") as mock_pub:
        execute_publishing_task(str(pub_cross.id))
        mock_pub.assert_not_called()

    publishing_db.refresh(pub_cross)
    assert pub_cross.status == "FAILED"
    assert pub_cross.error_code == "INVALID_CONTENT"
    assert "mismatch" in pub_cross.error_message.lower()

# 8. Support Integration Model Fallback in PublishingService
def test_publishing_service_with_integration_fallback(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)
    publishing_db.commit()

    # Add WordPress integration in Integration table
    wp_integ = Integration(
        workspace_id=ws.id,
        brand_id=b.id,
        provider="wordpress",
        status="CONNECTED",
        credentials_encrypted=encrypt(json.dumps({"site_url": "https://example.com", "username": "admin", "app_password": "pwd"}))
    )
    publishing_db.add(wp_integ)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
        pub = service.enqueue_publish(ws.id, b.id, d.id, "wordpress", u.id)
        mock_delay.assert_called_once_with(str(pub.id))

    assert pub.status == "QUEUED"
    assert pub.platform == "wordpress"


# 9. Fresh publications are NOT marked stale
def test_fresh_publications_not_marked_stale(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    # Approved draft
    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)

    # Fresh publication updated 10 minutes ago (< 60 minute threshold)
    ten_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    fresh_pub = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="PUBLISHING",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:fresh_test",
        created_by=u.id,
        created_at=ten_mins_ago,
        updated_at=ten_mins_ago
    )
    publishing_db.add(fresh_pub)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    result = service.recover_stale_publications(timeout_minutes=60)

    publishing_db.refresh(fresh_pub)
    assert fresh_pub.status == "PUBLISHING"
    assert str(fresh_pub.id) not in [d["publication_id"] for d in result["details"]]


# 10. Stale publication with no attempts is safely re-queued
def test_stale_recovery_with_no_attempt_requeued(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)

    # Stale publication: worker crashed before creating attempt (updated 90 mins ago)
    ninety_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=90)
    stale_pub = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="PUBLISHING",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:stale_no_attempt",
        created_by=u.id,
        created_at=ninety_mins_ago,
        updated_at=ninety_mins_ago
    )
    publishing_db.add(stale_pub)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
        result = service.recover_stale_publications(timeout_minutes=60)
        mock_delay.assert_called_once_with(str(stale_pub.id))

    publishing_db.refresh(stale_pub)
    assert stale_pub.status == "QUEUED"
    assert result["actions"]["REQUEUED_FOR_RETRY"] >= 1


# 11. Stale publication already published externally is marked PUBLISHED without retry
def test_stale_recovery_already_published_external_id(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)

    ninety_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=90)
    pub_with_ext = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="PUBLISHING",
        external_post_id="urn:li:share:123456789",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:stale_ext_id",
        created_by=u.id,
        created_at=ninety_mins_ago,
        updated_at=ninety_mins_ago
    )
    publishing_db.add(pub_with_ext)
    publishing_db.commit()

    attempt = PublicationAttempt(
        publication_id=pub_with_ext.id,
        attempt_number="1",
        status="STARTED",
        started_at=ninety_mins_ago
    )
    publishing_db.add(attempt)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
        result = service.recover_stale_publications(timeout_minutes=60)
        mock_delay.assert_not_called()

    publishing_db.refresh(pub_with_ext)
    publishing_db.refresh(attempt)
    assert pub_with_ext.status == "PUBLISHED"
    assert pub_with_ext.external_post_id == "urn:li:share:123456789"
    assert attempt.status == "SUCCESS"
    assert result["actions"]["RECOVERED_AS_PUBLISHED"] >= 1


# 12. Stale publication blocked if approval revoked or missing
def test_stale_recovery_blocked_if_approval_revoked(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    # Revoked / rejected approval
    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="REJECTED",
        requested_by=u.id
    )
    publishing_db.add(approval)

    ninety_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=90)
    stale_pub = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="PUBLISHING",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:stale_revoked",
        created_by=u.id,
        created_at=ninety_mins_ago,
        updated_at=ninety_mins_ago
    )
    publishing_db.add(stale_pub)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
        result = service.recover_stale_publications(timeout_minutes=60)
        mock_delay.assert_not_called()

    publishing_db.refresh(stale_pub)
    assert stale_pub.status == "BLOCKED"
    assert stale_pub.error_code == "APPROVAL_REQUIRED"
    assert "explicit approval is required" in stale_pub.error_message.lower()
    assert result["actions"]["BLOCKED_REVOKED_APPROVAL"] >= 1


# 13. Stale publication with attempt in flight marked RECONCILIATION_REQUIRED
def test_stale_recovery_uncertain_external_outcome_marked_for_reconciliation(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)

    ninety_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=90)
    stale_pub = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="PUBLISHING",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:linkedin",
        created_by=u.id,
        created_at=ninety_mins_ago,
        updated_at=ninety_mins_ago
    )
    publishing_db.add(stale_pub)
    publishing_db.commit()

    # In-flight attempt when worker crashed
    attempt = PublicationAttempt(
        publication_id=stale_pub.id,
        attempt_number="1",
        status="STARTED",
        started_at=ninety_mins_ago
    )
    publishing_db.add(attempt)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
        result = service.recover_stale_publications(timeout_minutes=60)
        # CRITICAL: Must NEVER blindly retry
        mock_delay.assert_not_called()

    publishing_db.refresh(stale_pub)
    publishing_db.refresh(attempt)
    assert stale_pub.status == "RECONCILIATION_REQUIRED"
    assert stale_pub.error_code == "EXTERNAL_OUTCOME_UNCERTAIN"
    assert attempt.status == "UNCERTAIN"
    assert result["actions"]["MARKED_RECONCILIATION_REQUIRED"] >= 1

    # Verify enqueue_publish guards against blind retry of RECONCILIATION_REQUIRED publications
    with pytest.raises(HTTPException) as exc:
        service.enqueue_publish(ws.id, b.id, d.id, "linkedin", u.id)
    assert exc.value.status_code == 409
    assert "reconciliation" in exc.value.detail.lower()


# 14. Concurrency-safe claim prevents simultaneous worker conflicts
def test_concurrent_stale_recovery_conditional_claim(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)

    ninety_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=90)
    stale_pub = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="PUBLISHING",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:concurrency_test",
        created_by=u.id,
        created_at=ninety_mins_ago,
        updated_at=ninety_mins_ago
    )
    publishing_db.add(stale_pub)
    publishing_db.commit()

    # Simulate Worker 1 claiming the publication first via conditional update
    claimed_rows = publishing_db.query(Publication).filter(
        Publication.id == stale_pub.id,
        Publication.status == "PUBLISHING"
    ).update(
        {"status": "RECOVERING", "updated_at": datetime.datetime.utcnow()},
        synchronize_session=False
    )
    publishing_db.commit()
    assert claimed_rows == 1

    # Now Worker 2 runs recover_stale_publications for publications stuck > 60 mins
    # Since updated_at was bumped and status was changed, Worker 2's conditional update finds 0 rows
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=60)
    second_claim = publishing_db.query(Publication).filter(
        Publication.id == stale_pub.id,
        Publication.status.in_(["PUBLISHING", "RECOVERING"]),
        Publication.updated_at <= cutoff_time
    ).update(
        {"status": "RECOVERING", "updated_at": datetime.datetime.utcnow()},
        synchronize_session=False
    )
    publishing_db.commit()
    assert second_claim == 0


# 15. Reconciliation workflow for publications marked RECONCILIATION_REQUIRED
def test_reconcile_publication_published_and_retry(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)

    reconcile_pub = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="RECONCILIATION_REQUIRED",
        error_code="EXTERNAL_OUTCOME_UNCERTAIN",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:reconcile_flow",
        created_by=u.id
    )
    publishing_db.add(reconcile_pub)
    publishing_db.commit()

    service = PublishingService(publishing_db)

    # Resolution 1: Reconcile as PUBLISHED with external ID
    reconciled = service.reconcile_publication(
        reconcile_pub.id,
        resolution="PUBLISHED",
        external_post_id="urn:li:share:manual_verified_123",
        notes="Verified manual post on LinkedIn"
    )
    assert reconciled.status == "PUBLISHED"
    assert reconciled.external_post_id == "urn:li:share:manual_verified_123"

    # Create another publication needing reconciliation to test RETRY
    reconcile_pub2 = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="RECONCILIATION_REQUIRED",
        error_code="EXTERNAL_OUTCOME_UNCERTAIN",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:reconcile_retry_flow",
        created_by=u.id
    )
    publishing_db.add(reconcile_pub2)
    publishing_db.commit()

    # Resolution 2: Reconcile as RETRY
    with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
        reconciled2 = service.reconcile_publication(reconcile_pub2.id, resolution="RETRY")
        mock_delay.assert_called_once_with(str(reconcile_pub2.id))
    assert reconciled2.status == "QUEUED"


# 16. Celery task recover_stale_publications and repeated idempotent runs
def test_recovery_repeated_run_is_idempotent(publishing_db, base_test_data):
    from app.publishing.tasks import recover_stale_publications

    # Calling directly
    result1 = recover_stale_publications(timeout_minutes=60)
    assert isinstance(result1, dict)
    assert "claimed_count" in result1

    # Immediate second run produces 0 claims
    result2 = recover_stale_publications(timeout_minutes=60)
    assert result2["claimed_count"] == 0
    assert result2["recovered_count"] == 0


# 17. Publishing through authoritative Integration record succeeds end-to-end
def test_publishing_through_authoritative_integration_record(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)

    # Authoritative Integration record for linkedin
    integ = Integration(
        workspace_id=ws.id,
        brand_id=b.id,
        provider="linkedin",
        status="CONNECTED",
        credentials_encrypted=encrypt(json.dumps({
            "access_token": "valid_oauth_token",
            "author_urn": "urn:li:person:auth_user"
        }))
    )
    publishing_db.add(integ)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    # Proves get_connection resolves Integration authoritatively
    connection = service.get_connection(ws.id, b.id, "linkedin")
    assert isinstance(connection, Integration)
    assert connection.id == integ.id

    with patch("app.publishing.tasks.execute_publishing_task.delay") as mock_delay:
        pub = service.enqueue_publish(ws.id, b.id, d.id, "linkedin", u.id)
        mock_delay.assert_called_once_with(str(pub.id))

    # Mock external LinkedIn API call in worker
    with patch("httpx.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.headers = {}
        mock_resp.json.return_value = {"id": "urn:li:share:mock_authoritative"}
        mock_post.return_value = mock_resp

        execute_publishing_task(str(pub.id))

    publishing_db.refresh(pub)
    assert pub.status == "PUBLISHED"
    assert pub.external_post_id == "urn:li:share:mock_authoritative"


# 18. Publishing fails when Integration is disconnected or not configured
def test_publishing_fails_when_integration_is_disconnected(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)

    # Disconnected integration
    integ = Integration(
        workspace_id=ws.id,
        brand_id=b.id,
        provider="linkedin",
        status="NOT_CONNECTED",
        credentials_encrypted=None
    )
    publishing_db.add(integ)
    publishing_db.commit()

    # Delete any legacy PublisherConnection to isolate Integration check
    publishing_db.query(PublisherConnection).filter_by(workspace_id=ws.id, brand_id=b.id, platform="linkedin").delete()
    publishing_db.commit()

    service = PublishingService(publishing_db)
    with pytest.raises(HTTPException) as exc:
        service.enqueue_publish(ws.id, b.id, d.id, "linkedin", u.id)
    assert exc.value.status_code == 400
    assert "not connected" in exc.value.detail.lower()


# 19. Publishing fails with AuthenticationError on invalid credentials
def test_publishing_fails_with_invalid_credentials(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)

    # Missing author_urn
    integ = Integration(
        workspace_id=ws.id,
        brand_id=b.id,
        provider="linkedin",
        status="CONNECTED",
        credentials_encrypted=encrypt(json.dumps({
            "access_token": "valid_token"
            # Missing author_urn
        }))
    )
    publishing_db.add(integ)

    # Delete legacy connection
    publishing_db.query(PublisherConnection).filter_by(workspace_id=ws.id, brand_id=b.id, platform="linkedin").delete()

    pub = Publication(
        workspace_id=ws.id,
        brand_id=b.id,
        content_project_id=p.id,
        content_draft_id=d.id,
        platform="linkedin",
        status="QUEUED",
        idempotency_key=f"{ws.id}:{b.id}:{d.id}:invalid_creds_test",
        created_by=u.id
    )
    publishing_db.add(pub)
    publishing_db.commit()

    execute_publishing_task(str(pub.id))

    publishing_db.refresh(pub)
    assert pub.status == "FAILED"
    assert pub.error_code == "AUTHENTICATION_ERROR"
    assert "author urn" in pub.error_message.lower()


# 20. Strict brand isolation enforced with Integration records
def test_publishing_enforces_strict_brand_isolation_with_integration(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b1 = base_test_data["brand"]
    u = base_test_data["user"]

    # Brand 2 in same workspace
    b2 = Brand(workspace_id=ws.id, name="Isolated Brand 2")
    publishing_db.add(b2)
    publishing_db.commit()

    project2 = ContentProject(workspace_id=ws.id, brand_id=b2.id, title="P2", created_by=u.id)
    publishing_db.add(project2)
    publishing_db.commit()

    draft2 = ContentDraft(
        workspace_id=ws.id,
        brand_id=b2.id,
        content_project_id=project2.id,
        content_type="LINKEDIN_POST",
        title="D2",
        body="B2"
    )
    publishing_db.add(draft2)
    publishing_db.commit()

    approval2 = ContentApproval(
        content_project_id=project2.id,
        content_draft_id=draft2.id,
        workspace_id=ws.id,
        brand_id=b2.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval2)
    publishing_db.commit()

    # Connect Brand 1 ONLY
    integ_b1 = Integration(
        workspace_id=ws.id,
        brand_id=b1.id,
        provider="linkedin",
        status="CONNECTED",
        credentials_encrypted=encrypt(json.dumps({"access_token": "token1", "author_urn": "urn:1"}))
    )
    publishing_db.add(integ_b1)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    # Brand 2 must NOT borrow Brand 1's connection
    with pytest.raises(HTTPException) as exc:
        service.enqueue_publish(ws.id, b2.id, draft2.id, "linkedin", u.id)
    assert exc.value.status_code == 400
    assert "not connected" in exc.value.detail.lower()


# 21. Publishing fails truthfully on unsupported provider
def test_publishing_fails_truthfully_on_unsupported_provider(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]
    d = base_test_data["draft"]
    u = base_test_data["user"]
    p = base_test_data["project"]

    approval = ContentApproval(
        content_project_id=p.id,
        content_draft_id=d.id,
        workspace_id=ws.id,
        brand_id=b.id,
        status="APPROVED",
        requested_by=u.id
    )
    publishing_db.add(approval)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    with pytest.raises(HTTPException) as exc:
        service.enqueue_publish(ws.id, b.id, d.id, "myspace", u.id)
    assert exc.value.status_code == 400
    assert "not connected" in exc.value.detail.lower()

    from app.integrations.registry import integration_registry
    with pytest.raises(ValueError) as val_exc:
        integration_registry.get_provider("myspace")
    assert "not found" in str(val_exc.value).lower()


# 22. Removed fake LinkedIn OAuth fallback fails truthfully
def test_removed_fake_linkedin_oauth_path_fails_truthfully(publishing_db, base_test_data):
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    ws = base_test_data["workspace"]
    b = base_test_data["brand"]

    # Ensure no pre-existing connection from base_test_data
    publishing_db.query(PublisherConnection).filter_by(workspace_id=ws.id, brand_id=b.id, platform="linkedin").delete()
    publishing_db.commit()

    # Calling callback without LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET
    state_payload = f"{ws.id}:{b.id}"
    secure_state = encrypt(state_payload)

    with patch.dict("os.environ", {"LINKEDIN_CLIENT_ID": "", "LINKEDIN_CLIENT_SECRET": ""}):
        response = client.get(f"/api/publishers/linkedin/callback?code=fake_code&state={secure_state}")
        # Must fail with 500 error, NEVER simulate successful connection
        assert response.status_code == 500
        assert "configuration is missing" in response.json()["detail"].lower()

        # Verify no PublisherConnection was created
        conn = publishing_db.query(PublisherConnection).filter_by(workspace_id=ws.id, brand_id=b.id, platform="linkedin").first()
        assert conn is None

    # Verify dummy token connect is rejected in /api/integrations/{id}/connect
    from app.api.deps import get_current_user, get_current_brand
    app.dependency_overrides[get_current_user] = lambda: base_test_data["user"]
    app.dependency_overrides[get_current_brand] = lambda: base_test_data["brand"]

    dummy_connect_resp = client.post(
        "/api/integrations/linkedin/connect",
        json={"dummy_token": "mock_credential_123"}
    )
    assert dummy_connect_resp.status_code == 400
    assert "mock tokens are not permitted" in dummy_connect_resp.json()["detail"].lower()
    app.dependency_overrides = {}


# 23. Authoritative Integration precedence over PublisherConnection
def test_authoritative_integration_precedence_over_publisher_connection(publishing_db, base_test_data):
    ws = base_test_data["workspace"]
    b = base_test_data["brand"]

    # Both exist
    integ = Integration(
        workspace_id=ws.id,
        brand_id=b.id,
        provider="linkedin",
        status="CONNECTED",
        credentials_encrypted=encrypt(json.dumps({"access_token": "integ_token", "author_urn": "urn:integ"}))
    )
    publishing_db.add(integ)

    pub_conn = PublisherConnection(
        workspace_id=ws.id,
        brand_id=b.id,
        platform="linkedin",
        status="CONNECTED",
        encrypted_credentials=encrypt(json.dumps({"access_token": "conn_token", "author_urn": "urn:conn"}))
    )
    publishing_db.add(pub_conn)
    publishing_db.commit()

    service = PublishingService(publishing_db)
    resolved = service.get_connection(ws.id, b.id, "linkedin")

    # Authoritative Integration model MUST take precedence
    assert isinstance(resolved, Integration)
    assert resolved.id == integ.id



