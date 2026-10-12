"""
Unit and Integration Tests for StandBharat PostgreSQL Backup & Restore (Phase 38A)
Tests backup execution, SHA-256 integrity, authenticated encryption, S3 upload failure resilience,
retention pruning with last-known-good protection, and safe isolated database restoration.
"""

import os
import shutil
import tempfile
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

from app.core.config import settings
from app.core.security import sanitize_error_message
from app.backup.crypto import (
    encrypt_file,
    decrypt_file,
    compute_file_sha256,
    get_fernet_key,
    BackupCryptoError,
    BackupDecryptionError
)
from app.backup.engine import (
    BackupManager,
    BackupMetadata,
    RestoreResult,
    BackupError,
    BackupSecurityError,
    BackupNotFoundError
)
from app.backup.tasks import execute_scheduled_backup

# Valid 44-character base64 Fernet test key
TEST_ENCRYPTION_KEY = "k4P9_k_qX8k3qG0Q5_v5x6mZ_y6_Wz1-q8e6_l_u_r0="


def dummy_pg_dump_runner(db_name: str, output_path: str):
    """Simulates a custom format pg_dump output (-Fc header + dummy payload)."""
    # PostgreSQL custom format magic header: "PGDMP" followed by version bytes
    header = b"PGDMP\x01\x10\x00\x04"
    dummy_payload = b"\x00" * 1024 + b"CREATE TABLE users (id int, email text);\nINSERT INTO users VALUES (1, 'admin@example.com');"
    with open(output_path, "wb") as f:
        f.write(header + dummy_payload)


def dummy_pg_restore_runner(target_db: str, input_dump_path: str):
    """Simulates pg_restore execution into target_db."""
    if not os.path.exists(input_dump_path):
        raise BackupError(f"Dump file does not exist: {input_dump_path}")
    with open(input_dump_path, "rb") as f:
        data = f.read(5)
        if data != b"PGDMP":
            raise BackupError("Archiver: did not recognize format of input file")


@pytest.fixture
def temp_backup_dir():
    temp_dir = tempfile.mkdtemp(prefix="test_sb_backups_")
    yield temp_dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# 1. Cryptography & Checksum Tests
# ---------------------------------------------------------------------------

def test_crypto_key_derivation_deterministic():
    key1 = get_fernet_key(TEST_ENCRYPTION_KEY)
    assert len(key1) == 44

    # Passphrase derivation
    derived1 = get_fernet_key("my-secure-production-passphrase-2026")
    derived2 = get_fernet_key("my-secure-production-passphrase-2026")
    assert derived1 == derived2
    assert len(derived1) == 44

    with pytest.raises(BackupCryptoError):
        get_fernet_key("")


def test_file_encryption_and_decryption_cycle(temp_backup_dir):
    plain_path = os.path.join(temp_backup_dir, "test.dump")
    enc_path = os.path.join(temp_backup_dir, "test.dump.enc")
    dec_path = os.path.join(temp_backup_dir, "test_decrypted.dump")

    sample_content = b"CRITICAL_DATABASE_PAYLOAD_" * 500
    with open(plain_path, "wb") as f:
        f.write(sample_content)

    orig_sha = compute_file_sha256(plain_path)

    # Encrypt
    encrypt_file(plain_path, enc_path, TEST_ENCRYPTION_KEY)
    assert os.path.exists(enc_path)
    assert os.path.getsize(enc_path) > 0

    # Ensure encrypted content is not plaintext
    with open(enc_path, "rb") as f:
        cipher_bytes = f.read()
    assert sample_content not in cipher_bytes

    # Decrypt
    decrypt_file(enc_path, dec_path, TEST_ENCRYPTION_KEY)
    assert os.path.exists(dec_path)

    dec_sha = compute_file_sha256(dec_path)
    assert dec_sha == orig_sha


