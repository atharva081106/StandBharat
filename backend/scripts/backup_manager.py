"""
StandBharat PostgreSQL Backup & Restore CLI Manager
Usage:
    python scripts/backup_manager.py --action backup [--db DBNAME]
    python scripts/backup_manager.py --action list
    python scripts/backup_manager.py --action verify --file FILENAME
    python scripts/backup_manager.py --action restore --file FILENAME [--target-db TARGET_DB]
    python scripts/backup_manager.py --action prune
"""

import sys
import os
import argparse
import json

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.backup.engine import BackupManager, BackupError

def main():
    parser = argparse.ArgumentParser(description="StandBharat PostgreSQL Backup & Restore Manager")
    parser.add_argument(
        "--action",
        choices=["backup", "list", "verify", "restore", "prune"],
        required=True,
        help="Action to perform: backup, list, verify, restore, or prune"
    )
    parser.add_argument("--db", default=None, help="Database name to back up (defaults to POSTGRES_DB)")
    parser.add_argument("--file", default=None, help="Backup filename for verify or restore actions")
    parser.add_argument("--target-db", default=None, help="Target isolated database for restore action")
    parser.add_argument(
        "--allow-active-db-overwrite",
        action="store_true",
        default=False,
        help="Explicitly permit restoring into active database (DISABLED by default for safety)"
    )

    args = parser.parse_args()
    manager = BackupManager()

    if args.action == "backup":
        print(f"[*] Starting PostgreSQL backup for database '{args.db or settings.POSTGRES_DB}'...")
        try:
            meta = manager.create_backup(db_name=args.db)
            print("[+] Backup SUCCESS!")
            print(f"    ID:         {meta.backup_id}")
            print(f"    File:       {meta.filename}")
            print(f"    Size:       {meta.file_size_bytes} bytes")
            print(f"    Encrypted:  {meta.encrypted}")
            print(f"    Checksum:   {meta.unencrypted_sha256}")
            print(f"    S3 Upload:  {meta.cold_storage_uploaded}")
            if meta.cold_storage_error:
                print(f"    S3 Warning: {meta.cold_storage_error}")
        except BackupError as e:
            print(f"[-] Backup FAILED: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.action == "list":
        backups = manager.list_backups()
        print(f"[*] Found {len(backups)} backups in manifest:")
        for b in backups:
            status_symbol = "[OK]" if b.status == "SUCCESS" else "[FAIL]"
            enc_tag = "[ENC]" if b.encrypted else "[RAW]"
            s3_tag = "[S3]" if b.cold_storage_uploaded else "[LOCAL]"
            print(f"  {status_symbol} {b.filename:<45} {b.file_size_bytes:>10}B  {enc_tag} {s3_tag}  {b.timestamp}")

    elif args.action == "verify":
        if not args.file:
            print("[-] Error: --file is required for verify action.", file=sys.stderr)
            sys.exit(1)
        print(f"[*] Verifying integrity of backup artifact '{args.file}'...")
        try:
            ok = manager.verify_backup(args.file)
            print(f"[+] Verification PASSED for '{args.file}'. Artifact is intact and valid.")
        except Exception as e:
            print(f"[-] Verification FAILED: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.action == "restore":
        if not args.file:
            print("[-] Error: --file is required for restore action.", file=sys.stderr)
            sys.exit(1)
        target = args.target_db or f"{settings.POSTGRES_DB}_restore_isolated"
        print(f"[*] Restoring backup '{args.file}' into isolated database '{target}'...")
        try:
            res = manager.restore_backup(
                filename=args.file,
                target_database=target,
                allow_active_db_overwrite=args.allow_active_db_overwrite
            )
            print("[+] Restore SUCCESS!")
            print(f"    Target Database: {res.target_database}")
            print(f"    Tables Restored: {res.tables_restored}")
            print(f"    Restored At:     {res.restored_at}")
        except Exception as e:
            print(f"[-] Restore FAILED: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.action == "prune":
        print("[*] Running retention pruning on older backups...")
        pruned = manager.prune_old_backups()
        if pruned:
            print(f"[+] Pruned {len(pruned)} expired backup(s): {', '.join(pruned)}")
        else:
            print("[+] No expired backups to prune. Last known-good and retention count protected.")

if __name__ == "__main__":
    main()
