# Database Architecture

## 1. Core Technology
- **Engine:** PostgreSQL
- **Vector Extension:** pgvector
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Note:** SQLite is strictly prohibited for production.

## 2. Multi-Tenancy Strategy
Data is segmented at the `Workspace` and `Brand` levels.
Foreign keys MUST enforce tenant isolation. Queries must always include tenant context derived from the secure server-side session, never trusting client-provided IDs.

## 3. Key Domains

### Identity & Access
- `users`
- `workspaces`
- `workspace_members` (roles: OWNER, ADMIN, MARKETER, EDITOR, VIEWER)
- `brands`

### Intelligence & Context
- `brand_brain_documents`
- `brand_brain_vectors` (pgvector)
- `competitors`
- `opportunities`

### Orchestration & Execution
- `workflows`
- `tasks`
- `agent_runs`
- `approval_requests` (Statuses: PENDING, APPROVED, REJECTED, EXPIRED)

### Content & Campaigns
- `content_items`
- `campaigns`
- `revenue_attribution_events`

### AI & Observability
- `ai_usage_logs` (provider, model, tokens, cost, workspace, agent)

## 4. Large Objects
Images, generated assets, and large documents are stored in an S3-compatible object storage service, with their metadata and URLs referenced in PostgreSQL.
