"""
StandBharat - Phase 38B: DB Encryption Key & Migration Test Suite
Tests dedicated DB_ENCRYPTION_KEY, backward compatibility, fail-closed handling,
redaction, migration dry-run, live re-encryption, rollback, and corrupted record handling.
"""

import os
import json
import uuid
import pytest
from cryptography.fernet import Fernet

from app.core.config import settings
from app.core.encryption import (
    get_encryption_engine,
    encrypt,
    decrypt,
    re_encrypt,
    derive_fernet_key,
    derive_legacy_fernet_key,
    get_primary_fernet,
    get_legacy_fernet,
    is_encrypted_with_primary_key,
    is_encrypted_with_legacy_key,
    get_token_key_source,
    EncryptionError,
    EncryptionKeyMissingError,
    DecryptionError,
)
from app.core.security import sanitize_error_message
from app.db.session import SessionLocal, engine
from app.models.all_models import Base, Workspace, Brand, User, Integration
from app.publishing.models import PublisherConnection
from app.publishing.service import PublishingService
from scripts.migrate_credentials_encryption import (
    inspect_credentials_status,
    run_dry_run_migration,
    execute_migration,
    execute_rollback,
    MigrationError,
)

# Deterministic test keys
TEST_SECRET_KEY = "legacy-secret-key-32-chars-long!!"
TEST_DB_KEY_1 = Fernet.generate_key().decode()
TEST_DB_KEY_2 = Fernet.generate_key().decode()
WRONG_KEY = Fernet.generate_key().decode()


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def setup_models(db_session):
    u = User(email=f"encrypt_test_{uuid.uuid4().hex[:6]}@example.com", hashed_password="pwd")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    ws = Workspace(name="Test Encryption WS", slug=f"enc-ws-{uuid.uuid4().hex[:6]}", owner_id=u.id)
    db_session.add(ws)
    db_session.commit()
    db_session.refresh(ws)

    b = Brand(name="Test Brand Enc", workspace_id=ws.id)
    db_session.add(b)
    db_session.commit()
    db_session.refresh(b)

    return {"user": u, "workspace": ws, "brand": b}


# -----------------------------------------------------------------------------
# 1. Cryptographic Primitive & Engine Tests
# -----------------------------------------------------------------------------

def test_new_key_encryption_and_decryption():
    """Verifies that encrypt and decrypt round-trip with dedicated DB_ENCRYPTION_KEY."""
    engine = get_encryption_engine(db_key=TEST_DB_KEY_1, secret_key=TEST_SECRET_KEY)
    plaintext = json.dumps({"access_token": "token_123", "client_secret": "secret_abc"})
    
    ciphertext = encrypt(plaintext, engine=engine)
    assert ciphertext != plaintext
    assert isinstance(ciphertext, str)

    decrypted = decrypt(ciphertext, engine=engine)
    assert decrypted == plaintext


def test_legacy_credential_compatibility_fallback():
    """Verifies that credentials encrypted with legacy SECRET_KEY can be decrypted by engine with fallback."""
    legacy_engine = get_encryption_engine(db_key=None, secret_key=TEST_SECRET_KEY, allow_fallback=True)
    plaintext = json.dumps({"legacy_token": "secret_legacy_999"})
    
    # Encrypt using legacy key
    legacy_ciphertext = encrypt(plaintext, engine=legacy_engine)

    # Engine with dedicated DB_ENCRYPTION_KEY + fallback enabled
    new_engine = get_encryption_engine(db_key=TEST_DB_KEY_1, secret_key=TEST_SECRET_KEY, allow_fallback=True)
    
    # Decryption must succeed via fallback
    decrypted = decrypt(legacy_ciphertext, engine=new_engine)
    assert decrypted == plaintext
    assert get_token_key_source(legacy_ciphertext, engine=new_engine) == "legacy"


def test_primary_key_precedence_on_write():
    """Verifies that new encryptions strictly use the primary DB_ENCRYPTION_KEY."""
    multi_engine = get_encryption_engine(db_key=TEST_DB_KEY_1, secret_key=TEST_SECRET_KEY, allow_fallback=True)
    plaintext = json.dumps({"new_oauth_token": "tok_new_555"})
    
    new_ciphertext = encrypt(plaintext, engine=multi_engine)
    assert get_token_key_source(new_ciphertext, engine=multi_engine) == "primary"

    # A legacy engine (SECRET_KEY only) MUST NOT be able to decrypt it
    legacy_only_engine = get_encryption_engine(db_key=None, secret_key=TEST_SECRET_KEY, allow_fallback=True)
    with pytest.raises(DecryptionError):
        decrypt(new_ciphertext, engine=legacy_only_engine)


