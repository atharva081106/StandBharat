# Architecture Overview

## 1. System Components
StandBharat follows a modern, decoupled architecture designed for scale, AI orchestration, and multi-tenancy.

### Frontend
- **Framework:** Next.js with React (TypeScript)
- **Styling:** Tailwind CSS
- **State:** React Server Components + Client-side state as needed

### Backend Application Server
- **Framework:** FastAPI (Python)
- **API Paradigm:** RESTful + WebSockets for real-time AI CMO chat and agent status updates
- **Authentication:** Secure HTTP-only cookies, robust session management

### Asynchronous Execution & Agents
- **Message Broker:** Redis
- **Worker Framework:** Celery
- **Execution Model:** Long-running agents MUST NOT block HTTP requests. FastAPI enqueues tasks and returns task IDs. Workers process tasks and update statuses in PostgreSQL.

### Database
- **Primary Database:** PostgreSQL
- **Vector Database:** pgvector for embeddings
- **ORM:** SQLAlchemy
- **Migrations:** Alembic

### Storage
- **Object Storage:** S3-compatible storage abstraction (StorageProvider)
- **Use case:** User uploads, generated assets, large document storage

## 2. Multi-Tenancy
The system architecture supports a hierarchy of isolation:
- `User`
- `Workspace`
- `Brand`

All business data is tenant-scoped via authenticated server-side identity.

## 3. Deployment & Observability
- **Observability:** Structured logs, request IDs, workflow IDs, error tracking, AI cost tracking, and system health checks.