def test_decryption_wrong_key_fails_safely(temp_backup_dir):
    plain_path = os.path.join(temp_backup_dir, "data.dump")
    enc_path = os.path.join(temp_backup_dir, "data.dump.enc")
    dec_path = os.path.join(temp_backup_dir, "data.restored.dump")

    with open(plain_path, "wb") as f:
        f.write(b"TOP_SECRET_TABLE_RECORDS")

    encrypt_file(plain_path, enc_path, TEST_ENCRYPTION_KEY)

    wrong_key = "wrong_passphrase_attempt_for_decryption"
    with pytest.raises(BackupDecryptionError) as exc_info:
        decrypt_file(enc_path, dec_path, wrong_key)

    assert "Invalid encryption key" in str(exc_info.value)
    # Ensure neither key string is leaked in exception message
    assert TEST_ENCRYPTION_KEY not in str(exc_info.value)
    assert wrong_key not in str(exc_info.value)


# ---------------------------------------------------------------------------
# 2. Backup Creation & Integrity Checksum Tests
# ---------------------------------------------------------------------------

def test_backup_creation_unencrypted(temp_backup_dir):
    manager = BackupManager(
        local_dir=temp_backup_dir,
        storage_backend="local",
        encryption_key=None,
        pg_dump_runner=dummy_pg_dump_runner,
    )
    meta = manager.create_backup(db_name="standbharat_test_db")

    assert meta.status == "SUCCESS"
    assert meta.db_name == "standbharat_test_db"
    assert meta.filename.endswith(".dump")
    assert not meta.encrypted
    assert meta.file_size_bytes > 0
    assert len(meta.unencrypted_sha256) == 64
    assert meta.format == "pg_dump_custom_Fc"

    # Verify file exists on disk
    artifact_path = os.path.join(temp_backup_dir, meta.filename)
    assert os.path.exists(artifact_path)
    assert compute_file_sha256(artifact_path) == meta.unencrypted_sha256

    # Verify manifest tracking
    backups = manager.list_backups()
    assert len(backups) == 1
    assert backups[0].backup_id == meta.backup_id


def test_backup_creation_encrypted(temp_backup_dir):
    manager = BackupManager(
        local_dir=temp_backup_dir,
        storage_backend="local",
        encryption_key=TEST_ENCRYPTION_KEY,
        pg_dump_runner=dummy_pg_dump_runner,
    )
    meta = manager.create_backup(db_name="standbharat_prod_db")

    assert meta.status == "SUCCESS"
    assert meta.encrypted is True
    assert meta.filename.endswith(".dump.enc")
    assert meta.encryption_algorithm == "fernet-aes128-cbc-hmac-sha256"

    # Verify raw dump is removed and only .enc artifact remains
    assert not os.path.exists(os.path.join(temp_backup_dir, meta.filename.replace(".enc", "")))
    assert os.path.exists(os.path.join(temp_backup_dir, meta.filename))

    # Verify integrity validation
    assert manager.verify_backup(meta.filename) is True


# ---------------------------------------------------------------------------
# 3. Retention Safety & Last-Known-Good Protection Tests
# ---------------------------------------------------------------------------

def test_retention_preserves_last_known_good_even_if_expired(temp_backup_dir):
    """
    CRITICAL RULE: Even if all backups are older than retention_days,
    the last known-good (newest successful) backup must NEVER be deleted.
    """
    manager = BackupManager(
        local_dir=temp_backup_dir,
        retention_count=2,
        retention_days=7,
        pg_dump_runner=dummy_pg_dump_runner
    )

    now = datetime.now(timezone.utc)
    # Simulate 5 backups all older than 30 days
    manifest = {}
    for i in range(5):
        days_old = 40 - (i * 2) # 40, 38, 36, 34, 32 days old
        ts = (now - timedelta(days=days_old)).isoformat()
        fn = f"standbharat_db_{i}.dump"
        path = os.path.join(temp_backup_dir, fn)
        with open(path, "wb") as f:
            f.write(b"BACKUP_CONTENT")
        manifest[fn] = {
            "backup_id": f"b_{i}",
            "filename": fn,
            "db_name": "standbharat_db",
            "timestamp": ts,
            "file_size_bytes": 14,
            "unencrypted_sha256": "fake_sha",
            "status": "SUCCESS"
        }
    manager._save_manifest(manifest)

    # Run pruning
    pruned = manager.prune_old_backups()
    remaining = manager.list_backups()

    # The newest backup (standbharat_db_4.dump, 32 days old) MUST be preserved!
    assert len(remaining) >= 1
    newest = manager.get_latest_successful_backup()
    assert newest is not None
    assert newest.filename == "standbharat_db_4.dump"
    assert os.path.exists(os.path.join(temp_backup_dir, "standbharat_db_4.dump"))


