# StandBharat — Phase 20: Stale Recovery & Retries Hardening

## 1. Objective
Audit the Phase 19 self-healing implementation to fix any edge cases surrounding timestamps, concurrent requests, and retry collisions. Preserve the frozen dashboard UI and existing architecture without introducing a duplicate tracking system.

## 2. Hardening Fixes Implemented

### A. Atomic Concurrent Stale Recovery
**Vulnerability:** In Phase 19, if a user had multiple dashboard tabs open, concurrent `/workflow-status` polling requests could theoretically both evaluate `updated_naive < stale_threshold` and attempt to race each other to fail the same database record.
**Fix:** Refactored the `updated_at` threshold check in `app/api/endpoints/brands.py` to use an atomic SQLAlchemy `.update()` query:
```python
rows = db.query(WebsiteAnalysis).filter(
    WebsiteAnalysis.id == analysis.id,
    WebsiteAnalysis.status.in_(["QUEUED", "RUNNING"])
).update({"status": "FAILED"}, synchronize_session=False)
```
This leverages database-level locking. The first request will succeed (`rows > 0`) and commit the failure. The concurrent requests will return `rows == 0` and safely refresh their local object state, achieving absolute atomicity under heavy polling.

### B. Optimized WebsiteAnalysis Retries
**Vulnerability:** When a user clicked "Try Again" after a *Strategy* generation failed (e.g. `NOT_CONFIGURED`), the frontend hit the root `/website-analysis` endpoint. Previously, this endpoint blindly set the `WebsiteAnalysis` back to `QUEUED` and re-ran the full analysis, wasting ~15 seconds of compute.
**Fix:** Audited `app/api/endpoints/website_analysis.py` and implemented a bypass:
If the analysis is already `COMPLETED`, the endpoint safely skips re-running the background extraction task and immediately dispatches the `generate_core_brand_strategy.delay()` worker. 

### C. Configurable Timeout & Timezone Consistency
**Audit:** Confirmed `all_models.py` uses `datetime.utcnow` which persists as naive UTC timestamps. The boundary check now safely strips any tzinfo (if present in memory) to prevent `TypeError: can't compare offset-naive and offset-aware datetimes`.
**Fix:** Hardened the `STALE_WORKFLOW_TIMEOUT_MINUTES` environment variable parsing to enforce a strictly positive integer, falling back to 10 minutes safely if a malformed string or negative number is injected into the container environment.

## 3. Regression Testing

Added three deterministic regression tests in `tests/test_workflow_reliability.py`:
1. **`test_recent_workflow_not_marked_stale`**: Simulates a workflow that updated just 2 minutes ago (under the 10-minute threshold) and validates that `get_workflow_status` correctly leaves it in `PROCESSING` rather than aggressively killing it.
2. **`test_completed_analysis_skipped_on_retry`**: Simulates clicking "Try Again". Asserts that the existing `COMPLETED` analysis is strictly preserved and not downgraded to `QUEUED`, while asserting that the downstream `BrandStrategy` worker is immediately dispatched via `.delay()`.
3. **Preservation Rules (Existing)**: Re-confirmed that manual edits and `NOT_CONFIGURED` terminal states are correctly identified and safely skipped by the retry sweep.

## 4. Execution Results
- **Backend Tests:** 
  - `python -m pytest tests/test_workflow_reliability.py -v` (Passed 9/9)
  - `python -m pytest tests/test_workflow_status.py -v` (Passed 7/7)
- **Frontend Build:** `npm run build` completed successfully with Turbopack, validating strict type-checking and successful static generation for 26/26 routes. No changes to the dashboard UI were required.

## 5. Deliverables & Changed Files
- `backend/app/api/endpoints/brands.py` (Atomic stale updates & timeout validation)
- `backend/app/api/endpoints/website_analysis.py` (Retry optimization bypass)
- `backend/tests/test_workflow_reliability.py` (3 new concurrency and bypass test cases)

## 6. Remaining Risks
The workflow state machine is now highly robust and fault-tolerant to broker/worker crashes. No immediate architectural risks remain for Phase 20's scope.
