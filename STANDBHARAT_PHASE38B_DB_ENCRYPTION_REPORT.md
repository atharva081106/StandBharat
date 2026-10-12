# StandBharat — Phase 38B: Dedicated DB Encryption Key & Backward-Compatible Migration Report

**Date:** 2026-10-12  
**Status:** Complete & Fully Verified  
**Target:** Integration Credential Encryption-at-Rest Hardening, Decoupled Key Management, and Backward-Compatible Re-Encryption Migration  

---

## 1. Executive Summary

In Phase 38B, StandBharat successfully introduced a dedicated database credential encryption key (**`DB_ENCRYPTION_KEY`**), fully decoupling integration credentials at rest from session signing keys (**`SECRET_KEY`**) and cold storage backup encryption (**`BACKUP_ENCRYPTION_KEY`**).

Before modifying code, a comprehensive audit of all credential read, write, refresh, and decrypt code paths was completed. The encryption architecture was upgraded to use `cryptography.fernet.MultiFernet` with automatic legacy fallback, strict primary-key precedence for all writes, fail-closed exception handling (`DecryptionError`, `EncryptionKeyMissingError`), and an explicit CLI migration and rollback tool (`backend/scripts/migrate_credentials_encryption.py`). Existing production and test data were preserved without destructive migrations or automatic unverified mutations.

All 11 targeted encryption migration tests, 23 publishing regression tests, 12 Google integration regression tests, 15 backup/restore regression tests, and 11 production security audit tests passed (72/72 tests passing). The frozen Command Center dashboard (`frontend/app/app/command-center/page.tsx`) remains 100% untouched.

---

## 2. Existing Encryption Design & Key Derivation Audit

### 2.1 Pre-Phase 38B Legacy Architecture
Prior to Phase 38B, integration credentials (e.g. OAuth access and refresh tokens for Google Analytics 4, Google Search Console, LinkedIn, and WordPress) were encrypted using:
- **Module:** `backend/app/core/encryption.py`
- **Key Source:** `settings.SECRET_KEY`
- **Key Derivation Function (KDF):**
  - PBKDF2-HMAC-SHA256
  - Iterations: 100,000
  - Salt: `b"standbharat_salt"`
  - Derived Length: 32 bytes (URL-safe base64 encoded)
- **Ciphertext Format:** Standard RFC Fernet token (`AES-128-CBC` with `HMAC-SHA256` authentication).

### 2.2 Identified Vulnerabilities & Architectural Risks
1. **Key Coupling Hazard:** `SECRET_KEY` was shared between JWT session tokens and database credential encryption. If `SECRET_KEY` needed rotation (e.g., due to user session invalidation or key compromise), all stored integration credentials became immediately undecryptable.
2. **Silent Failure Risk:** `PublishingService.get_credentials` previously had a broad `except Exception: return {}`, which masked decryption failures instead of failing closed.
3. **No Key Versioning:** Ciphertext tokens lacked key version metadata, preventing gradual or staged key rotation without data loss.

---

## 3. Credential Code Paths & Storage Audit

Every code path interacting with stored provider credentials was mapped and verified:

| Component / File | Operation | Data Field | Behavior / Invariants |
| :--- | :--- | :--- | :--- |
| `backend/app/core/encryption.py` | Encrypt / Decrypt | Centralized cipher | Primary key precedence on write, MultiFernet fallback on read, fail-closed on error. |
| `backend/app/models/all_models.py` | Storage | `Integration.credentials_encrypted` | Text column storing Fernet ciphertext. |
| `backend/app/publishing/models.py` | Storage | `PublisherConnection.encrypted_credentials` | String column storing Fernet ciphertext. |
| `backend/app/api/endpoints/integrations.py` | Write (Manual & OAuth) | `credentials_encrypted` | Encrypts credentials on connect; decrypts on GA4 property inspection. |
| `backend/app/api/endpoints/publishing.py` | Write (OAuth & State) | `encrypted_credentials`, state | Encrypts OAuth callback tokens and CSRF state payloads; decrypts state on callback. |
| `backend/app/publishing/service.py` | Read | `get_credentials()` | Decrypts connection credentials; fails closed with `DecryptionError` on failure. |
| `backend/app/publishing/tasks.py` | Worker Read | `execute_publishing_task` | Catches `EncryptionError`, fails task permanently with `AUTHENTICATION_ERROR` and redacts errors. |
| `backend/app/integrations/providers/ga4.py` | Read / Refresh / Write | `credentials_encrypted` | Decrypts credentials, refreshes expired OAuth tokens, re-encrypts updated tokens to DB. |
| `backend/app/integrations/providers/gsc.py` | Read / Refresh / Write | `credentials_encrypted` | Decrypts credentials, refreshes tokens, re-encrypts updated tokens to DB. |
| `backend/app/integrations/providers/*.py` | Read | `credentials_encrypted` | Facebook, Instagram, LinkedIn, Reddit, TikTok, WordPress, X, YouTube decrypt credentials. |

---

