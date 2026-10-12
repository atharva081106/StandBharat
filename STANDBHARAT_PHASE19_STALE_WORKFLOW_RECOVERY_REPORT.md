# StandBharat — Phase 19: Stale Workflow Recovery

## 1. Objective
Implement a safe recovery mechanism for `BrandStrategy` and `WebsiteAnalysis` tasks that remain indefinitely stuck in `QUEUED` or `RUNNING` due to Celery worker process crashes or message broker disconnects. Ensure recovery safely preserves existing data and prevents duplicate tracking systems.

## 2. Implementation Strategy

### A. Just-In-Time Self-Healing
Instead of introducing an entirely new Celery Beat process or background daemon to sweep the database for stale tasks (which introduces architectural complexity and duplicate tracking), I implemented **JIT Self-Healing** within the `/api/brands/{brand_id}/workflow-status` polling endpoint.
- **How it works:** When the frontend polls the backend for workflow status, the endpoint inspects the `updated_at` timestamp of any `QUEUED` or `RUNNING` analysis or strategy.
- **Configurable Timeout:** If a task's `updated_at` is older than `STALE_WORKFLOW_TIMEOUT_MINUTES` (defaults to 10 minutes), the backend synchronously marks the record as `FAILED` and supplies the truthful error `Task stalled and timed out (Worker/Broker failure)`.
- **Result:** The frontend immediately receives the `FAILED` state, stops polling, displays the appropriate failure UI, and enables the user to click "Try Again".

### B. Safe Retries & Preservation
When a user clicks "Try Again", the system hits the existing `trigger_website_analysis` endpoint:
- **Duplicate Prevention:** If the tasks were genuinely running (not stale), the endpoint detects `QUEUED`/`RUNNING` and correctly refuses to re-dispatch.
- **Recovery:** Because the stale tasks were recovered into `FAILED`, the endpoint successfully re-queues them.
- **Data Preservation:** The Celery worker (`generate_foundational_documents`) explicitly inspects existing documents. If a document is `ACTIVE` and contains real content (not `PARTIAL` or `NOT_CONFIGURED`), the worker safely returns `{"status": "skipped", "reason": "already_exists"}` instead of generating a duplicate.

### C. Regression Testing
Expanded `tests/test_workflow_reliability.py` to assert the self-healing behavior deterministically without waiting 10 minutes:
- **`test_stale_workflow_recovery`**: Programmatically injects a `WebsiteAnalysis` and `BrandStrategy` record marked as `RUNNING` and `QUEUED` respectively, with their `updated_at` timestamps artificially set to 20 minutes in the past. 
- **Assertion:** Triggers the `workflow-status` endpoint and strictly verifies that the endpoint both returns `FAILED` and permanently commits the `FAILED` status and timeout reasons back to the database.

## 3. Execution Results
- **Backend Tests:** 
  - `python -m pytest tests/test_workflow_reliability.py -v` (Passed 7/7)
  - `python -m pytest tests/test_workflow_status.py -v` (Passed 7/7)
- **Frontend Build:** `npm run build` completed successfully, ensuring the API schema changes align with the React providers.

## 4. Deliverables & Changed Files
- `backend/app/api/endpoints/brands.py` (Self-healing timeout logic)
- `backend/tests/test_workflow_reliability.py` (Stale task recovery test)

## 5. Remaining Limitations
- A 10-minute timeout is generous for an AI strategy generation, but if an external model (e.g. OpenAI o1-preview) genuinely takes longer than 10 minutes, it will be falsely flagged as stale. For production, `STALE_WORKFLOW_TIMEOUT_MINUTES` can be tuned via the environment variables.