def test_key_independence_rotating_secret_key():
    """Verifies that rotating SECRET_KEY does not break DB_ENCRYPTION_KEY encrypted records."""
    engine_old_secret = get_encryption_engine(db_key=TEST_DB_KEY_1, secret_key=TEST_SECRET_KEY)
    plaintext = "super_sensitive_token"
    ciphertext = encrypt(plaintext, engine=engine_old_secret)

    # Rotate SECRET_KEY completely
    rotated_secret = "brand-new-rotated-secret-key-32ch!!"
    engine_new_secret = get_encryption_engine(db_key=TEST_DB_KEY_1, secret_key=rotated_secret)

    # Decryption must still succeed seamlessly because primary DB key is untouched
    decrypted = decrypt(ciphertext, engine=engine_new_secret)
    assert decrypted == plaintext


# -----------------------------------------------------------------------------
# 2. Fail-Closed & Error Handling Tests
# -----------------------------------------------------------------------------

def test_wrong_key_fails_closed():
    """Verifies that decryption fails closed with DecryptionError on incorrect key."""
    engine_a = get_encryption_engine(db_key=TEST_DB_KEY_1, allow_fallback=False)
    engine_b = get_encryption_engine(db_key=WRONG_KEY, allow_fallback=False)

    ciphertext = encrypt("secret_content", engine=engine_a)

    with pytest.raises(DecryptionError) as exc_info:
        decrypt(ciphertext, engine=engine_b)

    assert "Failed to decrypt credentials" in str(exc_info.value)
    # Ensure no secret content or raw keys leaked in exception
    assert "secret_content" not in str(exc_info.value)
    assert TEST_DB_KEY_1 not in str(exc_info.value)


def test_missing_key_fails_closed():
    """Verifies that missing keys raise EncryptionKeyMissingError rather than proceeding."""
    with pytest.raises(EncryptionKeyMissingError):
        get_encryption_engine(db_key=None, secret_key=None, allow_fallback=False)


def test_corrupted_ciphertext_fails_closed():
    """Verifies that corrupted or tampered ciphertext raises DecryptionError and never returns empty string."""
    engine = get_encryption_engine(db_key=TEST_DB_KEY_1)
    corrupted = "gAAAAABlZ" + "x" * 60 + "=="

    with pytest.raises(DecryptionError):
        decrypt(corrupted, engine=engine)


def test_sanitization_and_redaction():
    """Verifies that sanitize_error_message redacts Fernet keys, passwords, and tokens."""
    sample_error = (
        f"Database error with db_encryption_key={TEST_DB_KEY_1} and "
        "access_token=ya29.a0AfH6SMDhg73498hg34h98gh34 and password=SuperSecretPassword123"
    )
    sanitized = sanitize_error_message(sample_error)
    assert TEST_DB_KEY_1 not in sanitized
    assert "ya29.a0AfH6SMDhg73498hg34h98gh34" not in sanitized
    assert "SuperSecretPassword123" not in sanitized
    assert "[REDACTED" in sanitized


# -----------------------------------------------------------------------------
# 3. Migration, Dry-Run & Rollback Tests
# -----------------------------------------------------------------------------

