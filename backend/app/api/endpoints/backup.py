"""
Read-Only Backup Status & Observability Endpoints
Provides system administrators visibility into backup health, latest dump status,
and cold storage synchronizations.
Does NOT couple blocking backup executions to HTTP requests.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from app.api import deps
from app.models.all_models import User
from app.core.config import settings
from app.backup.engine import BackupManager

router = APIRouter()

@router.get("/status", response_model=Dict[str, Any])
def get_backup_status(
    current_user: User = Depends(deps.get_current_user),
) -> Dict[str, Any]:
    """
    Returns administrative status of the automated PostgreSQL backup subsystem.
    Read-only inspection; backups are scheduled and run asynchronously via Celery.
    """
    manager = BackupManager()
    backups = manager.list_backups()
    latest = manager.get_latest_successful_backup()

    return {
        "backup_enabled": settings.BACKUP_ENABLED,
        "storage_backend": settings.BACKUP_STORAGE_BACKEND,
        "schedule": settings.BACKUP_SCHEDULE_CRON,
        "retention_count": settings.BACKUP_RETENTION_COUNT,
        "retention_days": settings.BACKUP_RETENTION_DAYS,
        "encryption_enabled": manager.encryption_enabled,
        "total_backups_tracked": len(backups),
        "latest_successful_backup": latest.model_dump() if latest else None,
        "recent_backups": [b.model_dump() for b in backups[:5]],
    }
