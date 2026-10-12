# StandBharat — PostgreSQL Backup & Disaster Recovery Runbook

**Document Version:** 1.0.0  
**Last Verified:** October 12, 2026 (Phase 38A)  
**Target Engine:** PostgreSQL 16 (`pgvector/pgvector:pg16`)  
**Artifact Format:** PostgreSQL Custom Archive (`pg_dump -Fc`)  
**Default Retention:** 7 Backups / 30 Days (Guaranteed Last-Known-Good Preservation)  

---

## 1. Overview & Architectural Design

StandBharat implements an automated, recoverable database backup and disaster recovery architecture designed to protect enterprise data without disrupting user-facing API workflows.

```
+-----------------------------------------------------------------------------------+
|                            CELERY BEAT SCHEDULER                                  |
|                 Dispatches execute_scheduled_backup daily at 02:00 UTC            |
+-----------------------------------------------------------------------------------+
                                          |
                                          v (Redis Broker)
+-----------------------------------------------------------------------------------+
|                            CELERY WORKER PROCESS                                  |
|  1. Executes pg_dump (-Fc format) via internal PostgreSQL connection               |
|  2. Computes unencrypted SHA-256 checksum                                         |
|  3. Encrypts artifact (Fernet AES-128-CBC + HMAC-SHA256) if configured            |
|  4. Uploads encrypted dump to S3-compatible cold storage (with local fallback)    |
|  5. Prunes expired backups (STRICT RULE: Never prunes last known-good backup)      |
|  6. Updates persistent manifest and logs sanitized status (no credentials)        |
+-----------------------------------------------------------------------------------+
       |                                                            |
       v (Local Disk Storage)                                       v (Cloud Cold Storage)
+-------------------------------+                           +-------------------------------+
| storage/backups/postgresql/   |                           | S3 Bucket / Wasabi / MinIO    |
| - backup_<ts>_<uuid>.dump.enc |                           | backups/postgresql/           |
| - backup_manifest.json        |                           | - backup_<ts>_<uuid>.dump.enc |
+-------------------------------+                           +-------------------------------+
```

### Key Safety Guarantees:
1. **Decoupled Execution:** Backups are executed by background Celery worker tasks or dedicated CLI management commands, never synchronously inside web request handlers.
2. **Guaranteed Last-Known-Good Preservation:** The retention engine strictly preserves the newest successful backup artifact under all circumstances, even if all backups have exceeded the retention duration.
3. **Resilient Cold Storage Fallback:** If S3 upload fails due to network or provider issues, the local backup artifact is preserved as a fallback; the failure is recorded in metadata with sanitized error messages.
4. **Isolated Restore Gate:** The restore workflow restores into an isolated sandbox database first (`<dbname>_restore_isolated`) to verify schema and record count before production traffic switchover.
5. **Zero Secret Leakage:** Database connection passwords, encryption keys, and raw tokens are actively redacted from all logs and metadata files via `sanitize_error_message()`.

---

## 2. Configuration Reference

Configure the following variables in your `.env` file or container environment:

| Variable | Type | Default | Description |
|---|:---:|:---:|---|
| `BACKUP_ENABLED` | boolean | `true` | Enables or disables automated background backup execution. |
| `BACKUP_SCHEDULE_CRON` | string | `"0 2 * * *"` | Crontab expression for Celery Beat schedule (Daily at 02:00 UTC). |
| `BACKUP_LOCAL_DIR` | string | `storage/backups/postgresql` | Local directory for storing dumps and the manifest file. |
| `BACKUP_STORAGE_BACKEND` | string | `local` | `local` for disk storage or `s3` for cloud cold storage. |
| `BACKUP_S3_BUCKET` | string | None | S3 bucket name (falls back to `S3_BUCKET_NAME` if unset). |
| `BACKUP_S3_PREFIX` | string | `backups/postgresql` | Prefix/folder path inside the S3 bucket. |
| `BACKUP_RETENTION_COUNT` | integer | `7` | Minimum count of successful backups to retain before pruning. |
| `BACKUP_RETENTION_DAYS` | integer | `30` | Maximum age in days before pruning eligible backups. |
| `BACKUP_ENCRYPTION_KEY` | string | None | Symmetric Fernet key (32-byte url-safe base64 or passphrase). |
| `BACKUP_ENCRYPTION_ENABLED` | boolean | `false` | Auto-enabled if `BACKUP_ENCRYPTION_KEY` is provided. |
| `PG_DUMP_PATH` | string | None | Custom path to `pg_dump` executable (optional). |
| `PG_RESTORE_PATH` | string | None | Custom path to `pg_restore` executable (optional). |

---

## 3. CLI Management Commands

Administrative operators can manage backups using `backend/scripts/backup_manager.py`:

