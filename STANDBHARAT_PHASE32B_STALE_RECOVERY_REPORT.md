# STANDBHARAT — PHASE 32B: STALE PUBLICATION RECOVERY REPORT

**Execution Date:** 2026-10-11T21:18:00+05:30  
**Phase:** 32B (Stale Publication Recovery)  
**Status:** COMPLETE (All requirements verified with automated regression tests)

---

## 1. Executive Summary

Phase 32B designed and implemented automated, concurrency-safe recovery for content publication jobs that become stuck in `PUBLISHING` status following unexpected worker crashes (e.g. `SIGKILL`, host restarts, OOM events).
1. **Configurable Stale Timeout & Cutoff**: Stale publications are identified when `status in ("PUBLISHING", "RECOVERING")` and `updated_at <= cutoff_time` (default 60 minutes / 1 hour), configurable via `settings.STALE_PUBLICATION_TIMEOUT_MINUTES` or per-call parameters.
2. **Concurrency-Safe Conditional Database Updates**: Prevents race conditions and double claims between concurrent recovery processes by executing atomic SQL updates:
   ```python
   claim_count = db.query(Publication).filter(
       Publication.id == candidate_id,
       Publication.status.in_(["PUBLISHING", "RECOVERING"]),
       Publication.updated_at <= cutoff_time
   ).update({"status": "RECOVERING", "updated_at": datetime.datetime.utcnow()}, synchronize_session=False)
   ```
   Only the worker that obtains `claim_count == 1` acquires exclusive ownership of the recovery lifecycle.
