# Security Architecture

## 1. Authentication
- Secure authentication architecture supporting signup, login, logout, session management, password hashing, email verification, and password resets.
- Use secure HTTP-only cookies for web sessions.
- **NEVER** store sensitive authentication tokens in `localStorage`.

## 2. Multi-Tenancy & Authorization
- Tenant isolation is strictly enforced at the `Workspace` and `Brand` level.
- Never trust `workspace_id` or `brand_id` supplied blindly by clients.
- Always scope operations through the authenticated server-side identity.
- Role-based access control (OWNER, ADMIN, MARKETER, EDITOR, VIEWER).

## 3. Human-in-the-Loop (Approvals)
- Destructive, financial, or external publishing actions initiated by agents must trigger an approval workflow.
- No external publishing occurs without a verified approval record.

## 4. SSRF & Network Protections
When agents fetch external data (e.g., Competitor Intelligence):
- Block localhost and private IPs.
- Block cloud instance metadata endpoints (e.g., 169.254.169.254).
- Enforce strict timeouts, payload size limits, and max redirects.
- Validate DNS resolution before performing HTTP requests.

## 5. Input Validation
- All inputs from users and external APIs must be sanitized.
- Prevent XSS and SQL Injection via ORM (SQLAlchemy) and strict validation frameworks (e.g., Pydantic).