### 3.1 Create an Immediate Backup
```bash
python scripts/backup_manager.py --action backup
# Or target a specific database:
python scripts/backup_manager.py --action backup --db standbharat_db
```

### 3.2 List All Tracked Backups
```bash
python scripts/backup_manager.py --action list
```
*Output Example:*
```
[*] Found 3 backups in manifest:
  [OK] standbharat_standbharat_db_20261012_123422Z_01c8556a.dump.enc   122766B  [ENC] [LOCAL]  2026-10-12T12:34:22Z
  [OK] standbharat_standbharat_db_20261011_020000Z_e71b29a1.dump.enc   121950B  [ENC] [S3]     2026-10-11T02:00:00Z
  [OK] standbharat_standbharat_db_20261010_020000Z_38bc8892.dump.enc   120400B  [ENC] [S3]     2026-10-10T02:00:00Z
```

### 3.3 Verify Backup Integrity & Decryption
```bash
python scripts/backup_manager.py --action verify --file standbharat_standbharat_db_20261012_123422Z_01c8556a.dump.enc
```

### 3.4 Safe Retention Pruning
```bash
python scripts/backup_manager.py --action prune
```

---

## 4. Production Disaster Recovery & Restore Runbook

When performing a database restoration, always follow this four-phase protocol:

```
[Phase 1: Verification] -> [Phase 2: Restore to Sandbox] -> [Phase 3: Validation Queries] -> [Phase 4: Traffic Switch]
```

### Phase 1: Retrieve and Verify Artifact Integrity
1. Confirm the target backup artifact exists in `storage/backups/postgresql/` (or download it from your S3 bucket).
2. Verify artifact checksum and decryptability:
   ```bash
   python scripts/backup_manager.py --action verify --file <backup_filename>
   ```

### Phase 2: Restore into an Isolated Sandbox Database
> [!IMPORTANT]
> Never restore directly into the active production database without sandbox validation. The tool blocks direct overwrites by default.

Restore into an isolated database (e.g. `standbharat_restore_sandbox`):
```bash
python scripts/backup_manager.py --action restore --file <backup_filename> --target-db standbharat_restore_sandbox
```

### Phase 3: Integrity & Schema Verification Queries
Connect to the restored sandbox database and run verification queries:

```bash
docker exec -it standbharat_db psql -U standbharat_user -d standbharat_restore_sandbox
```

Run internal sanity checks:
```sql
-- 1. Check total table count in public schema
SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';

-- 2. Verify Alembic migration head matches production revision
SELECT version_num FROM alembic_version;

-- 3. Check critical user and tenant records
SELECT count(*) FROM "user";
SELECT count(*) FROM workspace;
SELECT count(*) FROM brand;
SELECT count(*) FROM contentdraft;
```

### Phase 4: Production Switchover (When Promoting Restored DB)
Once the sandbox database data integrity is verified by the DBA / Engineering team:

1. Put the application into maintenance mode or stop the backend and Celery workers to freeze writes:
   ```bash
   docker compose stop backend celery_worker celery_beat
   ```
2. Take a final snapshot of the current active database:
   ```bash
   python scripts/backup_manager.py --action backup --db standbharat_db
   ```
3. Swap the databases in PostgreSQL:
   ```sql
   -- Inside psql connected to maintenance database 'postgres':
   ALTER DATABASE standbharat_db RENAME TO standbharat_db_pre_restore_backup;
   ALTER DATABASE standbharat_restore_sandbox RENAME TO standbharat_db;
   ```
4. Restart all services:
   ```bash
   docker compose start backend celery_worker celery_beat
   ```
5. Confirm application health via:
   ```bash
   curl -f http://localhost:8000/health/db
   ```

---

## 5. Automated S3 Cold Storage Setup

To stream backups to AWS S3, Cloudflare R2, MinIO, or Wasabi:

1. Configure `.env`:
   ```ini
   BACKUP_STORAGE_BACKEND=s3
   BACKUP_S3_BUCKET=my-standbharat-backups
   BACKUP_S3_PREFIX=backups/postgresql
   STORAGE_S3_ENDPOINT_URL=https://s3.us-east-1.amazonaws.com
   STORAGE_S3_REGION=us-east-1
   STORAGE_S3_ACCESS_KEY_ID=AKIA...
   STORAGE_S3_SECRET_ACCESS_KEY=...
   ```
2. Recommended AWS IAM Policy for Backup Service:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:GetObject",
           "s3:DeleteObject",
           "s3:ListBucket"
         ],
         "Resource": [
           "arn:aws:s3:::my-standbharat-backups",
           "arn:aws:s3:::my-standbharat-backups/*"
         ]
       }
     ]
   }
   ```
3. Enable S3 Object Versioning and Lifecycle Policies (e.g. Glacier Instant Retrieval after 30 days) on your bucket for compliance.