3. **External Outcome Safety & Reconciliation Guard**: 
   - Never blindly republishes when an external outcome is uncertain. If an attempt was in-flight (`status in ("STARTED", "RECOVERING")`) without confirmed provider response or `external_post_id`, the publication transitions to `RECONCILIATION_REQUIRED` (`error_code="EXTERNAL_OUTCOME_UNCERTAIN"`).
   - Guarded [`PublishingService.enqueue_publish`](file:///d:/standbharat/backend/app/publishing/service.py#L60) to reject re-publishing of publications requiring reconciliation with HTTP 409.
   - Implemented [`PublishingService.reconcile_publication`](file:///d:/standbharat/backend/app/publishing/service.py#L351) for deterministic resolution (`PUBLISHED`, `FAILED`, `RETRY`).
4. **Approval Revalidation During Recovery**: Draft approval is revalidated against [`ContentApproval`](file:///d:/standbharat/backend/app/models/all_models.py#L380) for the exact draft, workspace, and brand. If approval was revoked or rejected while the task was stuck, the publication transitions to `BLOCKED`.
5. **Periodic Celery Beat Scheduling**: Registered `'recover-stale-publications-every-30-minutes'` in Celery Beat with complete idempotency across repeated runs.

---

## 2. Changed Files & Implementation Details

### 2.1 Configuration
- **File:** [`backend/app/core/config.py`](file:///d:/standbharat/backend/app/core/config.py)
- **Changes:** Added `STALE_PUBLICATION_TIMEOUT_MINUTES: int = 60` to [`Settings`](file:///d:/standbharat/backend/app/core/config.py#L5) with environment file support.

### 2.2 Celery Beat Task Registration
- **File:** [`backend/app/core/celery_app.py`](file:///d:/standbharat/backend/app/core/celery_app.py)
- **Changes:** Added `'recover-stale-publications-every-30-minutes'` to `celery_app.conf.beat_schedule`:
  ```python
  'recover-stale-publications-every-30-minutes': {
      'task': 'recover_stale_publications',
      'schedule': crontab(minute='*/30'),
  },
  ```

### 2.3 Recovery Service & Reconciliation Logic
- **File:** [`backend/app/publishing/service.py`](file:///d:/standbharat/backend/app/publishing/service.py)
- **Changes:**
  - Implemented [`PublishingService.recover_stale_publications`](file:///d:/standbharat/backend/app/publishing/service.py#L156):
    - Atomic conditional updates claim stale records.
    - Resolves confirmed publications as `PUBLISHED` without duplicate external posts.
    - Validates persisted approval status, transitioning unapproved/revoked items to `BLOCKED`.
    - Detects in-flight attempts and flags them as `RECONCILIATION_REQUIRED` to avoid duplicate social posts.
    - Re-queues tasks only when provably safe (no attempts executed yet, valid approval).
  - Implemented [`PublishingService.reconcile_publication`](file:///d:/standbharat/backend/app/publishing/service.py#L351):
    - Supports manual or automated resolution as `PUBLISHED` (with `external_post_id`), `FAILED`, or `RETRY` (re-validates approval and dispatches task).
  - Updated [`PublishingService.enqueue_publish`](file:///d:/standbharat/backend/app/publishing/service.py#L60):
    - Added guard raising HTTP 409 if a publication is currently in `RECONCILIATION_REQUIRED`.

### 2.4 Celery Task Wrapper
- **File:** [`backend/app/publishing/tasks.py`](file:///d:/standbharat/backend/app/publishing/tasks.py)
- **Changes:**
  - Registered `@celery_app.task(name="recover_stale_publications")`:
    - Wraps `PublishingService.recover_stale_publications` in a dedicated database session.
    - Returns structured summary telemetry with recovery action breakdowns.

### 2.5 Regression Test Suite
- **File:** [`backend/tests/test_publishing.py`](file:///d:/standbharat/backend/tests/test_publishing.py)
- **Changes:** Added 8 new automated test cases (Tests 9 to 16) verifying all recovery criteria.

---

## 3. Automated Test Evidence

### 3.1 Targeted Publishing Test Suite (`pytest tests/test_publishing.py -v`)
```text
tests/test_publishing.py::test_publishing_service_unapproved_draft PASSED [  6%]
tests/test_publishing.py::test_publishing_service_success_enqueue PASSED [ 12%]
tests/test_publishing.py::test_worker_blocks_unapproved_content_on_direct_invocation PASSED [ 18%]
tests/test_publishing.py::test_worker_blocks_rejected_approval PASSED    [ 25%]
tests/test_publishing.py::test_worker_blocks_revoked_approval_on_retry PASSED [ 31%]
tests/test_publishing.py::test_dispatch_failure_persists_failed_state_and_preserves_idempotency PASSED [ 37%]
tests/test_publishing.py::test_worker_enforces_workspace_and_brand_isolation PASSED [ 43%]
tests/test_publishing.py::test_publishing_service_with_integration_fallback PASSED [ 50%]
tests/test_publishing.py::test_fresh_publications_not_marked_stale PASSED [ 56%]
tests/test_publishing.py::test_stale_recovery_with_no_attempt_requeued PASSED [ 62%]
tests/test_publishing.py::test_stale_recovery_already_published_external_id PASSED [ 68%]
tests/test_publishing.py::test_stale_recovery_blocked_if_approval_revoked PASSED [ 75%]
tests/test_publishing.py::test_stale_recovery_uncertain_external_outcome_marked_for_reconciliation PASSED [ 81%]
tests/test_publishing.py::test_concurrent_stale_recovery_conditional_claim PASSED [ 87%]
tests/test_publishing.py::test_reconcile_publication_published_and_retry PASSED [ 93%]
tests/test_publishing.py::test_recovery_repeated_run_is_idempotent PASSED [100%]

============================= 16 passed in 5.01s ==============================
```

### 3.2 Combined Backend Test Suite
```bash
python -m pytest tests/test_publishing.py tests/test_linkedin.py tests/test_wordpress.py tests/test_google_integrations.py tests/test_dashboard.py tests/test_oauth.py
```
**Result:** **47 passed in 18.32s (100% pass rate across 6 test modules)**.

### 3.3 Frontend Production Build
```bash
npm run build
```
**Result:** **Exit code 0** (Compiled successfully in 1.85s with Next.js Turbopack; 26/26 routes generated cleanly with zero type errors).

---

## 4. Recovery Behavior Matrix

| Stuck State Scenario | Detection Trigger | Recovery Action | New Status | Error Code | External Re-Dispatch? |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Fresh Active Job** | `updated_at > cutoff` | Skipped | `PUBLISHING` | Unchanged | No |
| **Pre-Dispatch Crash** | `attempts == 0` & `APPROVED` | Re-queued | `QUEUED` | `None` | **Yes** (Safe) |
| **Already Succeeded Externally** | `external_post_id` or `SUCCESS` attempt | Confirmed published | `PUBLISHED` | `None` | **No** (Idempotent) |
| **Revoked/Rejected Approval** | `ContentApproval != "APPROVED"` | Blocked | `BLOCKED` | `APPROVAL_REQUIRED` | **No** (Forbidden) |
| **Crash In-Flight / Ambiguous Network** | `STARTED` attempt with no response | Paused for reconciliation | `RECONCILIATION_REQUIRED` | `EXTERNAL_OUTCOME_UNCERTAIN` | **No** (Protected) |
| **Known Failed Attempt** | All attempts `FAILED` | Finalized failed | `FAILED` | Attempt error code | **No** |
| **Concurrent Beat Runners** | Row claimed by worker A | Worker B update returns 0 | Unchanged | Unchanged | Skipped by Worker B |

---

## 5. Unresolved Risks & Next Phase Recommendations

1. **Automated External Platform Probing for Uncertain Posts**:
   - Currently, uncertain publications are flagged `RECONCILIATION_REQUIRED` and can be resolved manually or programmatically via [`PublishingService.reconcile_publication`](file:///d:/standbharat/backend/app/publishing/service.py#L351).
   - In a future phase, connectors could implement an optional `query_recent_posts(query)` interface to automatically search platform feeds for identical draft titles/hashes before requiring user intervention.
2. **Frozen Dashboard UI Preservation**:
   - The Command Center dashboard remains frozen and unaltered as strictly required.
   - When the Approvals and Content details pages are wired in Phase 33, a dedicated "Reconcile" badge can display for items in `RECONCILIATION_REQUIRED`.