def test_retention_single_backup_never_pruned(temp_backup_dir):
    manager = BackupManager(
        local_dir=temp_backup_dir,
        retention_count=0, # Aggressive 0 count
        retention_days=0,  # Aggressive 0 days
        pg_dump_runner=dummy_pg_dump_runner
    )

    meta = manager.create_backup()
    assert len(manager.list_backups()) == 1

    pruned = manager.prune_old_backups()
    assert len(pruned) == 0
    assert len(manager.list_backups()) == 1
    assert os.path.exists(os.path.join(temp_backup_dir, meta.filename))


# ---------------------------------------------------------------------------
# 4. S3 Cold Storage & Upload Failure Handling Tests (Mocked Cloud)
# ---------------------------------------------------------------------------

def test_s3_upload_failure_retains_local_copy(temp_backup_dir):
    """
    [MOCKED CLOUD TEST]
    When S3 cold storage upload fails (e.g. connection timeout),
    the local backup artifact must be retained safely without failing the backup task.
    """
    mock_s3 = MagicMock()
    mock_s3.put_object.side_effect = ConnectionError("Could not connect to S3 endpoint: Connection timed out")

    manager = BackupManager(
        local_dir=temp_backup_dir,
        storage_backend="s3",
        pg_dump_runner=dummy_pg_dump_runner,
        s3_client=mock_s3
    )

    meta = manager.create_backup(db_name="standbharat_s3_test")

    # Overall backup succeeds locally
    assert meta.status == "SUCCESS"
    assert meta.cold_storage_uploaded is False
    assert "Connection timed out" in (meta.cold_storage_error or "")
    # Local file exists intact
    assert os.path.exists(os.path.join(temp_backup_dir, meta.filename))


def test_s3_upload_success_recorded(temp_backup_dir):
    """[MOCKED CLOUD TEST] S3 upload success properly flags metadata."""
    mock_s3 = MagicMock()
    mock_s3.put_object.return_value = {"ETag": '"abc123etag"'}

    manager = BackupManager(
        local_dir=temp_backup_dir,
        storage_backend="s3",
        pg_dump_runner=dummy_pg_dump_runner,
        s3_client=mock_s3
    )

    meta = manager.create_backup()
    assert meta.status == "SUCCESS"
    assert meta.cold_storage_uploaded is True
    assert meta.cold_storage_error is None
    assert mock_s3.put_object.called


# ---------------------------------------------------------------------------
# 5. Restore Workflow & Active Database Overwrite Safeguard Tests
# ---------------------------------------------------------------------------

def test_restore_into_isolated_database_succeeds(temp_backup_dir):
    manager = BackupManager(
        local_dir=temp_backup_dir,
        encryption_key=TEST_ENCRYPTION_KEY,
        pg_dump_runner=dummy_pg_dump_runner,
        pg_restore_runner=dummy_pg_restore_runner
    )

    meta = manager.create_backup(db_name="standbharat_db")
    isolated_target = "standbharat_restore_sandbox"

    res = manager.restore_backup(
        filename=meta.filename,
        target_database=isolated_target,
        allow_active_db_overwrite=False
    )

    assert res.status == "SUCCESS"
    assert res.target_database == isolated_target
    assert res.tables_restored > 0


