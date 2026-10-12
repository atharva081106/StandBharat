import uuid
import datetime
import json
import os
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.publishing.models import PublisherConnection, Publication, PublicationAttempt
from app.models.all_models import ContentDraft, ContentProject, ContentApproval
from app.publishing.registry import PublisherRegistry
from app.publishing.exceptions import NotConfiguredError
from app.core.encryption import decrypt
from app.core.config import settings
from app.core.security import sanitize_error_message
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PublishingService:
    def __init__(self, db: Session):
        self.db = db

    def get_connection(self, workspace_id: uuid.UUID, brand_id: uuid.UUID, platform: str) -> Optional[Any]:
        # 1. Authoritative Integration table check with alias support
        from app.models.all_models import Integration
        provider_name = platform
        if provider_name in ("x", "twitter"):
            provider_name = "twitter_x"

        integ = self.db.query(Integration).filter(
            Integration.workspace_id == workspace_id,
            Integration.brand_id == brand_id,
            Integration.provider == provider_name
        ).first()
        if integ and integ.status == "CONNECTED":
            return integ

        # 2. Backward-compatible fallback to PublisherConnection
        conn = self.db.query(PublisherConnection).filter(
            PublisherConnection.workspace_id == workspace_id,
            PublisherConnection.brand_id == brand_id,
            PublisherConnection.platform == platform
        ).first()
        if conn and conn.status == "CONNECTED":
            return conn

        return integ or conn

    def get_credentials(self, connection: Any) -> Dict[str, Any]:
        if not connection or connection.status != "CONNECTED":
            return {}
        encrypted = getattr(connection, "encrypted_credentials", None) or getattr(connection, "credentials_encrypted", None)
        if not encrypted:
            return {}
        try:
            return json.loads(decrypt(encrypted))
        except Exception as e:
            logger.error("Failed to decrypt credentials for connection: %s", type(e).__name__)
            raise

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
            ContentApproval.content_draft_id == draft_id,
            ContentApproval.workspace_id == workspace_id,
            ContentApproval.brand_id == brand_id
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
            if existing.status == "RECONCILIATION_REQUIRED":
                raise HTTPException(status_code=409, detail="Publication requires reconciliation before retrying")
            # If failed or blocked, we can retry by creating a new attempt. 
            existing.status = "QUEUED"
            existing.error_code = None
            existing.error_message = None
            existing.updated_at = datetime.datetime.utcnow()
            self.db.commit()
            publication = existing
        else:
            # 5. Create new Publication with concurrent idempotency protection
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
            try:
                self.db.add(publication)
                self.db.commit()
                self.db.refresh(publication)
            except IntegrityError:
                self.db.rollback()
                existing = self.db.query(Publication).filter(
                    Publication.idempotency_key == idemp_key
                ).first()
                if existing:
                    if existing.status in ("PUBLISHED", "PUBLISHING", "QUEUED"):
                        return existing
                    if existing.status == "RECONCILIATION_REQUIRED":
                        raise HTTPException(status_code=409, detail="Publication requires reconciliation before retrying")
                    existing.status = "QUEUED"
                    existing.error_code = None
                    existing.error_message = None
                    existing.updated_at = datetime.datetime.utcnow()
                    self.db.commit()
                    publication = existing
                else:
                    raise

        # 6. Enqueue Celery Task
        from app.publishing.tasks import execute_publishing_task
        try:
            execute_publishing_task.delay(str(publication.id))
        except Exception as e:
            # Handle Celery dispatch failure after DB commit
            sanitized_err = sanitize_error_message(f"Failed to enqueue publishing task: {str(e)}")
            publication.status = "FAILED"
            publication.error_code = "DISPATCH_FAILED"
            publication.error_message = sanitized_err
            
            attempt_number = str(len(publication.attempts) + 1)
            attempt = PublicationAttempt(
                publication_id=publication.id,
                attempt_number=attempt_number,
                status="FAILED",
                error_code="DISPATCH_FAILED",
                error_message=sanitized_err,
                started_at=datetime.datetime.utcnow(),
                completed_at=datetime.datetime.utcnow()
            )
            self.db.add(attempt)
            self.db.commit()
            
            raise HTTPException(
                status_code=500,
                detail=sanitized_err
            )
        
        return publication

    def recover_stale_publications(self, timeout_minutes: Optional[int] = None) -> dict:
        """
        Identifies publications stuck in PUBLISHING or RECOVERING beyond the timeout (default 1 hour).
        Uses concurrency-safe conditional database updates so concurrent recovery runs do not conflict.
        Revalidates publication attempts, external responses, approval status, and idempotency before retrying.
        """
        if timeout_minutes is None:
            try:
                env_val = os.environ.get("STALE_PUBLICATION_TIMEOUT_MINUTES")
                timeout_minutes = int(env_val) if env_val else getattr(settings, "STALE_PUBLICATION_TIMEOUT_MINUTES", 60)
                if timeout_minutes <= 0:
                    timeout_minutes = 60
            except (ValueError, TypeError):
                timeout_minutes = 60

        cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=timeout_minutes)

        stale_filter = and_(
            Publication.status.in_(["PUBLISHING", "RECOVERING"]),
            or_(
                Publication.updated_at <= cutoff_time,
                and_(Publication.updated_at.is_(None), Publication.created_at <= cutoff_time)
            )
        )

        candidate_ids = [
            row[0] for row in self.db.query(Publication.id).filter(stale_filter).all()
        ]

        claimed_count = 0
        recovered_count = 0
        actions_breakdown = {
            "RECOVERED_AS_PUBLISHED": 0,
            "BLOCKED_REVOKED_APPROVAL": 0,
            "MARKED_RECONCILIATION_REQUIRED": 0,
            "REQUEUED_FOR_RETRY": 0,
            "MARKED_FAILED": 0,
        }
        details = []

        for candidate_id in candidate_ids:
            # Concurrency-safe atomic conditional update to claim the record
            claim_count = self.db.query(Publication).filter(
                Publication.id == candidate_id,
                stale_filter
            ).update(
                {
                    "status": "RECOVERING",
                    "updated_at": datetime.datetime.utcnow()
                },
                synchronize_session=False
            )
            self.db.commit()

            if claim_count == 0:
                # Another recovery worker claimed it or status transitioned
                continue

            claimed_count += 1

            pub = self.db.query(Publication).filter(Publication.id == candidate_id).first()
            if not pub:
                continue

            # 1. Check if already confirmed published externally
            external_id = pub.external_post_id
            if not external_id and pub.attempts:
                for att in pub.attempts:
                    if att.response_metadata and isinstance(att.response_metadata, dict):
                        extracted = (
                            att.response_metadata.get("external_id")
                            or att.response_metadata.get("id")
                            or att.response_metadata.get("post_id")
                        )
                        if extracted:
                            external_id = str(extracted)
                            break

            if external_id or any(att.status == "SUCCESS" for att in pub.attempts):
                pub.status = "PUBLISHED"
                pub.external_post_id = external_id
                pub.published_at = pub.published_at or datetime.datetime.utcnow()
                pub.error_code = None
                pub.error_message = None
                pub.updated_at = datetime.datetime.utcnow()

                for att in pub.attempts:
                    if att.status in ("STARTED", "RECOVERING"):
                        att.status = "SUCCESS"
                        att.completed_at = att.completed_at or datetime.datetime.utcnow()
                        if not att.response_metadata:
                            att.response_metadata = {"recovery_resolution": "CONFIRMED_EXTERNAL_POST", "external_id": external_id}

                self.db.commit()
                recovered_count += 1
                actions_breakdown["RECOVERED_AS_PUBLISHED"] += 1
                details.append({"publication_id": str(pub.id), "action": "RECOVERED_AS_PUBLISHED", "status": "PUBLISHED"})
                continue

            # 2. Check ContentApproval status (workspace, brand, and draft isolation)
            approval = self.db.query(ContentApproval).filter(
                ContentApproval.content_draft_id == pub.content_draft_id,
                ContentApproval.workspace_id == pub.workspace_id,
                ContentApproval.brand_id == pub.brand_id
            ).order_by(ContentApproval.created_at.desc()).first()

            if not approval or approval.status != "APPROVED":
                reason = "Approval is missing or revoked" if not approval else f"Content approval status is '{approval.status}', expected 'APPROVED'"
                safe_err_msg = f"Publication blocked during stale recovery: {reason}. Explicit approval is required before publishing."

                pub.status = "BLOCKED"
                pub.error_code = "APPROVAL_REQUIRED"
                pub.error_message = safe_err_msg
                pub.updated_at = datetime.datetime.utcnow()

                for att in pub.attempts:
                    if att.status in ("STARTED", "RECOVERING"):
                        att.status = "BLOCKED"
                        att.error_code = "APPROVAL_REQUIRED"
                        att.error_message = safe_err_msg
                        att.completed_at = datetime.datetime.utcnow()

                self.db.commit()
                recovered_count += 1
                actions_breakdown["BLOCKED_REVOKED_APPROVAL"] += 1
                details.append({"publication_id": str(pub.id), "action": "BLOCKED_REVOKED_APPROVAL", "status": "BLOCKED"})
                continue

            # 3. Check for in-flight attempt (Uncertain external outcome)
            # If an attempt was started and has not terminated in failure, the provider call
            # may have executed before the worker died. Mark for reconciliation.
            has_in_flight_attempt = any(att.status in ("STARTED", "RECOVERING") for att in pub.attempts)
            if has_in_flight_attempt:
                uncertain_msg = (
                    "Publication recovery paused: external outcome is uncertain after worker crash. "
                    "Reconciliation required before retry to prevent duplicate publishing."
                )
                pub.status = "RECONCILIATION_REQUIRED"
                pub.error_code = "EXTERNAL_OUTCOME_UNCERTAIN"
                pub.error_message = uncertain_msg
                pub.updated_at = datetime.datetime.utcnow()

                for att in pub.attempts:
                    if att.status in ("STARTED", "RECOVERING"):
                        att.status = "UNCERTAIN"
                        att.error_code = "EXTERNAL_OUTCOME_UNCERTAIN"
                        att.error_message = uncertain_msg
                        att.completed_at = datetime.datetime.utcnow()

                self.db.commit()
                recovered_count += 1
                actions_breakdown["MARKED_RECONCILIATION_REQUIRED"] += 1
                details.append({"publication_id": str(pub.id), "action": "MARKED_RECONCILIATION_REQUIRED", "status": "RECONCILIATION_REQUIRED"})
                continue

            # 4. Check if attempt had already recorded a failure
            if pub.attempts and all(att.status == "FAILED" for att in pub.attempts):
                latest_att = sorted(pub.attempts, key=lambda a: a.started_at or datetime.datetime.min, reverse=True)[0]
                pub.status = "FAILED"
                pub.error_code = latest_att.error_code or "WORKER_CRASHED"
                pub.error_message = latest_att.error_message or "Publication attempt failed before worker crash."
                pub.updated_at = datetime.datetime.utcnow()
                self.db.commit()
                recovered_count += 1
                actions_breakdown["MARKED_FAILED"] += 1
                details.append({"publication_id": str(pub.id), "action": "MARKED_FAILED", "status": "FAILED"})
                continue

            # 5. Safe to retry: No attempt was ever dispatched, approval is valid, provider was never touched
            pub.status = "QUEUED"
            pub.error_code = None
            pub.error_message = None
            pub.updated_at = datetime.datetime.utcnow()
            self.db.commit()

            from app.publishing.tasks import execute_publishing_task
            try:
                execute_publishing_task.delay(str(pub.id))
            except Exception as e:
                pub.status = "FAILED"
                pub.error_code = "DISPATCH_FAILED"
                pub.error_message = "Failed to re-dispatch publishing task to worker queue."
                self.db.commit()

            recovered_count += 1
            actions_breakdown["REQUEUED_FOR_RETRY"] += 1
            details.append({"publication_id": str(pub.id), "action": "REQUEUED_FOR_RETRY", "status": pub.status})

        return {
            "claimed_count": claimed_count,
            "recovered_count": recovered_count,
            "actions": actions_breakdown,
            "details": details
        }

    def reconcile_publication(
        self,
        publication_id: uuid.UUID,
        resolution: str,
        external_post_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Publication:
        """
        Reconciles a publication marked RECONCILIATION_REQUIRED.
        Resolution options:
        - 'PUBLISHED': Confirms external publication with external_post_id.
        - 'FAILED': Marks publication as permanently failed.
        - 'RETRY': Revalidates approval and re-queues task for safe re-execution.
        """
        pub = self.db.query(Publication).filter(Publication.id == publication_id).first()
        if not pub:
            raise HTTPException(status_code=404, detail="Publication not found")

        if pub.status != "RECONCILIATION_REQUIRED":
            raise HTTPException(
                status_code=400,
                detail=f"Publication status is '{pub.status}', expected 'RECONCILIATION_REQUIRED'"
            )

        resolution = resolution.upper()
        if resolution == "PUBLISHED":
            if not external_post_id:
                raise HTTPException(status_code=400, detail="external_post_id is required when resolution is PUBLISHED")
            pub.status = "PUBLISHED"
            pub.external_post_id = external_post_id
            pub.published_at = datetime.datetime.utcnow()
            pub.error_code = None
            pub.error_message = notes
            pub.updated_at = datetime.datetime.utcnow()

            for att in pub.attempts:
                if att.status in ("UNCERTAIN", "STARTED", "RECOVERING"):
                    att.status = "SUCCESS"
                    att.response_metadata = {"reconciled_as": "PUBLISHED", "external_id": external_post_id, "notes": notes}
                    att.completed_at = datetime.datetime.utcnow()

            self.db.commit()
            return pub

        elif resolution == "FAILED":
            pub.status = "FAILED"
            pub.error_code = "RECONCILED_FAILED"
            pub.error_message = notes or "Publication manually reconciled as failed."
            pub.updated_at = datetime.datetime.utcnow()

            for att in pub.attempts:
                if att.status in ("UNCERTAIN", "STARTED", "RECOVERING"):
                    att.status = "FAILED"
                    att.error_code = "RECONCILED_FAILED"
                    att.error_message = pub.error_message
                    att.completed_at = datetime.datetime.utcnow()

            self.db.commit()
            return pub

        elif resolution == "RETRY":
            from app.models.all_models import ContentApproval
            approval = self.db.query(ContentApproval).filter(
                ContentApproval.content_draft_id == pub.content_draft_id,
                ContentApproval.workspace_id == pub.workspace_id,
                ContentApproval.brand_id == pub.brand_id
            ).order_by(ContentApproval.created_at.desc()).first()

            if not approval or approval.status != "APPROVED":
                pub.status = "BLOCKED"
                pub.error_code = "APPROVAL_REQUIRED"
                pub.error_message = "Cannot retry publication: Content approval is missing, rejected, or revoked."
                pub.updated_at = datetime.datetime.utcnow()
                self.db.commit()
                raise HTTPException(status_code=409, detail=pub.error_message)

            pub.status = "QUEUED"
            pub.error_code = None
            pub.error_message = None
            pub.updated_at = datetime.datetime.utcnow()
            self.db.commit()

            from app.publishing.tasks import execute_publishing_task
            try:
                execute_publishing_task.delay(str(pub.id))
            except Exception as e:
                pub.status = "FAILED"
                pub.error_code = "DISPATCH_FAILED"
                pub.error_message = f"Failed to enqueue publishing task: {str(e)}"
                self.db.commit()
                raise HTTPException(status_code=500, detail=pub.error_message)

            return pub
        else:
            raise HTTPException(status_code=400, detail=f"Invalid resolution '{resolution}'. Must be PUBLISHED, FAILED, or RETRY")
