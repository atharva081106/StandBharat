# StandBharat — Phase 15: Automatic Background Workflow Updates

## 1. Objective
Connect existing background Celery workflow statuses (Website Analysis, Core Brand Strategy, and Foundational Documents) into the frontend. 

The goal is to allow the UI to reflect processing states, conditionally poll only while tasks run, stop gracefully on terminal states, and refresh the connected state containers without needing to refresh the page or use long-running WebSockets.

## 2. Implementation Overview

### Backend Changes
* **File:** `backend/app/api/endpoints/brands.py`
* **Action:** Created `GET /{brand_id}/workflow-status`
* **Features:**
  * Pulls `status` from `WebsiteAnalysis` and `business_strategy` from `BrandStrategy`, mapping their individual states to a unified `overall_status` (NOT_STARTED, PROCESSING, COMPLETED, FAILED).
  * Automatically returns the count of generated `StrategyDocument` rows.
  * **Security:** Checked request context against `X-Brand-ID` and ensured that the path `{brand_id}` perfectly maps the authorized context to prevent bypassing access layers (tenant-isolation).

### Frontend Changes
* **File:** `frontend/lib/providers/WorkflowStatusProvider.tsx`
* **Action:** Created a context provider to manage polling functionality.
* **Features:**
  * Runs a silent `setInterval` every 3 seconds requesting `workflow-status` if `overall_status === "PROCESSING"`.
  * Detects when the state resolves to a terminal state (`COMPLETED` or `FAILED`), immediately clears the interval to halt polling, and fires `.refresh()` hooks on `useBrandBrain()` and `useWebsiteAnalysis()` to pull the fresh data from the server.
* **File:** `frontend/app/layout.tsx`
  * Injected `<WorkflowStatusProvider>` ensuring it wraps the internal app layout securely, sitting below `BrandBrainContextProvider` but above the layout component tree.
* **File:** `frontend/app/app/layout.tsx`
  * Hooked the "AI CMO is analyzing..." UI widget directly into `useWorkflowStatus()`. It now intelligently displays the analyzing loader while parsing, rendering "Brand Brain Synced" successfully on completion.

## 3. Automation and Testing Validation

### Backend Testing 
* **File:** `backend/tests/test_workflow_status.py`
* Created isolated `TestClient` integrations mirroring the production authentication strategy utilizing `signup`, `login` cookies, and `X-Workspace-ID` configurations.
* Verified 6 scenarios:
  * Empty Database Defaults (`NOT_STARTED`)
  * Actively Computing tasks (`PROCESSING`)
  * Data availability scenarios (`PARTIAL`)
  * Execution failures (`FAILED`)
  * Fully populated systems (`COMPLETED`)
  * Unauthorized tenant-bleed testing (`403 Forbidden` response validated).

```text
tests/test_workflow_status.py::test_workflow_status_not_started PASSED   [ 16%]
tests/test_workflow_status.py::test_workflow_status_processing PASSED    [ 33%]
tests/test_workflow_status.py::test_workflow_status_completed PASSED     [ 50%]
tests/test_workflow_status.py::test_workflow_status_failed PASSED        [ 66%]
tests/test_workflow_status.py::test_workflow_status_partial PASSED       [ 83%]
tests/test_workflow_status.py::test_workflow_status_cross_tenant PASSED  [100%]
======================= 6 passed, 16 warnings in 9.80s ========================
```

### Frontend Build Validations
* NextJS static generation and dependency graph confirmed unblemished.
```text
  Creating an optimized production build ...
✓ Compiled successfully in 3.7s
✓ Generating static pages using 11 workers (26/26) in 663ms
```
