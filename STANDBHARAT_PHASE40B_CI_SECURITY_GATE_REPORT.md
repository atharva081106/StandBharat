# StandBharat — Phase 40B: CI Security Gate Verification & Hardening Report

**Date:** 2026-10-12  
**Target:** CI Security Gate Verification, Policy Hardening, and Cryptographic Regression Protection  
**Status:** Complete & Hardened  

---

## 1. Executive Summary

Phase 40B rigorously hardened the StandBharat CI security gate and preflight verification pipeline established in Phase 40A. Rather than masking development dependencies behind permissive flags, this phase established an explicit, verifiable security policy for high-severity dev dependencies, created focused cryptographic regression tests for JWT algorithm restrictions and ECDSA non-usage, pinned backend dependencies reproducibly, safeguarded local environment secrets during Compose preflight validation, and audited deployment gating behavior.

All 56 backend security and regression tests pass (100%), the Next.js 16 production build compiles cleanly across all 26 static routes, and the frontend dependency audit policy confirms 0 production vulnerabilities, 0 critical vulnerabilities, and bounded acceptance of the ESLint/braces dev linter advisory. The Command Center dashboard ([`frontend/app/app/command-center/page.tsx`](file:///d:/standbharat/frontend/app/app/command-center/page.tsx)) remains 100% untouched.

---

## 2. In-Depth Vulnerability & Policy Verification

### 2.1 `braces` Vulnerability & Dependency Chain (`GHSA-vfj7-8cjw-p6xm`)
- **Advisory Details:** `GHSA-vfj7-8cjw-p6xm` / `CVE-2024-4068` identifies an uncontrolled resource consumption / regular expression denial-of-service (ReDoS) vulnerability in `braces` when expanding untrusted glob patterns containing nested braces.
- **Dependency Path:**
  ```
  frontend/package.json (devDependencies)
  └── eslint-config-next@16.3.8
      └── @next/eslint-plugin-next@16.3.8
          └── fast-glob@*
              └── micromatch@4.0.8
                  └── braces@3.0.3 (installed: 3.0.3)
  ```
- **Authoritative Version Check:** The installed version in `node_modules/braces` is `3.0.3`, which is the latest stable release of the 3.x line.
- **Why Next.js Downgrade was Rejected:** Running `npm audit fix --force` would downgrade `eslint-config-next` to `14.2.35`. StandBharat runs Next.js 16 (`16.3.8`) and React 19 (`19.2.8`); forcing Next.js 14 lint configurations causes immediate syntax errors and breaks the build.
- **Runtime Impact:** **ZERO**. `braces` is strictly in devDependencies and executed only during local development linting. Production client bundles contain 0 vulnerabilities (`npm audit --omit=dev` exits 0).

### 2.2 Re-Evaluation of `npm audit --audit-level=critical` & Explicit Policy Implementation
- **Investigation Finding:** In Phase 40A, `.github/workflows/security_audit.yml` executed:
  ```bash
  npm audit --audit-level=critical
  ```
  Because `--audit-level=critical` only exits with failure on *critical* severity findings, it silently permitted the five *high*-severity dev findings (`braces`, `micromatch`, `fast-glob`, `@next/eslint-plugin-next`, `eslint-config-next`). Claiming "zero high vulnerabilities" without qualification was therefore inaccurate.
- **Hardened Policy Enforcer ([`frontend/scripts/audit-policy.mjs`](file:///d:/standbharat/frontend/scripts/audit-policy.mjs)):**
  Created an automated JSON audit validator integrated via `npm run audit:policy`:
  1. **Strict Production Enforcement:** Executes `npm audit --omit=dev --json` and asserts total production vulnerabilities is exactly 0.
  2. **Zero Critical Policy:** Asserts total critical vulnerabilities across the entire graph is 0.
  3. **Strict Whitelist for High Dev Dependencies:** Parses all high-severity findings and verifies they map strictly to the accepted advisory `1240992` (`GHSA-vfj7-8cjw-p6xm`) under `eslint-config-next`.
  4. **Fail-Closed Gate:** Any other high-severity vulnerability or any vulnerability from another package immediately causes exit code 1.

### 2.3 Python Advisories & Cryptographic Regression Tests
- **`python-jose` (`CVE-2026-85394`):**
  - *Vector:* In unconstrained JWT decoders, attackers with an RSA public key can trick the HMAC validator into verifying public keys as symmetric secrets if algorithm validation is omitted.
  - *Active Code Hardening:* In [`backend/app/api/deps.py`](file:///d:/standbharat/backend/app/api/deps.py#L33):
    ```python
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    ```
    Where `settings.ALGORITHM` is strictly `"HS256"`.
- **`ecdsa` (`PYSEC-2026-1325`):**
  - *Vector:* Minerva side-channel timing attack during `sign_digest()` on P-256 curves.
  - *Codebase Audit:* Grep and AST inspection confirm zero references to `ecdsa`, `SigningKey`, or ECDSA signing operations in application code. `ecdsa` is an unused transitive dependency of `python-jose`.
- **New Regression Test Suite ([`backend/tests/test_jwt_security_regression.py`](file:///d:/standbharat/backend/tests/test_jwt_security_regression.py)):**
  Added 7 focused tests:
  1. `test_jwt_algorithm_is_strictly_hs256`: Asserts `settings.ALGORITHM == "HS256"`.
  2. `test_valid_access_token_decodes_successfully`: Verifies standard HS256 tokens decode properly.
  3. `test_jwt_rejects_none_algorithm`: Forges `alg="none"` tokens and asserts `JWTError` rejection.
  4. `test_jwt_rejects_mismatched_algorithms`: Signs with HS512/RS256 and asserts `JWTError` rejection.
  5. `test_jwt_rejects_tampered_payload`: Asserts tampered payloads fail signature validation.
  6. `test_deps_enforces_explicit_algorithm_restriction`: Inspects source AST of `deps.get_current_user` to ensure `algorithms=[settings.ALGORITHM]` is never removed.
  7. `test_zero_ecdsa_signing_in_app`: Verifies application modules do not import or call `ecdsa.SigningKey`.

### 2.4 Reproducible Dependency Pinned Lockfile
- Generated [`backend/requirements.lock`](file:///d:/standbharat/backend/requirements.lock) containing exact pinned distributions (e.g., `fastapi==0.141.1`, `cryptography==50.0.1`, `python-jose==3.5.0`, `pgvector==0.3.6`).
- Updated `.github/workflows/security_audit.yml` to:
  - Run `npm ci` in frontend for deterministic lockfile hydration.
  - Scan `backend/requirements.lock` with `pip-audit`.

### 2.5 Safe Compose Preflight Configuration
- In Phase 40A, the workflow ran `cp .env.example .env`, which would overwrite local secrets in a non-containerized developer workspace.
- Updated both local testing and CI workflow to:
  ```bash
  docker compose --env-file .env.example config --quiet
  ```
  Validates compose service topology, environment variable interpolation, and syntax purely using safe placeholder definitions without touching `.env`.

### 2.6 Deployment Workflow Gating Audit
- **Audit Question:** Does deployment proceed if security checks fail?
- **Investigation Result:** Inspected `.github/workflows/`. Only `.github/workflows/security_audit.yml` exists. There is **NO automated CD or deployment workflow** in git.
- **Honest Verdict:** Deployment gating is not automated through GitHub Actions because no deployment workflow exists. StandBharat deployments are currently executed manually or externally. Therefore, we do not claim automated deployment blocking in CI. However, `security_audit.yml` runs on push and PR to `master` and `main`, providing pull-request gating when GitHub branch protection is enabled.

---

## 3. Changed Files

1. [`.github/workflows/security_audit.yml`](file:///d:/standbharat/.github/workflows/security_audit.yml):
   - Switched to `pip-audit -r backend/requirements.lock`.
   - Added `npm ci` for deterministic package-lock hydration.
   - Replaced permissive `--audit-level=critical` with `npm run audit:policy`.
   - Replaced `cp .env.example .env` with safe `docker compose --env-file .env.example config --quiet`.
2. [`frontend/scripts/audit-policy.mjs`](file:///d:/standbharat/frontend/scripts/audit-policy.mjs):
   - Created security policy validator enforcing 0 production vulnerabilities, 0 criticals, and strict dev whitelist.
3. [`frontend/package.json`](file:///d:/standbharat/frontend/package.json):
   - Added `"audit:policy": "node scripts/audit-policy.mjs"`.
4. [`backend/requirements.lock`](file:///d:/standbharat/backend/requirements.lock):
   - Pinned reproducible dependency lockfile for backend dependencies.
5. [`backend/tests/test_jwt_security_regression.py`](file:///d:/standbharat/backend/tests/test_jwt_security_regression.py):
   - Added 7 cryptographic regression tests verifying algorithm whitelisting, none-algorithm rejection, and ECDSA non-usage.
6. [`backend/tests/test_approvals_and_content.py`](file:///d:/standbharat/backend/tests/test_approvals_and_content.py):
   - Updated test mock credential from placeholder `"enc"` to valid Fernet token to satisfy strict DB encryption validation.

---

## 4. Verification Evidence & Test Execution

### 4.1 Backend Security & Regression Suite
```powershell
python -m pytest tests/test_jwt_security_regression.py tests/test_db_encryption_migration.py tests/test_backup_restore.py tests/test_production_security_audit.py tests/test_approvals_and_content.py -v
```
**Output:**
```
======================= 56 passed, 2 warnings in 26.98s =======================
```
- `test_jwt_security_regression.py`: 7 / 7 PASSED (100%)
- `test_db_encryption_migration.py`: 11 / 11 PASSED (100%)
- `test_backup_restore.py`: 15 / 15 PASSED (100%)
- `test_production_security_audit.py`: 11 / 11 PASSED (100%)
- `test_approvals_and_content.py`: 12 / 12 PASSED (100%)

### 4.2 Frontend Audit Policy Gate
```powershell
npm run audit:policy
```
**Output:**
```
============================================================
STANDBHARAT FRONTEND DEPENDENCY AUDIT POLICY CHECK
============================================================

[1/2] Verifying production runtime dependencies (--omit=dev)...
✓ PASS: Zero vulnerabilities in production runtime bundle.

[2/2] Verifying full tree against devDependency security policy...
✓ PASS: 5 high-severity findings documented & accepted in dev dependencies.
        Reason: eslint-config-next / braces (GHSA-vfj7-8cjw-p6xm) dev linter tool.
        Installed braces version is 3.0.3. Zero production client exposure.
============================================================
STATUS: POLICY COMPLIANT (0 production, 0 critical, 0 unvetted high)
============================================================
Exit code: 0
```

### 4.3 Frontend Production Build
```powershell
npm run build
```
**Output:**
```
▲ Next.js 16.3.8 (Turbopack)
✓ Compiled successfully in 7.2s
  Finished TypeScript in 3.3s ...
✓ Generating static pages using 11 workers (26/26) in 790ms
  Finalizing page optimization ...
Exit code: 0
```

### 4.4 Docker Compose Safe Preflight
```powershell
docker compose --env-file .env.example config --quiet
```
**Output:**
```
Exit code: 0 (clean, no warnings)
```

### 4.5 Frozen Dashboard Boundary
```powershell
git status frontend/app/app/command-center/page.tsx
```
**Output:**
```
nothing to commit, working tree clean (0 lines modified)
```

---

## 5. Remaining Accepted Vulnerabilities

| Dependency | Scope | Severity | Advisory ID | Reason for Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| **`braces` / `micromatch` / `eslint-config-next`** | `devDependencies` | High | `GHSA-vfj7-8cjw-p6xm` | Strictly confined to development linter. `3.0.3` is installed. Downgrading breaks Next.js 16. **0 client runtime exposure**. |
| **`python-jose`** | `backend` | High | `CVE-2026-85394` | Asymmetric key confusion attack. **Fully mitigated** by strict `algorithms=[settings.ALGORITHM]` (`HS256`) in `deps.py`. Verified by regression tests. |
| **`ecdsa`** | `backend` (transitive) | Medium | `PYSEC-2026-1325` | Minerva timing attack on ECDSA signing. **Non-exploitable**: StandBharat never generates or signs with ECDSA keys; library is unused transitive code. Verified by regression tests. |

---

## 6. Remote CI Status & Honest Release Verdict

- **Remote CI Status:** **`NOT_VERIFIED`**  
  *Rationale:* Remote GitHub Actions runners cannot be triggered without pushing commits to the remote GitHub repository. Local execution of the exact workflow commands validates that the jobs are syntactically and logically sound.
- **Automated Deployment Gating:** **`NOT_APPLICABLE`**  
  *Rationale:* No deployment workflow exists in `.github/workflows/`. There is no CD pipeline to gate.
- **Release Verdict:** **`GO / RELEASE READY`**  
  *Rationale:* The application has 0 production runtime bundle vulnerabilities, 0 critical vulnerabilities, strictly bounded dev linter exceptions, 100% passing security and cryptographic regression tests (56/56), a verified Next.js 16 production build, and safe Compose preflight configuration.
