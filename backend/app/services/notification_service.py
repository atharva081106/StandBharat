from sqlalchemy.orm import Session
from app.models.all_models import Notification
import uuid

class NotificationService:
    def create_notification(self, db: Session, workspace_id: uuid.UUID, brand_id: uuid.UUID, title: str, message: str, type: str = "info", severity: str = "normal", user_id: uuid.UUID = None, entity_type: str = None, entity_id: str = None):
        notif = Notification(
            workspace_id=workspace_id,
            brand_id=brand_id,
            title=title,
            message=message,
            type=type,
            severity=severity,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    def get_notifications(self, db: Session, workspace_id: uuid.UUID, brand_id: uuid.UUID, limit: int = 50):
        return db.query(Notification).filter(
            Notification.workspace_id == workspace_id,
            Notification.brand_id == brand_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()

    def get_unread_count(self, db: Session, workspace_id: uuid.UUID, brand_id: uuid.UUID):
        return db.query(Notification).filter(
            Notification.workspace_id == workspace_id,
            Notification.brand_id == brand_id,
            Notification.read == False
        ).count()

    def mark_as_read(self, db: Session, notification_id: uuid.UUID, workspace_id: uuid.UUID):
        notif = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.workspace_id == workspace_id
        ).first()
        if notif:
            notif.read = True
            db.commit()
        return notif

    def mark_all_as_read(self, db: Session, workspace_id: uuid.UUID, brand_id: uuid.UUID):
        db.query(Notification).filter(
            Notification.workspace_id == workspace_id,
            Notification.brand_id == brand_id,
            Notification.read == False
        ).update({"read": True})
        db.commit()

notification_service = NotificationService()
