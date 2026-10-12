# STANDBHARAT — PHASE 32A: PUBLISHING SAFETY AND DISPATCH RELIABILITY REPORT

**Execution Date:** 2026-10-11T20:56:00+05:30  
**Phase:** 32A (Publishing Safety and Dispatch Reliability)  
**Status:** COMPLETE (All requirements verified with automated regression tests)

---

## 1. Executive Summary

Phase 32A fixed the highest-risk backend defects identified in the Phase 31 Content Publishing Pipeline Audit without modifying the frozen Command Center UI or redesigning the integration architecture:
1. **Worker-Level Approval Enforcement**: The Celery background worker now revalidates persisted `ContentApproval` status immediately before calling any external publishing provider, strictly requiring `APPROVED` status for the exact draft, workspace, and brand. Direct task invocation and retries can no longer bypass approval.
2. **Safe Task Dispatch Error Handling**: In `PublishingService.enqueue_publish`, Celery dispatch failures (e.g., broker disconnects) are safely trapped, transitioning the publication to `FAILED` with an actionable `DISPATCH_FAILED` error. No phantom `QUEUED` records are left behind, and idempotency is preserved for subsequent retries.
3. **Comprehensive Regression Testing**: Added 8 regression tests in [`backend/tests/test_publishing.py`](file:///d:/standbharat/backend/tests/test_publishing.py). All 39 combined backend tests passed (`pytest` 100% pass rate), and the frontend production build compiled cleanly (`npm run build` exit code 0).

---

## 2. Code Changes & Defect Remediations

### 2.1 Worker-Level Approval Enforcement
- **File**: [`backend/app/publishing/tasks.py`](file:///d:/standbharat/backend/app/publishing/tasks.py)
- **Defect Fixed**: Previously, `execute_publishing_task` retrieved `Publication` and `ContentDraft` and immediately called `connector.publish()`, bypassing approval checks if tasks were triggered directly or retried after revocation.
- **Implementation**:
  ```python
  # Revalidate ContentApproval status immediately before invoking any external provider
  from app.models.all_models import ContentApproval
  approval = db.query(ContentApproval).filter(
      ContentApproval.content_draft_id == draft.id,
      ContentApproval.workspace_id == publication.workspace_id,
      ContentApproval.brand_id == publication.brand_id
  ).order_by(ContentApproval.created_at.desc()).first()

  if not approval or approval.status != "APPROVED":
      reason = "Approval is missing or revoked" if not approval else f"Content approval status is '{approval.status}', expected 'APPROVED'"
      error_msg = f"Publication blocked: {reason}. Explicit approval is required before publishing."
      
      publication.status = "BLOCKED"
      publication.error_code = "APPROVAL_REQUIRED"
      publication.error_message = error_msg
      
      attempt.status = "BLOCKED"
      attempt.error_code = "APPROVAL_REQUIRED"
      attempt.error_message = error_msg
      attempt.completed_at = datetime.datetime.utcnow()
      
      db.commit()
      return
  ```
- **Retry Protection**: On transient errors (`RATE_LIMITED`, `NETWORK_ERROR`, `PROVIDER_ERROR`), `publication.status = "QUEUED"` is explicitly committed before calling `raise self.retry(...)`. When the retry fires, it re-executes the approval query. If approval was revoked while waiting, the retry transitions the publication to `BLOCKED` instead of publishing.

### 2.2 Task Dispatch Failure Handling
- **File**: [`backend/app/publishing/service.py`](file:///d:/standbharat/backend/app/publishing/service.py)
- **Defect Fixed**: Previously, `enqueue_publish` committed the `QUEUED` publication to the database, but did not wrap `execute_publishing_task.delay()` in exception handling. If Celery dispatch failed, an unhandled exception crashed the request, leaving a phantom `QUEUED` publication in the database.
- **Implementation**:
  ```python
  # Enqueue Celery Task
  from app.publishing.tasks import execute_publishing_task
  try:
      execute_publishing_task.delay(str(publication.id))
  except Exception as e:
      publication.status = "FAILED"
      publication.error_code = "DISPATCH_FAILED"
      publication.error_message = f"Failed to enqueue publishing task: {str(e)}"
      
      attempt_number = str(len(publication.attempts) + 1)
      attempt = PublicationAttempt(
          publication_id=publication.id,
          attempt_number=attempt_number,
          status="FAILED",
          error_code="DISPATCH_FAILED",
          error_message=publication.error_message,
          started_at=datetime.datetime.utcnow(),
          completed_at=datetime.datetime.utcnow()
      )
      self.db.add(attempt)
      self.db.commit()
      
      raise HTTPException(
          status_code=500,
          detail=f"Failed to dispatch publishing task to worker queue: {str(e)}"
      )
  ```
- **Idempotency & Retry**: Because `existing.status` becomes `"FAILED"`, subsequent requests can safely retry the publication using the same idempotency key (`{workspace_id}:{brand_id}:{draft_id}:{platform}`) without duplicate publication records.
- **Integration Model Fallback**: Enhanced `service.get_connection()` to check both `PublisherConnection` and `Integration`, allowing platforms connected through the main Integrations page (e.g., WordPress) to be recognized without throwing false "Not connected" 400 errors.

---

## 3. Verification & Automated Test Evidence

### 3.1 Targeted Publishing Regression Suite (`pytest tests/test_publishing.py`)
```
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\standbharat\backend
collected 8 items

tests\test_publishing.py ........                                        [100%]

============================== 8 passed in 3.89s ==============================
```
**Test Breakdown:**
1. `test_publishing_service_unapproved_draft`: Proves API route rejects unapproved drafts with HTTP 409.
2. `test_publishing_service_success_enqueue`: Proves API route succeeds and enqueues task when draft is approved.
3. `test_worker_blocks_unapproved_content_on_direct_invocation`: Proves that calling `execute_publishing_task` directly without an approval record immediately sets `BLOCKED` and NEVER calls the external provider.
4. `test_worker_blocks_rejected_approval`: Proves that a draft with `REJECTED` status is blocked by the worker.
5. `test_worker_blocks_revoked_approval_on_retry`: Proves that if an approval is revoked between retry attempts, the Celery retry immediately detects the change, transitions to `BLOCKED`, and does not call the provider.
6. `test_dispatch_failure_persists_failed_state_and_preserves_idempotency`: Proves broker dispatch exceptions set `FAILED` state, log a failed attempt, and permit clean recovery retries.
7. `test_worker_enforces_workspace_and_brand_isolation`: Proves that cross-tenant or cross-brand publications fail with `INVALID_CONTENT`.
8. `test_publishing_service_with_integration_fallback`: Proves connections in `Integration` table are recognized by `PublishingService`.

### 3.2 Full Combined Backend Regression Suite
Ran all publishing, social provider, Google integration, dashboard, and OAuth test suites:
```bash
python -m pytest tests/test_publishing.py tests/test_linkedin.py tests/test_wordpress.py tests/test_google_integrations.py tests/test_dashboard.py tests/test_oauth.py
```
**Result**: **39 passed in 17.78s (100% pass rate)**.

### 3.3 Frontend Production Build
Ran production Next.js build:
```bash
npm run build
```
**Result**: **Exit code 0** (Compiled in 3.3s, all 26 static/dynamic routes generated cleanly).

---

## 4. Race Condition & Concurrency Analysis

| Scenario | Risk Before Phase 32A | Mitigation in Phase 32A | Status |
| :--- | :--- | :--- | :---: |
| **Approval Revoked After Enqueue** | Worker publishes unapproved content. | Worker re-checks `ContentApproval` in database immediately before provider call. If revoked, marks `BLOCKED` and exits. | **RESOLVED** |
| **Approval Revoked During Retry Wait** | Worker retries and publishes content whose approval was revoked during backoff. | Transient retry sets `publication.status = "QUEUED"`. On retry wake-up, approval check re-runs and blocks execution if status changed. | **RESOLVED** |
| **Broker Unreachable at Enqueue** | Publication left in phantom `QUEUED` state forever; user cannot retry due to idempotency check. | Trapped in try/except; marked `FAILED` with `DISPATCH_FAILED` error. Subsequent retry is permitted and succeeds once broker recovers. | **RESOLVED** |
| **Concurrent Dispatches on Same Draft** | Double post to external platform. | `idempotency_key` unique constraint + `status in ("PUBLISHED", "PUBLISHING", "QUEUED")` guard returns existing publication without second dispatch. | **RESOLVED** |
| **Worker SIGKILL While Publishing** | Publication remains in `PUBLISHING` status indefinitely. | Requires Celery Beat reaper task (`recover_stale_publications`), scheduled for Phase 32B. | *Phase 32B* |
