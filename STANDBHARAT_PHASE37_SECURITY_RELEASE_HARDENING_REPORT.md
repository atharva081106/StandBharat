# StandBharat — Phase 37: Production Security & Release Hardening Report

**Date:** October 12, 2026  
**Phase:** 37 (Production Security & Release Hardening)  
**Executive Release Verdict:** **READY FOR CONTROLLED DEPLOYMENT** (Subject to secret rotation before production go-live)  
**Alembic Head Revision:** `3bb7a1f94824`  

---

## 1. Executive Summary

A comprehensive, evidence-based security and release hardening audit of the StandBharat platform was executed across production secrets, network exposure, authentication, tenant isolation, asynchronous background jobs, document persistence, and dependency hygiene.

All high-impact security safeguards identified were implemented and verified with automated test suites (80 backend tests passing, frontend production build passing with 26/26 pages rendered, and 7/7 Docker Compose containers healthy).

---

## 2. Ranked Findings Matrix

| Finding ID | Title | Severity | Status | File Path / Component | Description & Concrete Evidence |
|---|---|:---:|:---:|---|---|
| **SEC-01** | Production Secret Key Enforcement | **Critical** | **PASS** | `backend/app/core/config.py` | `Settings` validator enforces minimum 32 characters and explicitly rejects default dummy keys in production (`test_production_rejects_weak_secret_key` PASS). |
| **SEC-02** | Database & Cache Network Exposure | **High** | **PASS** | `docker-compose.yml` | PostgreSQL (5432) and Redis (6380) port exposures restricted from `0.0.0.0` to loopback `127.0.0.1` (`127.0.0.1:5432:5432`, `127.0.0.1:6380:6379`), preventing public network access while preserving local development workflows. |
| **SEC-03** | CORS Wildcard Invalidation with Credentials | **High** | **PASS** | `backend/app/core/config.py` | Added production validator strictly forbidding wildcard `"*"` in `CORS_ORIGINS` when credentials are enabled (`test_production_rejects_wildcard_cors` PASS). |
| **SEC-04** | Cross-Tenant Authorization Enforcement | **High** | **PASS** | `backend/app/api/deps.py`, `backend/tests/test_production_security_audit.py` | Client-supplied `X-Workspace-ID` and `X-Brand-ID` headers are validated against authenticated user membership in the database; spoofed IDs are rejected with `HTTP 403/404` across documents, approvals, drafts, and Brand Brain. |
| **SEC-05** | OAuth State Tampering & Replay Protection | **High** | **PASS** | `backend/app/api/endpoints/integrations.py` | OAuth `state` parameter is signed with HMAC-SHA256 using `SECRET_KEY` with a 15-minute replay window; tampered or expired states are rejected with `HTTP 403` / `HTTP 400` (`test_oauth_callback_tampered_state_rejected`, `test_oauth_callback_expired_timestamp_rejected` PASS). |
| **SEC-06** | Password Hashing & Bcrypt 72-Byte Truncation Safety | **Medium** | **PASS** | `backend/app/core/security.py` | Migrated from unmaintained Passlib to direct standard `bcrypt.hashpw` and `bcrypt.checkpw`, eliminating 72-byte truncation crash bug while retaining full hash verification compatibility (`test_password_longer_than_72_bytes_safe_handling` PASS). |
| **SEC-07** | Sensitive Credential & Token Redaction | **Medium** | **PASS** | `backend/app/core/security.py`, `backend/app/publishing/tasks.py` | `sanitize_error_message()` actively redacts Bearer tokens, passwords in DB URLs, and API keys from logs and publication metadata records. |
| **SEC-08** | Production Swagger & OpenAPI Schema Exposure | **Medium** | **PASS** | `backend/app/main.py` | `docs_url=None`, `redoc_url=None`, and `openapi_url=None` are conditionally set when `ENVIRONMENT=production`, preventing schema reconnaissance. |
| **SEC-09** | Rate Limiting on Authentication & Expensive Routes | **Medium** | **PASS** | `backend/app/api/endpoints/auth.py`, `content.py`, `ai.py` | Rate limits enforced via SlowAPI on `/api/auth/signup` (5/min), `/api/auth/login` (10/min), and AI generation endpoints. |
| **SEC-10** | Unapproved Publishing & Idempotent Retry Safety | **Medium** | **PASS** | `backend/app/publishing/service.py` | Direct publishing of unapproved drafts returns `HTTP 409 Conflict`. Uncertain outcomes transition to `RECONCILIATION_REQUIRED` and block blind retries. |
| **SEC-11** | Environment File Tracking Exclusions | **Low** | **PASS** | `.gitignore`, `backend/.dockerignore`, `frontend/.dockerignore` | Enhanced `.gitignore` and `.dockerignore` files with `.env*` wildcards to prevent committing or copying staging/production `.env` files into Git or container layers. |
| **SEC-12** | Client-Side Transitive DevDependency Vulnerability | **Low** | **BLOCKED** | `frontend/package.json` | `npm audit` reported high-severity vulnerability in `braces` via build-time devDependency `eslint-config-next`. `npm audit fix --force` requires breaking downgrade to `eslint-config-next@14`. Runtime bundle is unaffected. |
| **SEC-13** | Python Package Security Scanning Tool | **Low** | **NOT_VERIFIED** | `backend/requirements.txt` | `pip-audit` utility is not installed in the local environment; manual dependency review conducted. |
| **SEC-14** | Live Cloud Storage & Live OAuth Credentials | **Medium** | **BLOCKED** | Platform Integrations | Live AWS S3/MinIO and live LinkedIn/Google OAuth credentials were not configured; mock providers verified. |

---

## 3. Changes Made in Phase 37