## 4. Phase 38B Technical Implementation

### 4.1 Dedicated Encryption Engine (`backend/app/core/encryption.py`)
- **Key Derivation:**
  - Dedicated Salt: `DB_KDF_SALT = b"StandBharat_DB_Encryption_Salt_2026_v1"`
  - Direct 44-character base64 Fernet key support (e.g. `Fernet.generate_key()`) or high-entropy passphrase via PBKDF2-HMAC-SHA256 (100,000 iterations).
  - Legacy Salt: `LEGACY_KDF_SALT = b"standbharat_salt"` preserved for backward compatibility.
- **`MultiFernet` Architecture:**
  - `MultiFernet([primary_fernet, legacy_fernet])`
  - All calls to `encrypt()` encrypt using `primary_fernet` (`DB_ENCRYPTION_KEY`).
  - Calls to `decrypt()` attempt `primary_fernet` first; if `InvalidToken`, falls back to `legacy_fernet` seamlessly.
- **Fail-Closed Exceptions:**
  - `EncryptionError(Exception)`
  - `EncryptionKeyMissingError(EncryptionError)`: Raised when no valid encryption key is configured.
  - `DecryptionError(EncryptionError)`: Raised when token cannot be decrypted by either key. Never returns empty string or placeholder credentials.
- **Inspection & Rotation Helpers:**
  - `re_encrypt(token)`: Decrypts with working key and re-encrypts strictly with primary key.
  - `get_token_key_source(token)`: Returns `"primary"`, `"legacy"`, or raises `DecryptionError`.
  - `is_encrypted_with_primary_key(token)` / `is_encrypted_with_legacy_key(token)`

### 4.2 Configuration & Sanitization
- **`backend/app/core/config.py`:**
  - `DB_ENCRYPTION_KEY: Optional[str] = None`
  - `DB_ENCRYPTION_FALLBACK_TO_SECRET_KEY: bool = True`
  - Production validation ensures keys meet entropy requirements (at least 16 chars, recommended 32+ chars or 44-char Fernet key).
- **`backend/app/core/security.py`:**
  - `sanitize_error_message()` updated to redact `db_encryption_key` occurrences alongside `backup_encryption_key` and API tokens.
- **`.env.example`:**
  - Added clean documentation for `DB_ENCRYPTION_KEY` and fallback toggles without committing real secrets.
- **`docker-compose.yml`:**
  - Passed `DB_ENCRYPTION_KEY` and `DB_ENCRYPTION_FALLBACK_TO_SECRET_KEY` to `migration`, `backend`, and `celery_worker` services.

### 4.3 Safe Migration & Rollback Tooling (`backend/scripts/migrate_credentials_encryption.py`)
A dedicated command-line and programmatic tool provides complete visibility and control over credential re-encryption:
- **`--status`:** Scans all records and classifies them into `PRIMARY_KEY`, `LEGACY_KEY`, `UNREADABLE`, or `EMPTY` without modifying database state.
- **`--dry-run`:** Simulates re-encryption in-memory, verifies round-trip decryptability, and checks for corrupted rows before any database write.
- **`--migrate --confirm`:** 
  1. Performs pre-flight checks (aborts if any corrupted row exists).
  2. Creates a timestamped rollback snapshot JSON artifact (storing record IDs and original ciphertexts—never plaintext).
  3. Re-encrypts all legacy rows in a single atomic database transaction.
  4. Performs round-trip verification on each migrated row; rolls back transaction on any mismatch.
- **`--rollback --backup-file <path>`:** Atomically restores original ciphertexts from the rollback snapshot.

---

## 5. Test Evidence & Validation

All tests were executed against the active backend test environment:

### 5.1 Targeted Encryption Migration Suite (`tests/test_db_encryption_migration.py`)
```
platform win32 -- Python 3.10.11, pytest-9.1.1
collected 11 items

tests/test_db_encryption_migration.py::test_new_key_encryption_and_decryption PASSED          [  9%]
tests/test_db_encryption_migration.py::test_legacy_credential_compatibility_fallback PASSED   [ 18%]
tests/test_db_encryption_migration.py::test_primary_key_precedence_on_write PASSED          [ 27%]
tests/test_db_encryption_migration.py::test_key_independence_rotating_secret_key PASSED     [ 36%]
tests/test_db_encryption_migration.py::test_wrong_key_fails_closed PASSED                   [ 45%]
tests/test_db_encryption_migration.py::test_missing_key_fails_closed PASSED                 [ 54%]
tests/test_db_encryption_migration.py::test_corrupted_ciphertext_fails_closed PASSED         [ 63%]
tests/test_db_encryption_migration.py::test_sanitization_and_redaction PASSED               [ 72%]
tests/test_db_encryption_migration.py::test_migration_dry_run_and_execution PASSED          [ 81%]
tests/test_db_encryption_migration.py::test_migration_fails_closed_on_corrupt_record PASSED  [ 90%]
tests/test_db_encryption_migration.py::test_publishing_service_fails_closed_on_bad_decryption PASSED [100%]

============================= 11 passed in 4.08s ==============================
```