def test_restore_blocks_active_database_overwrite(temp_backup_dir):
    """
    CRITICAL SECURITY & RELIABILITY TEST:
    Restoring directly into settings.POSTGRES_DB without explicit flag is forbidden.
    """
    manager = BackupManager(
        local_dir=temp_backup_dir,
        pg_dump_runner=dummy_pg_dump_runner,
        pg_restore_runner=dummy_pg_restore_runner
    )

    meta = manager.create_backup()

    with pytest.raises(BackupSecurityError) as exc_info:
        manager.restore_backup(
            filename=meta.filename,
            target_database=settings.POSTGRES_DB,
            allow_active_db_overwrite=False
        )

    assert "SAFETY VIOLATION" in str(exc_info.value)
    assert "Direct restore into active database" in str(exc_info.value)


def test_restore_corrupted_artifact_fails_safely(temp_backup_dir):
    manager = BackupManager(
        local_dir=temp_backup_dir,
        pg_dump_runner=dummy_pg_dump_runner,
        pg_restore_runner=dummy_pg_restore_runner
    )

    # Create corrupted dump file (missing custom format header)
    corrupted_fn = "corrupted_archive.dump"
    corrupted_path = os.path.join(temp_backup_dir, corrupted_fn)
    with open(corrupted_path, "wb") as f:
        f.write(b"CORRUPTED_GARBAGE_HEADER_DATA_12345")

    with pytest.raises(BackupError) as exc_info:
        manager.restore_backup(
            filename=corrupted_fn,
            target_database="standbharat_isolated_test"
        )

    assert "Restore failed" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 6. Celery Background Task Decoupling Test
# ---------------------------------------------------------------------------

def test_celery_backup_task_executes_decoupled(temp_backup_dir):
    with patch("app.backup.tasks.BackupManager") as MockManagerClass:
        mock_instance = MagicMock()
        mock_instance.create_backup.return_value = BackupMetadata(
            backup_id="celery_test_123",
            filename="standbharat_celery.dump",
            db_name="standbharat_db",
            timestamp=datetime.now(timezone.utc).isoformat(),
            file_size_bytes=1024,
            unencrypted_sha256="abc",
            encrypted=False,
            status="SUCCESS"
        )
        MockManagerClass.return_value = mock_instance

        res = execute_scheduled_backup()
        assert res["status"] == "SUCCESS"
        assert res["backup_id"] == "celery_test_123"
        assert res["file_size_bytes"] == 1024


# ---------------------------------------------------------------------------
# 7. Credential Redaction Test
# ---------------------------------------------------------------------------

def test_credentials_redacted_in_backup_error_logging():
    raw_error = (
        "Fatal: connection failed: postgresql://standbharat_user:super_secret_db_pass@127.0.0.1:5432/standbharat_db "
        "using BACKUP_ENCRYPTION_KEY=k4P9_k_qX8k3qG0Q5_v5x6mZ_y6_Wz1-q8e6_l_u_r0= and bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token"
    )
    sanitized = sanitize_error_message(raw_error)

    assert "super_secret_db_pass" not in sanitized
    assert "k4P9_k_qX8k3qG0Q5_v5x6mZ_y6_Wz1-q8e6_l_u_r0=" not in sanitized
    assert "[REDACTED]" in sanitized or "[REDACTED_ENCRYPTION_KEY]" in sanitized


# ---------------------------------------------------------------------------
# 8. Read-Only API Status Endpoint Test
# ---------------------------------------------------------------------------

def test_api_backup_status_endpoint():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api import deps
    from app.models.all_models import User
    import uuid

    fake_user = User(id=uuid.uuid4(), email="admin@standbharat.com", name="Admin")
    app.dependency_overrides[deps.get_current_user] = lambda: fake_user

    client = TestClient(app)
    try:
        resp = client.get("/api/backup/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "backup_enabled" in data
        assert "storage_backend" in data
        assert "total_backups_tracked" in data
        assert "recent_backups" in data
    finally:
        app.dependency_overrides.pop(deps.get_current_user, None)
