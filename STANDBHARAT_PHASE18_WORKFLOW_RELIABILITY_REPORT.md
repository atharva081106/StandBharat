# StandBharat — Phase 18: Verified Queued Workflow Transitions (Updated)

## 1. Objective
Audit the Phase 17 fixes to rigorously trace the lifecycle of a queued `BrandStrategy` record, ensure Celery properly locks states, write regression tests, and confirm that the dashboard production build handles transitions gracefully. No features were added, and the dashboard remains frozen.

## 2. Implementation Details

### A. Celery Worker State Lock
**Enhancement:** In Phase 17, we pre-created the `BrandStrategy` model in `QUEUED` status *before* dispatching the task, ensuring the UI sees it. However, if the worker picked it up and crashed before completion, it could sit infinitely in `QUEUED`.
**Fix:** Modified `app/workers/celery_worker.py` to immediately commit `RUNNING` to the database the millisecond the worker grabs the task. This ensures absolute visibility: if it's `QUEUED`, it's waiting for compute. If it's `RUNNING`, a worker is actively processing it. 
**Retry Preservation:** The worker also skips generation if the strategy is manually marked `ACTIVE` or populated with `USER_EDITED_CONTENT`, safely preserving user modifications during recovery retries.

### B. Task Dispatch Failure Prevention
**Enhancement:** If the Celery message broker (RabbitMQ/Redis) was down, `website_analysis.py` would catch the dispatch exception and mark the analysis as `FAILED`, but the pre-created `BrandStrategy` would remain stranded in `QUEUED` forever.
**Fix:** Updated the exception handler in `_run_analysis_task` to query for the newly created `QUEUED` strategy and safely revert it to `FAILED` alongside the analysis, preventing infinite UI polling for a task that was never queued.

### C. Regression Test Coverage
Expanded `tests/test_workflow_reliability.py` to assert correct transitions across edge cases.
1. **`test_queue_delay_maintains_processing`**: Asserts that `(Website: COMPLETED, Strategy: QUEUED)` unambiguously maps to an overall `PROCESSING` state for the frontend.
2. **`test_missing_credentials_fails_gracefully`**: Asserts that if AI Gateway crashes due to unconfigured keys, it falls back to `NOT_CONFIGURED`, a proper terminal state that halts frontend polling.
3. **`test_dispatch_failure_reverts_queued_strategy`**: Asserts that if `.delay()` throws an exception, the `QUEUED` strategy is safely transitioned to `FAILED`.
4. **`test_successful_retry_preserves_active`**: Simulates a retry on a completed and modified document. Asserts the system gracefully skips generation and leaves the user's content intact.
5. **`test_workflow_status_cross_tenant`**: (Existing) Confirmed 403 Forbidden is strictly enforced.

## 3. Execution Results
- **Backend Tests:** 
  - `python -m pytest tests/test_workflow_reliability.py -v` (Passed 6/6)
  - `python -m pytest tests/test_workflow_status.py -v` (Passed 7/7)
- **Frontend Build:** `npm run build` completed successfully with Next.js Turbopack, validating strict type-checking and successful static generation for 26/26 routes.

## 4. Deliverables & Changed Files
- `backend/app/workers/celery_worker.py` (Worker logic)
- `backend/app/api/endpoints/website_analysis.py` (Dispatch failure handler)
- `backend/tests/test_workflow_reliability.py` (Regression suite)
- The existing frontend `WorkflowStatusProvider` seamlessly processes the locked states.

## 5. Remaining Limitations
- While AI failures degrade gracefully, actual OpenAI / Google credentials are required to progress a brand completely into `ACTIVE` state. The UI treats `NOT_CONFIGURED` as a halting terminal state correctly.
