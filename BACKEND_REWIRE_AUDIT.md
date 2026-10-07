# BACKEND REWIRE AUDIT

## 1. Existing Backend Structure
The `backend/` directory is an initial FastAPI + SQLAlchemy skeleton generated during an earlier initialization step.
- `backend/app/`: Core FastAPI application
- `backend/app/api/`: API routers and endpoints
- `backend/app/core/`: Settings and security configurations
- `backend/app/models/`: SQLAlchemy data models
- `backend/app/schemas/`: Pydantic validation schemas
- `backend/app/db/`: Database session management
- `backend/migrations/`: Alembic database migration scripts

## 2. Existing API Routes
Based on `backend/app/api/api.py` and `backend/app/api/endpoints/`:
- `/auth`: Signup, Login (JWT), and Me routes in `auth.py`.
- `/workspaces`: Basic CRUD in `workspaces.py`.
- `/brands`: Basic CRUD in `brands.py`.
- `/agents`: Stubs in `agents.py`.
- `/integrations`: Stubs in `integrations.py`.

*Missing Domains:* Opportunities, Workflows, Content, Campaigns, Calendar, Analytics, Revenue, Competitors, Approvals, Settings.

## 3. Existing Database Models
Defined in `backend/app/models/all_models.py`:
- `User`, `Workspace`, `WorkspaceMember`, `Brand`
- `Agent`, `AgentTask`, `AgentRun`
- `Approval`, `ContentAsset`, `Campaign`, `Integration`
*Note:* Models currently use SQLite-compatible generic columns but require tuning for PostgreSQL (e.g., `JSONB`).

## 4. Existing Migrations
Alembic is configured (`alembic.ini` and `migrations/` folder exist). An initial SQLite database (`standbharat.db`) exists locally.

## 5. Existing Authentication
- Uses simple JWT token authentication (`backend/app/core/security.py`).
- Routes for POST `/auth/login` (OAuth2PasswordRequestForm) and POST `/auth/signup`.
*To Fix:* Needs to be shifted to HTTP-only secure cookies as per instructions.

## 6. Existing AI Architecture
- Currently empty/non-existent. `backend/app/ai/` and `backend/app/orchestration/` exist as folders but contain no actual gateway, orchestration, or provider (OpenAI/Anthropic) logic.

## 7. Existing Agent Architecture
- Database models `Agent`, `AgentTask`, and `AgentRun` exist.
- Execution logic is completely missing.
- Background worker architecture (e.g. Celery/Redis) is currently missing/stubbed.

## 8. Existing Integrations
- Empty stubs. No actual OAuth flows or API clients.

## 9. Existing Background Jobs
- No background workers currently configured (e.g., Celery, RQ, or ARQ).

## 10. Existing Frontend Providers
Currently abstracted in `frontend/lib/providers/MockProvider.tsx` using a massive combined React context (`MockContext`).

## 11. Mock Data Currently Used by Frontend
Located in `frontend/lib/mock/data.ts`. Includes mock structures for:
- KPIs (Revenue, Leads, Traffic, Conversion)
- Opportunities
- Agents (ACTIVE/WAITING states)
- Content (Published/Draft states)
- Approvals

## 12. What is Missing
- A PostgreSQL database instance (currently falling back to SQLite locally).
- A Redis instance (for background tasks).
- Docker configuration (`docker-compose.yml` exists in root but needs to be verified for Postgres/Redis).
- Frontend API Client (`frontend/lib/api/*`) for standardizing requests.
- True Provider segregation on the frontend (e.g., `AgentProvider` instead of a monolithic `MockProvider`).
- Secure Cookie-based Authentication flow.
- A functional AI Gateway.
- True multi-tenant workspace isolation at the API middleware/dependency level.

## 13. What Can Be Reused
- The FastAPI structure and application factory (`main.py`).
- Alembic configuration (after pointing to Postgres).
- Basic SQLAlchemy models (after some schema tuning).
- The existing Frontend UI React Components completely unchanged.

## 14. What Must Be Implemented
1. Verify/Start PostgreSQL via Docker.
2. Refactor Authentication to use HTTP-only cookies.
3. Build the Frontend API Client `lib/api/client.ts`.
4. Segregate `MockProvider` into distinct `ApiProvider` abstractions.
5. Implement proper Workspace Context middleware for tenant data isolation.
6. Build Celery/Redis background worker system for Agent execution.
7. Implement the AI Gateway layer.
8. Wire up the Command Center to real database records.

---
**Blocker Note regarding PostgreSQL / Docker:** 
The repository currently contains `standbharat.db` (SQLite). The prompt strictly forbids SQLite for production. We must verify if Docker is available to spin up PostgreSQL before proceeding with Phase 4.
