import uuid
import datetime
import json
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.publishing.models import PublisherConnection, Publication, PublicationAttempt
from app.models.all_models import ContentDraft, ContentProject, ContentApproval
from app.publishing.registry import PublisherRegistry
from app.publishing.exceptions import NotConfiguredError
from app.core.encryption import decrypt
from typing import Dict, Any, Optional

class PublishingService:
    def __init__(self, db: Session):
        self.db = db

    def get_connection(self, workspace_id: uuid.UUID, brand_id: uuid.UUID, platform: str) -> Optional[PublisherConnection]:
        return self.db.query(PublisherConnection).filter(
            PublisherConnection.workspace_id == workspace_id,
            PublisherConnection.brand_id == brand_id,
            PublisherConnection.platform == platform
        ).first()

    def get_credentials(self, connection: PublisherConnection) -> Dict[str, Any]:
        if not connection or connection.status != "CONNECTED" or not connection.encrypted_credentials:
            return {}
        try:
            return json.loads(decrypt(connection.encrypted_credentials))
        except Exception:
            return {}

    def get_publication(self, publication_id: uuid.UUID, workspace_id: uuid.UUID) -> Optional[Publication]:
        return self.db.query(Publication).filter(
            Publication.id == publication_id,
            Publication.workspace_id == workspace_id
        ).first()

    def list_publications(self, workspace_id: uuid.UUID, brand_id: uuid.UUID) -> list[Publication]:
        return self.db.query(Publication).filter(
            Publication.workspace_id == workspace_id,
            Publication.brand_id == brand_id
        ).order_by(Publication.created_at.desc()).all()

    def enqueue_publish(
        self,
        workspace_id: uuid.UUID,
        brand_id: uuid.UUID,
        draft_id: uuid.UUID,
        platform: str,
        user_id: uuid.UUID
    ) -> Publication:
        # 1. Load content and verify ownership/status
        draft = self.db.query(ContentDraft).filter(
            ContentDraft.id == draft_id,
            ContentDraft.workspace_id == workspace_id,
            ContentDraft.brand_id == brand_id
        ).first()
        
        if not draft:
            raise HTTPException(status_code=404, detail="Content draft not found")
            
        # Verify approval status (Approval Boundary)
        approval = self.db.query(ContentApproval).filter(
            ContentApproval.content_draft_id == draft_id
        ).order_by(ContentApproval.created_at.desc()).first()
        
        if not approval or approval.status != "APPROVED":
            raise HTTPException(status_code=409, detail="Content is not approved for publishing")
            
        # 2. Check connection
        connection = self.get_connection(workspace_id, brand_id, platform)
        if not connection or connection.status != "CONNECTED":
            raise HTTPException(status_code=400, detail=f"{platform.capitalize()} is not connected")
            
        # 3. Generate Idempotency Key
        idemp_key = f"{workspace_id}:{brand_id}:{draft_id}:{platform}"
        
        # 4. Check for existing publication
        existing = self.db.query(Publication).filter(
            Publication.idempotency_key == idemp_key
        ).first()
        
        if existing:
            # If already published or publishing, don't duplicate
            if existing.status in ("PUBLISHED", "PUBLISHING", "QUEUED"):
                return existing
            # If failed, we can retry by creating a new attempt. 
            # In this simple model, we might just reuse the same publication object
            existing.status = "QUEUED"
            existing.error_code = None
            existing.error_message = None
            existing.updated_at = datetime.datetime.utcnow()
            self.db.commit()
            publication = existing
        else:
            # 5. Create new Publication
            publication = Publication(
                workspace_id=workspace_id,
                brand_id=brand_id,
                content_project_id=draft.content_project_id,
                content_draft_id=draft_id,
                platform=platform,
                status="QUEUED",
                idempotency_key=idemp_key,
                created_by=user_id
            )
            self.db.add(publication)
            self.db.commit()
            self.db.refresh(publication)

        # 6. Enqueue Celery Task
        from app.publishing.tasks import execute_publishing_task
        execute_publishing_task.delay(str(publication.id))
        
        return publication
