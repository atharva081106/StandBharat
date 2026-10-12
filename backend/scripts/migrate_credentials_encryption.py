"""
StandBharat - Database Credential Encryption Migration & Rollback Utility
Phase 38B: Dedicated DB Encryption Key & Backward-Compatible Migration

Inspects, safely migrates, and rolls back encryption of stored integration credentials
between legacy SECRET_KEY-derived encryption and dedicated DB_ENCRYPTION_KEY encryption.

Features:
- Status inspection without modifying records.
- Dry-run verification mode.
- Atomic live migration with mandatory rollback snapshot generation.
- Atomic rollback from backup snapshot.
- Fails closed on any decryption or verification error.
- Never logs, prints, or exposes plaintext secrets or encryption keys.
"""

import sys
import os
import json
import logging
import argparse
import datetime
from typing import Dict, Any, List, Optional

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.all_models import Integration
from app.publishing.models import PublisherConnection
from app.core.config import settings
from app.core.encryption import (
    get_encryption_engine,
    encrypt,
    decrypt,
    re_encrypt,
    is_encrypted_with_primary_key,
    is_encrypted_with_legacy_key,
    get_token_key_source,
    EncryptionError,
    EncryptionKeyMissingError,
    DecryptionError,
)
from app.core.security import sanitize_error_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("credentials_migration")


class MigrationError(Exception):
    """Raised when migration cannot proceed safely."""
    pass


def inspect_credentials_status(db: Session, engine=None) -> Dict[str, Any]:
    """
    Scans Integration and PublisherConnection records to classify ciphertext status.
    Returns aggregated metrics without exposing secret values.
    """
    eng = engine or get_encryption_engine()
    
    summary = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "total_checked": 0,
        "already_primary_key": 0,
        "legacy_key_eligible": 0,
        "unreadable_corrupt": 0,
        "empty_or_null": 0,
        "records": []
    }

    # 1. Inspect Integration table
    integrations = db.query(Integration).all()
    for row in integrations:
        summary["total_checked"] += 1
        raw_val = row.credentials_encrypted
        if not raw_val:
            summary["empty_or_null"] += 1
            continue

        try:
            key_source = get_token_key_source(raw_val, engine=eng)
            if key_source == "primary":
                summary["already_primary_key"] += 1
                status = "PRIMARY_KEY"
            elif key_source == "legacy":
                summary["legacy_key_eligible"] += 1
                status = "LEGACY_KEY"
            else:
                summary["unreadable_corrupt"] += 1
                status = "UNREADABLE"
        except Exception:
            summary["unreadable_corrupt"] += 1
            status = "UNREADABLE"

        summary["records"].append({
            "table": "integration",
            "id": str(row.id),
            "provider": row.provider,
            "status": status,
        })

    # 2. Inspect PublisherConnection table
    pub_connections = db.query(PublisherConnection).all()
    for row in pub_connections:
        summary["total_checked"] += 1
        raw_val = row.encrypted_credentials
        if not raw_val:
            summary["empty_or_null"] += 1
            continue

        try:
            key_source = get_token_key_source(raw_val, engine=eng)
            if key_source == "primary":
                summary["already_primary_key"] += 1
                status = "PRIMARY_KEY"
            elif key_source == "legacy":
                summary["legacy_key_eligible"] += 1
                status = "LEGACY_KEY"
            else:
                summary["unreadable_corrupt"] += 1
                status = "UNREADABLE"
        except Exception:
            summary["unreadable_corrupt"] += 1
            status = "UNREADABLE"

        summary["records"].append({
            "table": "publisher_connection",
            "id": str(row.id),
            "platform": row.platform,
            "status": status,
        })

    return summary


def run_dry_run_migration(db: Session, engine=None) -> Dict[str, Any]:
    """
    Simulates migration of legacy records in-memory.
    Validates that every legacy record can be decrypted and re-encrypted,
    and that the new ciphertext correctly round-trips to identical plaintext.
    Does NOT commit changes to the database.
    """
    eng = engine or get_encryption_engine()
    
    if not settings.DB_ENCRYPTION_KEY and engine is None:
        raise MigrationError(
            "DB_ENCRYPTION_KEY is not configured in settings. Cannot run migration without dedicated key."
        )

    status_data = inspect_credentials_status(db, engine=eng)
    if status_data["unreadable_corrupt"] > 0:
        raise MigrationError(
            f"Fail-closed: Found {status_data['unreadable_corrupt']} unreadable record(s). "
            "Migration cannot proceed while corrupted records exist."
        )

    migratable_count = 0
    verified_count = 0

    # Test Integration rows
    for rec_meta in status_data["records"]:
        if rec_meta["status"] != "LEGACY_KEY":
            continue

        migratable_count += 1
        if rec_meta["table"] == "integration":
            row = db.query(Integration).filter(Integration.id == rec_meta["id"]).first()
            raw_ciphertext = row.credentials_encrypted
        else:
            row = db.query(PublisherConnection).filter(PublisherConnection.id == rec_meta["id"]).first()
            raw_ciphertext = row.encrypted_credentials

        # Round-trip verification simulation
        plaintext = decrypt(raw_ciphertext, engine=eng)
        new_ciphertext = re_encrypt(raw_ciphertext, engine=eng)
        round_trip = decrypt(new_ciphertext, engine=eng)

        if round_trip != plaintext:
            raise MigrationError(
                f"Verification failure on record {rec_meta['id']}: Decrypted plaintext mismatch."
            )
        verified_count += 1

    return {
        "mode": "DRY_RUN",
        "migratable_records": migratable_count,
        "verified_simulations": verified_count,
        "already_primary_key": status_data["already_primary_key"],
        "unreadable_corrupt": status_data["unreadable_corrupt"],
        "status": "READY_FOR_MIGRATION"
    }