1. **Loopback Port Binding for State Stores (`docker-compose.yml`):**
   - Bound PostgreSQL host port mapping strictly to `127.0.0.1:5432:5432`.
   - Bound Redis host port mapping strictly to `127.0.0.1:6380:6379`.
   - Internal inter-service communication remains on the secure Compose network (`postgres:5432`, `redis:6379`).
2. **Production CORS Wildcard Prohibition (`backend/app/core/config.py`):**
   - Added `compute_security_defaults()` validation error when `ENVIRONMENT=production` and `CORS_ORIGINS` contains wildcard `*`.
3. **Environment Template Hardening (`.env.example`):**
   - Added all document storage parameters (`STORAGE_BACKEND`, `STORAGE_LOCAL_ROOT`, `STORAGE_MAX_UPLOAD_SIZE_BYTES`, `STORAGE_S3_*`) and database pooling parameters (`DB_POOL_*`) with safe documentation.
4. **Git & Docker Ignore Hardening (`.gitignore`, `backend/.dockerignore`, `frontend/.dockerignore`):**
   - Added wildcard `.env*` rules while safeguarding `!.env.example` to ensure no production or staging `.env` variants can ever be tracked or bundled into container contexts.
5. **Security Audit Test Suite (`backend/tests/test_production_security_audit.py`):**
   - Added 11 automated security tests validating secret key rejection, CORS restrictions, password truncation safety, sensitive error sanitization, cross-tenant isolation, and OAuth state verification.

---

## 4. Verification Evidence & Exact Test Results

### 1. Security Audit Test Suite
```powershell
pytest tests/test_production_security_audit.py -v
```
**Result:** **11 passed in 11.27s (100% Pass Rate)**
- `test_production_rejects_weak_secret_key`: **PASS**
- `test_production_rejects_wildcard_cors`: **PASS**
- `test_production_accepts_strong_secrets_and_specific_cors`: **PASS**
- `test_password_hashing_and_verification`: **PASS**
- `test_password_longer_than_72_bytes_safe_handling`: **PASS**
- `test_sensitive_error_sanitization`: **PASS**
- `test_cross_tenant_document_isolation`: **PASS**
- `test_cross_tenant_approval_and_publishing_isolation`: **PASS**
- `test_cross_tenant_brand_brain_endpoints`: **PASS**
- `test_oauth_callback_tampered_state_rejected`: **PASS**
- `test_oauth_callback_expired_timestamp_rejected`: **PASS**

### 2. Combined Backend Regression Suite
```powershell
pytest tests/test_production_security_audit.py tests/test_storage_and_database_hardening.py tests/test_approvals_and_content.py tests/test_publishing.py tests/test_auth.py tests/test_workflow_tenant_isolation.py tests/test_google_integrations.py tests/test_documents.py -q
```
**Result:** **80 passed in 48.98s (100% Pass Rate)**

### 3. Frontend Production Build
```powershell
npm run build
```
**Result:** **Passed with exit code 0** (Compiled successfully, static page generation 26/26 completed).

### 4. Docker Compose Config Validation
```powershell
docker compose config
```
**Result:** **Passed with exit code 0** (Valid syntax, loopback host IPs bound, volume mounts verified).

### 5. Frozen Command Center Integrity
- Inspected `frontend/app/app/command-center/page.tsx`: **Preserved without modification**.

---

## 5. Secrets Requiring Rotation Before Live Go-Live

The following environment variables were used during local integration and testing and **MUST be rotated before deploying to a public production environment**:

1. `SECRET_KEY`: Used for JWT authentication tokens and HMAC-SHA256 OAuth state signing. (Rotate to a freshly generated 64-character random key: `openssl rand -hex 32`).
2. `POSTGRES_PASSWORD`: Database user password. (Rotate in production `.env` and provision new secret in deployment vault).
3. `OPENAI_API_KEY`, `MISTRAL_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`: API provider keys. (Ensure individual API keys configured in `.env` are production-scoped with budget limits enabled).

*Note: No secret values are printed or reproduced in this report.*

---

## 6. Disaster Recovery, Backup & Operational Gaps

1. **Database Backup Automation:**
   - *Current State:* PostgreSQL data is stored in the Docker volume `standbharat_postgres_data`.
   - *Recommendation:* Deploy an automated cron job or sidecar service executing daily `pg_dump` with encryption and pushing to cold object storage (e.g. AWS S3 Glacier / Cloudflare R2).
2. **Shared Secret for Tokens vs Encryption:**
   - *Current State:* `SECRET_KEY` is currently used both for JWT session signing and for HMAC state validation.
   - *Recommendation:* Introduce a dedicated `DB_ENCRYPTION_KEY` for encrypting integration credentials at rest so that rotating `SECRET_KEY` (JWT sessions) does not require re-encrypting database credentials.
3. **Log Centralization & Alerting:**
   - *Current State:* Logs are collected via Docker container stdout/stderr.
   - *Recommendation:* Configure a log shipping agent (e.g. Vector, Promtail, or Datadog) to stream sanitized logs to a central SIEM.

---

## 7. Prioritized Remediation Roadmap

1. **Pre-Deployment (Immediate):**
   - Inject cryptographically random `SECRET_KEY` and `POSTGRES_PASSWORD` in production vault/orchestrator.
   - Supply production CORS domain (e.g. `https://app.standbharat.com`) via `CORS_ORIGINS`.
2. **Post-Deployment (Phase 38):**
   - Implement automated daily encrypted PostgreSQL backup script to S3/R2.
   - Split `DB_ENCRYPTION_KEY` from `SECRET_KEY` for cryptographic independence.
   - Upgrade Next.js ESLint plugin when upstream Next.js provides updated `braces` dependency bundle.
