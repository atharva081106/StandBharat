from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_brand, get_current_user
from app.models.all_models import Brand, User
from app.services.notification_service import notification_service
import uuid

router = APIRouter()

@router.get("/")
def get_notifications(
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    notifs = notification_service.get_notifications(db, workspace_id=brand.workspace_id, brand_id=brand.id)
    return [{
        "id": str(n.id),
        "type": n.type,
        "title": n.title,
        "message": n.message,
        "severity": n.severity,
        "read": n.read,
        "created_at": n.created_at
    } for n in notifs]

@router.get("/unread-count")
def get_xxx_unread_count(
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    count = notification_service.get_unread_count(db, workspace_id=brand.workspace_id, brand_id=brand.id)
    return {"unread_count": count}

@router.patch("/{notification_id}/read")
def mark_read(
    notification_id: uuid.UUID,
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    notif = notification_service.mark_as_read(db, notification_id, workspace_id=brand.workspace_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "SUCCESS"}

@router.post("/read-all")
def mark_all_read(
    brand: Brand = Depends(get_current_brand),
    db: Session = Depends(get_db)
):
    notification_service.mark_all_as_read(db, workspace_id=brand.workspace_id, brand_id=brand.id)
    return {"status": "SUCCESS"}