### 5.2 Full Regression Suite Summary
| Test Suite | Test Count | Status | Notes |
| :--- | :--- | :--- | :--- |
| `tests/test_db_encryption_migration.py` | 11 / 11 | **PASSED** | Core Phase 38B targeted test suite |
| `tests/test_publishing.py` | 23 / 23 | **PASSED** | Worker publishing, stale recovery, auth failure handling |
| `tests/test_google_integrations.py` | 12 / 12 | **PASSED** | GA4/GSC OAuth, sync runs, property configuration |
| `tests/test_backup_restore.py` | 15 / 15 | **PASSED** | Phase 38A backup, encryption, retention, isolated restore |
| `tests/test_production_security_audit.py` | 11 / 11 | **PASSED** | Phase 37 production secrets, isolation, CORS, cookies |
| **Total Passed** | **72 / 72** | **100% PASS** | Zero regressions across all phases |

### 5.3 Docker Compose Validation
```powershell
docker compose config --quiet
# Exit code: 0 (No syntax or interpolation errors)
```

---

## 6. Changed & Added Files

```
Modified Files:
- backend/app/core/config.py
- backend/app/core/security.py
- backend/app/core/encryption.py
- backend/app/publishing/service.py
- backend/app/publishing/tasks.py
- backend/app/services/performance/linkedin_provider.py
- .env.example
- docker-compose.yml

Created Files:
- backend/scripts/migrate_credentials_encryption.py
- backend/tests/test_db_encryption_migration.py
- STANDBHARAT_PHASE38B_DB_ENCRYPTION_REPORT.md

Untouched Boundaries:
- frontend/app/app/command-center/page.tsx (Frozen dashboard preserved with 0 modifications)
```

---

## 7. Manual Operational Steps to Configure the New Key Safely

To transition an environment to the dedicated `DB_ENCRYPTION_KEY` without downtime or credential loss, follow these precise steps:

### Step 1: Generate a Dedicated Encryption Key
Generate a strong Fernet key in a secure terminal:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
*(Store this key securely in your secret manager / vault).*

### Step 2: Configure Environment Variables
In your `.env` file (or secret manager), set:
```bash
# Set the new dedicated key
DB_ENCRYPTION_KEY=<generated-fernet-key>

# Keep fallback enabled during migration phase
DB_ENCRYPTION_FALLBACK_TO_SECRET_KEY=true
```

### Step 3: Restart Services
Restart the backend and worker containers:
```bash
docker compose up -d backend celery_worker
```
At this point, new credentials will immediately be encrypted with `DB_ENCRYPTION_KEY`, while existing credentials can still be read seamlessly via the legacy fallback.

### Step 4: Verify Status and Perform Dry-Run
Run the migration CLI inside the backend container:
```bash
# Inspect current status
docker compose exec backend python scripts/migrate_credentials_encryption.py --status

# Perform dry-run verification
docker compose exec backend python scripts/migrate_credentials_encryption.py --dry-run
```

### Step 5: Execute Live Migration
Once the dry-run succeeds, execute live migration:
```bash
docker compose exec backend python scripts/migrate_credentials_encryption.py --migrate --confirm
```
This generates a rollback snapshot in `storage/backups/postgresql/credential_migrations/` and re-encrypts all legacy credentials atomically.

### Step 6: (Optional) Disable Fallback for Complete Decoupling
Once all credentials are confirmed migrated via `--status`:
```bash
DB_ENCRYPTION_FALLBACK_TO_SECRET_KEY=false
```
Reload containers. At this point, `SECRET_KEY` can be rotated at will with zero impact on integration credentials.

### Emergency Rollback (If Ever Needed)
If a rollback is required before disabling fallback:
```bash
docker compose exec backend python scripts/migrate_credentials_encryption.py --rollback --backup-file storage/backups/postgresql/credential_migrations/rollback_snapshot_<timestamp>.json
```

---

## 8. Remaining Risks & Mitigations

1. **Missing Key in Production:**
   - *Risk:* If `DB_ENCRYPTION_KEY` is not set and `DB_ENCRYPTION_FALLBACK_TO_SECRET_KEY=false`, credentials cannot be decrypted.
   - *Mitigation:* The system fails closed immediately with clear `EncryptionKeyMissingError` without modifying database records or leaking secrets. `compute_security_defaults()` warns and enforces key configuration.
2. **Rollback Snapshot Storage:**
   - *Risk:* Deletion of local storage could remove rollback snapshots.
   - *Mitigation:* Rollback snapshots are placed in `storage/backups/postgresql/credential_migrations` which is mapped to the persistent Docker volume `backups_data`.
3. **Secret Leakage in Logs:**
   - *Risk:* Accidental logging of tokens or keys during exceptions.
   - *Mitigation:* Redaction in `sanitize_error_message()` actively strips Fernet base64 keys, tokens, passphrases, and query strings. `DecryptionError` outputs generic diagnostic messages with zero payload contents.