def execute_migration(
    db: Session,
    engine=None,
    backup_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes live re-encryption of legacy credentials to DB_ENCRYPTION_KEY.
    1. Writes an atomic rollback snapshot containing original ciphertexts.
    2. Re-encrypts each row and verifies round-trip decryption.
    3. Commits transaction only if all records succeed.
    4. Fails closed and rolls back on any error.
    """
    eng = engine or get_encryption_engine()

    if not settings.DB_ENCRYPTION_KEY and engine is None:
        raise MigrationError(
            "DB_ENCRYPTION_KEY is not configured. Dedicated encryption key is required."
        )

    # Pre-flight check
    status_data = inspect_credentials_status(db, engine=eng)
    if status_data["unreadable_corrupt"] > 0:
        raise MigrationError(
            f"Fail-closed: Found {status_data['unreadable_corrupt']} unreadable record(s). Aborting."
        )

    legacy_records = [r for r in status_data["records"] if r["status"] == "LEGACY_KEY"]
    if not legacy_records:
        return {
            "mode": "EXECUTE_MIGRATION",
            "migrated_count": 0,
            "status": "NO_MIGRATION_NEEDED",
            "message": "All existing records are already encrypted with primary key."
        }

    # Prepare rollback snapshot directory
    out_dir = backup_dir or os.path.join(
        getattr(settings, "BACKUP_LOCAL_DIR", "storage/backups/postgresql"),
        "credential_migrations"
    )
    os.makedirs(out_dir, exist_ok=True)
    timestamp_str = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    snapshot_path = os.path.join(out_dir, f"rollback_snapshot_{timestamp_str}.json")

    # Capture snapshot data (contains ciphertexts only, never plaintext secrets)
    snapshot_data = {
        "created_at": datetime.datetime.utcnow().isoformat(),
        "total_migrated": len(legacy_records),
        "records": []
    }

    try:
        migrated_count = 0
        for rec_meta in legacy_records:
            if rec_meta["table"] == "integration":
                row = db.query(Integration).filter(Integration.id == rec_meta["id"]).first()
                original_ciphertext = row.credentials_encrypted
                
                snapshot_data["records"].append({
                    "table": "integration",
                    "id": str(row.id),
                    "original_ciphertext": original_ciphertext
                })

                # Decrypt original, re-encrypt under primary key
                plaintext = decrypt(original_ciphertext, engine=eng)
                new_ciphertext = re_encrypt(original_ciphertext, engine=eng)

                # Round-trip verify
                verify_pt = decrypt(new_ciphertext, engine=eng)
                if verify_pt != plaintext:
                    raise MigrationError(f"Verification failure on Integration {row.id}")

                row.credentials_encrypted = new_ciphertext
                migrated_count += 1

            elif rec_meta["table"] == "publisher_connection":
                row = db.query(PublisherConnection).filter(PublisherConnection.id == rec_meta["id"]).first()
                original_ciphertext = row.encrypted_credentials

                snapshot_data["records"].append({
                    "table": "publisher_connection",
                    "id": str(row.id),
                    "original_ciphertext": original_ciphertext
                })

                plaintext = decrypt(original_ciphertext, engine=eng)
                new_ciphertext = re_encrypt(original_ciphertext, engine=eng)

                verify_pt = decrypt(new_ciphertext, engine=eng)
                if verify_pt != plaintext:
                    raise MigrationError(f"Verification failure on PublisherConnection {row.id}")

                row.encrypted_credentials = new_ciphertext
                migrated_count += 1

        # Write rollback snapshot before database commit
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, indent=2)

        # Atomic commit
        db.commit()

        logger.info(
            "Successfully migrated %d record(s) to DB_ENCRYPTION_KEY. Rollback file: %s",
            migrated_count,
            snapshot_path
        )
        return {
            "mode": "EXECUTE_MIGRATION",
            "migrated_count": migrated_count,
            "rollback_file": snapshot_path,
            "status": "SUCCESS"
        }

    except Exception as e:
        db.rollback()
        logger.error("Migration failed, transaction rolled back safely: %s", sanitize_error_message(str(e)))
        raise


def execute_rollback(db: Session, backup_file_path: str) -> Dict[str, Any]:
    """
    Restores original ciphertexts from the rollback snapshot.
    Fails closed if the rollback snapshot is invalid or corrupted.
    """
    if not os.path.isfile(backup_file_path):
        raise MigrationError(f"Rollback file not found: {backup_file_path}")

    try:
        with open(backup_file_path, "r", encoding="utf-8") as f:
            snapshot_data = json.load(f)
    except Exception as e:
        raise MigrationError(f"Invalid rollback file format: {e}")

    records = snapshot_data.get("records", [])
    if not records:
        raise MigrationError("Rollback file contains no records to restore.")

    restored_count = 0
    try:
        for item in records:
            table = item.get("table")
            row_id = item.get("id")
            original_ciphertext = item.get("original_ciphertext")

            if table == "integration":
                row = db.query(Integration).filter(Integration.id == row_id).first()
                if row:
                    row.credentials_encrypted = original_ciphertext
                    restored_count += 1
            elif table == "publisher_connection":
                row = db.query(PublisherConnection).filter(PublisherConnection.id == row_id).first()
                if row:
                    row.encrypted_credentials = original_ciphertext
                    restored_count += 1

        db.commit()
        logger.info("Successfully restored %d record(s) from %s", restored_count, backup_file_path)
        return {
            "mode": "ROLLBACK",
            "restored_count": restored_count,
            "rollback_file": backup_file_path,
            "status": "SUCCESS"
        }
    except Exception as e:
        db.rollback()
        logger.error("Rollback failed, transaction aborted: %s", sanitize_error_message(str(e)))
        raise


def main():
    parser = argparse.ArgumentParser(
        description="StandBharat Credential Encryption Migration & Rollback Utility"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="Inspect credential encryption status")
    group.add_argument("--dry-run", action="store_true", help="Simulate migration without committing changes")
    group.add_argument("--migrate", action="store_true", help="Execute live migration to dedicated DB_ENCRYPTION_KEY")
    group.add_argument("--rollback", action="store_true", help="Roll back migration from snapshot file")
    
    parser.add_argument("--backup-file", type=str, help="Path to rollback snapshot file (required for --rollback)")
    parser.add_argument("--confirm", action="store_true", help="Confirmation flag required for live migration")

    args = parser.parse_args()
    db = SessionLocal()

    try:
        if args.status:
            res = inspect_credentials_status(db)
            print("=" * 60)
            print("STANDBHARAT CREDENTIAL ENCRYPTION STATUS REPORT")
            print("=" * 60)
            print(f"Timestamp:             {res['timestamp']}")
            print(f"Total Records Checked: {res['total_checked']}")
            print(f"Primary Key (New):     {res['already_primary_key']}")
            print(f"Legacy Key (Eligible): {res['legacy_key_eligible']}")
            print(f"Unreadable / Corrupt:  {res['unreadable_corrupt']}")
            print(f"Empty / Unconfigured:  {res['empty_or_null']}")
            print("=" * 60)

        elif args.dry_run:
            res = run_dry_run_migration(db)
            print("=" * 60)
            print("STANDBHARAT MIGRATION DRY-RUN REPORT")
            print("=" * 60)
            print(f"Migratable Records:    {res['migratable_records']}")
            print(f"Verified Simulations:  {res['verified_simulations']}")
            print(f"Status:                {res['status']}")
            print("=" * 60)

        elif args.migrate:
            if not args.confirm:
                print("Error: --confirm flag is required to execute live migration.")
                sys.exit(1)
            res = execute_migration(db)
            print("=" * 60)
            print("STANDBHARAT MIGRATION EXECUTION REPORT")
            print("=" * 60)
            print(f"Migrated Count:        {res['migrated_count']}")
            print(f"Rollback Snapshot:     {res.get('rollback_file', 'None')}")
            print(f"Status:                {res['status']}")
            print("=" * 60)

        elif args.rollback:
            if not args.backup_file:
                print("Error: --backup-file <path> is required for --rollback.")
                sys.exit(1)
            res = execute_rollback(db, args.backup_file)
            print("=" * 60)
            print("STANDBHARAT ROLLBACK EXECUTION REPORT")
            print("=" * 60)
            print(f"Restored Count:        {res['restored_count']}")
            print(f"Rollback Snapshot:     {res['rollback_file']}")
            print(f"Status:                {res['status']}")
            print("=" * 60)

    except Exception as exc:
        print(f"ERROR: {sanitize_error_message(str(exc))}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
