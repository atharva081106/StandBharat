# StandBharat — Phase 16: Workflow Status & Polling Hardening

## 1. Objective
Audit and harden the Phase 15 implementation (Automatic Background Workflow Updates) by addressing specific architectural flaws, state edge cases, and potential security oversights. Ensure polling behaves predictably across component unmounts and terminal status changes.

## 2. Issues Addressed and Hardened

### A. Frontend: React Closure & Infinite Polling Loop Traps
- **Identified Defect:** `setInterval` inside the `useEffect` of `WorkflowStatusProvider.tsx` suffered from a stale closure bug because it captured `activeBrand` only from its initial render. 
- **Identified Defect:** Adding context refresh hooks (`refreshBrandBrain` and `refreshAnalysis`) into the dependency array would cause an infinite re-render or infinite interval cancellation loop if the providers didn't tightly wrap the refresh actions in `useCallback`.
- **Fix Applied:** 
  - Converted the polling mechanism from `setInterval` to an iterative, promise-aware `setTimeout` recursive poll. This ensures zero overlapping network requests and natively updates context.
  - Employed the `useRef` hook pattern to hold stable references to `refreshBrandBrain` and `refreshAnalysis` functions without binding them to the effect’s dependency array, completely eliminating infinite render loops.
  - Added strict component `isMounted` checks to prevent `setState` memory leaks on unmount.

### B. Backend: Security & Tenant Isolation
- **Verified Status:** Authenticated workspace ownership checks were confirmed securely implemented in `get_current_brand` via strict workspace validation.
- **Identified Defect:** However, the endpoint path parameter `GET /{brand_id}/workflow-status` did not originally assert that the requested `brand_id` matched the authenticated token's context, leaving a minor theoretical ambiguity.
- **Fix Applied:** Implemented a strict check `if str(brand_id) != str(brand.id): raise HTTPException(403)`. This explicitly locks down the path variables.

### C. Backend: Workflow State Ambiguity (Restarting states)
- **Identified Defect:** A scenario where Website Analysis is `COMPLETED`, but Brand Strategy fails back to `QUEUED` or `RUNNING`, was previously misinterpreted by the status parser as entirely `COMPLETED` due to how fallback logic evaluated non-failed strings.
- **Fix Applied:** Modified `get_workflow_status` to explicitly recognize `QUEUED` and `RUNNING` internal task states for `BrandStrategy`. The overall status now natively steps backward into `PROCESSING` if downstream documents or strategies are regenerating.

## 3. Automation and Validation
- **Focused Regression Tests Added:** 
  - `test_workflow_status_restarting`: Validated that restarting downstream workers successfully overrides preceding `COMPLETED` statuses and returns `PROCESSING`.
  - Re-validated the existing `test_workflow_status_cross_tenant` (Auth failure).
- **Backend Tests:** 
  - **Command:** `python -m pytest tests/test_workflow_status.py -v`
  - **Result:** 7 passing tests, 0 failures. (Total execution time: ~12s).
- **Frontend Build:** 
  - **Command:** `npm run build`
  - **Result:** Compiled successfully. Static generation passed zero dependency/hook cycle errors. (Total build time: ~2.5s).

The system remains isolated, the dashboard frozen, and existing mock integrations completely untouched.