def test_migration_dry_run_and_execution(db_session, setup_models, tmp_path):
    """
    Tests the full migration lifecycle:
    1. Create records encrypted with legacy key.
    2. Inspect status.
    3. Run dry-run migration (validates without committing).
    4. Execute live migration (updates to primary key, writes rollback snapshot).
    5. Verify all rows are now primary key.
    6. Roll back using snapshot and confirm original ciphertexts are restored.
    """
    ws = setup_models["workspace"]
    b = setup_models["brand"]

    # 1. Setup legacy records
    legacy_engine = get_encryption_engine(db_key=None, secret_key=TEST_SECRET_KEY, allow_fallback=True)
    plain_1 = json.dumps({"token": "integ_token_123"})
    plain_2 = json.dumps({"token": "conn_token_456"})

    integ = Integration(
        workspace_id=ws.id,
        brand_id=b.id,
        provider="linkedin",
        status="CONNECTED",
        credentials_encrypted=encrypt(plain_1, engine=legacy_engine)
    )
    conn = PublisherConnection(
        workspace_id=ws.id,
        brand_id=b.id,
        platform="linkedin",
        status="CONNECTED",
        encrypted_credentials=encrypt(plain_2, engine=legacy_engine)
    )
    db_session.add_all([integ, conn])
    db_session.commit()

    orig_integ_cipher = integ.credentials_encrypted
    orig_conn_cipher = conn.encrypted_credentials

    # Engine with dedicated DB key + legacy fallback
    mig_engine = get_encryption_engine(db_key=TEST_DB_KEY_2, secret_key=TEST_SECRET_KEY, allow_fallback=True)

    # 2. Inspect status
    status_report = inspect_credentials_status(db_session, engine=mig_engine)
    assert status_report["legacy_key_eligible"] >= 2
    assert status_report["unreadable_corrupt"] == 0

    # 3. Dry-run
    dry_res = run_dry_run_migration(db_session, engine=mig_engine)
    assert dry_res["migratable_records"] >= 2
    assert dry_res["status"] == "READY_FOR_MIGRATION"

    # Database must still have original legacy ciphertexts
    db_session.refresh(integ)
    db_session.refresh(conn)
    assert integ.credentials_encrypted == orig_integ_cipher
    assert conn.encrypted_credentials == orig_conn_cipher

    # 4. Execute migration
    backup_folder = str(tmp_path / "backups")
    mig_res = execute_migration(db_session, engine=mig_engine, backup_dir=backup_folder)
    assert mig_res["status"] == "SUCCESS"
    assert mig_res["migrated_count"] >= 2
    rollback_file = mig_res["rollback_file"]
    assert os.path.isfile(rollback_file)

    # 5. Verify records updated to primary key
    db_session.refresh(integ)
    db_session.refresh(conn)
    assert integ.credentials_encrypted != orig_integ_cipher
    assert conn.encrypted_credentials != orig_conn_cipher
    assert get_token_key_source(integ.credentials_encrypted, engine=mig_engine) == "primary"
    assert get_token_key_source(conn.encrypted_credentials, engine=mig_engine) == "primary"
    assert decrypt(integ.credentials_encrypted, engine=mig_engine) == plain_1
    assert decrypt(conn.encrypted_credentials, engine=mig_engine) == plain_2

    # 6. Execute rollback
    rb_res = execute_rollback(db_session, rollback_file)
    assert rb_res["status"] == "SUCCESS"
    assert rb_res["restored_count"] >= 2

    # Confirm ciphertexts are exactly restored to original
    db_session.refresh(integ)
    db_session.refresh(conn)
    assert integ.credentials_encrypted == orig_integ_cipher
    assert conn.encrypted_credentials == orig_conn_cipher


def test_migration_fails_closed_on_corrupt_record(db_session, setup_models, tmp_path):
    """Verifies that migration aborts and rolls back atomically if any corrupted record exists."""
    ws = setup_models["workspace"]
    b = setup_models["brand"]

    mig_engine = get_encryption_engine(db_key=TEST_DB_KEY_1, secret_key=TEST_SECRET_KEY, allow_fallback=True)

    # Valid legacy record
    valid_integ = Integration(
        workspace_id=ws.id,
        brand_id=b.id,
        provider="ga4",
        status="CONNECTED",
        credentials_encrypted=encrypt(json.dumps({"token": "valid"}), engine=get_encryption_engine(db_key=None, secret_key=TEST_SECRET_KEY))
    )
    # Corrupt unreadable record
    corrupt_integ = Integration(
        workspace_id=ws.id,
        brand_id=b.id,
        provider="gsc",
        status="CONNECTED",
        credentials_encrypted="gAAAAAB_TOTAL_CORRUPTED_CIPHERTEXT=="
    )
    db_session.add_all([valid_integ, corrupt_integ])
    db_session.commit()

    # Pre-flight check in execute_migration must fail closed
    with pytest.raises(MigrationError) as exc_info:
        execute_migration(db_session, engine=mig_engine, backup_dir=str(tmp_path / "backups"))

    assert "unreadable record" in str(exc_info.value).lower()


# -----------------------------------------------------------------------------
# 4. Service Fail-Closed Behavior
# -----------------------------------------------------------------------------

def test_publishing_service_fails_closed_on_bad_decryption(db_session, setup_models):
    """Verifies that PublishingService.get_credentials raises DecryptionError rather than returning {}."""
    ws = setup_models["workspace"]
    b = setup_models["brand"]

    conn = PublisherConnection(
        workspace_id=ws.id,
        brand_id=b.id,
        platform="linkedin",
        status="CONNECTED",
        encrypted_credentials="gAAAAAB_CORRUPTED_CREDENTIALS=="
    )
    db_session.add(conn)
    db_session.commit()

    service = PublishingService(db_session)
    with pytest.raises(DecryptionError):
        service.get_credentials(conn)
