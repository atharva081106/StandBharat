"""
Celery Background Tasks for Automated PostgreSQL Backups
Executes asynchronous backups on schedule via Celery Beat, completely decoupled
from user-facing API request lifecycles.
"""

import logging
from typing import Dict, Any
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.security import sanitize_error_message
from app.backup.engine import BackupManager, BackupError

logger = logging.getLogger(__name__)

@celery_app.task(
    name="app.backup.tasks.execute_scheduled_backup",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    acks_late=True
)
def execute_scheduled_backup(self) -> Dict[str, Any]:
    """
    Automated background Celery task executing periodic PostgreSQL backup.
    Never prints or logs database passwords, encryption keys, or dump contents.
    """
    if not settings.BACKUP_ENABLED:
        logger.info("Automated PostgreSQL backup is disabled via BACKUP_ENABLED=False.")
        return {"status": "SKIPPED", "reason": "BACKUP_ENABLED is False"}

    logger.info("Starting automated scheduled PostgreSQL backup...")
    try:
        manager = BackupManager()
        meta = manager.create_backup()
        logger.info(
            f"Automated PostgreSQL backup completed successfully: "
            f"filename={meta.filename}, size={meta.file_size_bytes}B, "
            f"encrypted={meta.encrypted}, cold_storage_uploaded={meta.cold_storage_uploaded}"
        )
        return {
            "status": "SUCCESS",
            "backup_id": meta.backup_id,
            "filename": meta.filename,
            "timestamp": meta.timestamp,
            "file_size_bytes": meta.file_size_bytes,
            "encrypted": meta.encrypted,
            "cold_storage_uploaded": meta.cold_storage_uploaded,
            "cold_storage_error": meta.cold_storage_error
        }
    except Exception as exc:
        sanitized_err = sanitize_error_message(str(exc))
        logger.error(f"Scheduled PostgreSQL backup encountered an error: {sanitized_err}")
        try:
            # Retry after delay if transient failure
            raise self.retry(exc=exc)
        except Exception:
            return {
                "status": "FAILED",
                "error": sanitized_err
            }
