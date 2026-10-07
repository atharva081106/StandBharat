# Testing Strategy

## 1. Core Philosophy
Do not call a feature "production verified" simply because a unit test passed. Testing must exist at multiple layers of the system to ensure robust operation.

## 2. Testing Layers
- **Unit Testing:** Small, isolated functions, utility methods, and isolated components.
- **Integration Testing:** Cross-component interactions (e.g., Database + ORM, API handlers).
- **API Testing:** Contract verification and endpoint responses.
- **Database Testing:** Migrations, schema integrity, and constraint validation.
- **Celery / Worker Testing:** Async task execution, state updates, and retries.
- **AI & Prompt Testing:** Validation of AI outputs, structure, and fallback handling (using determinism where possible, and evals).
- **Agent Testing:** State machine transitions, contract adherence, and isolation.
- **Workflow Testing:** Parallel execution, dependency resolution, idempotency, and lineage recording.
- **Security Testing:** SSRF blocks, auth barriers, tenant isolation checks.
- **Tenant Isolation Testing:** Verifying data from Workspace A cannot be accessed by Workspace B.
- **E2E & Browser Verification:** Real user journeys via automated browser tooling (e.g., Playwright or Cypress).

## 3. Fixtures & Fakes
- Clearly distinguish between `OBSERVED`, `ESTIMATED`, `AI_SUGGESTED`, and `TEST_FIXTURE` data.
- Do not use test fixtures in production workflows to "fake" data availability.
