from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.publishing.models import Publication, PublicationAttempt, PublisherConnection
from app.publishing.registry import PublisherRegistry
from app.publishing.exceptions import PublishingError, NotConfiguredError, AuthenticationError
from app.publishing.service import PublishingService
from app.models.all_models import ContentDraft
from app.core.security import sanitize_error_message
import datetime

@celery_app.task(bind=True, max_retries=3)
def execute_publishing_task(self, publication_id_str: str):
    db = SessionLocal()
    try:
        service = PublishingService(db)
        
        publication = db.query(Publication).filter(Publication.id == publication_id_str).first()
        if not publication:
            return
            
        if publication.status not in ("QUEUED", "FAILED"):
            return # Already processed or cancelled
            
        publication.status = "PUBLISHING"
        
        attempt_number = len(publication.attempts) + 1
        attempt = PublicationAttempt(
            publication_id=publication.id,
            attempt_number=str(attempt_number),
            status="STARTED"
        )
        db.add(attempt)
        db.commit()
        
        try:
            # 1. Load draft with workspace and brand isolation
            draft = db.query(ContentDraft).filter(
                ContentDraft.id == publication.content_draft_id,
                ContentDraft.workspace_id == publication.workspace_id,
                ContentDraft.brand_id == publication.brand_id
            ).first()
            if not draft:
                raise PublishingError("Content draft not found or workspace/brand mismatch", "INVALID_CONTENT")

            # 2. Revalidate ContentApproval status immediately before invoking any external provider
            from app.models.all_models import ContentApproval
            approval = db.query(ContentApproval).filter(
                ContentApproval.content_draft_id == draft.id,
                ContentApproval.workspace_id == publication.workspace_id,
                ContentApproval.brand_id == publication.brand_id
            ).order_by(ContentApproval.created_at.desc()).first()

            if not approval or approval.status != "APPROVED":
                reason = "Approval is missing or revoked" if not approval else f"Content approval status is '{approval.status}', expected 'APPROVED'"
                error_msg = f"Publication blocked: {reason}. Explicit approval is required before publishing."
                
                publication.status = "BLOCKED"
                publication.error_code = "APPROVAL_REQUIRED"
                publication.error_message = sanitize_error_message(error_msg)
                
                attempt.status = "BLOCKED"
                attempt.error_code = "APPROVAL_REQUIRED"
                attempt.error_message = sanitize_error_message(error_msg)
                attempt.completed_at = datetime.datetime.utcnow()
                
                db.commit()
                return
                
            # 3. Content prep
            content_dict = {
                "content_type": draft.content_type,
                "title": draft.title,
                "body": draft.body
            }
            
            # 4. Load connection
            connection = service.get_connection(publication.workspace_id, publication.brand_id, publication.platform)
            if not connection or connection.status != "CONNECTED":
                raise NotConfiguredError(f"Connection for {publication.platform} is missing or invalid.")

            if isinstance(connection, PublisherConnection):
                credentials = service.get_credentials(connection)
                connector = PublisherRegistry.get_connector(publication.platform)
                result = connector.publish(credentials, content_dict)
            else:
                from app.integrations.registry import integration_registry
                provider = integration_registry.get_provider(publication.platform)
                content_dict["brand_id"] = str(publication.brand_id)
                result = provider.publish(str(publication.workspace_id), content_dict)
            
            # Clean sensitive fields from response metadata
            clean_result = (
                {k: v for k, v in result.items() if k not in ("access_token", "token", "client_secret", "credentials", "encrypted_credentials")}
                if isinstance(result, dict) else result
            )

            # Success
            publication.status = "PUBLISHED"
            publication.external_post_id = result.get("external_id") if isinstance(result, dict) else None
            publication.published_at = datetime.datetime.utcnow()
            
            attempt.status = "SUCCESS"
            attempt.response_metadata = clean_result
            attempt.completed_at = datetime.datetime.utcnow()
            
            db.commit()
            
        except (NotConfiguredError, AuthenticationError) as e:
            # Permanent failure - don't retry auth issues automatically
            sanitized_msg = sanitize_error_message(e.message)
            publication.status = "FAILED"
            publication.error_code = e.code
            publication.error_message = sanitized_msg
            
            attempt.status = "FAILED"
            attempt.error_code = e.code
            attempt.error_message = sanitized_msg
            attempt.completed_at = datetime.datetime.utcnow()
            
            db.commit()
            
        except PublishingError as e:
            sanitized_msg = sanitize_error_message(e.message)
            # Depending on error, could retry. We will fail for INVALID_CONTENT etc.
            if e.code in ("RATE_LIMITED", "NETWORK_ERROR", "PROVIDER_ERROR"):
                attempt.status = "FAILED"
                attempt.error_code = e.code
                attempt.error_message = sanitized_msg
                attempt.completed_at = datetime.datetime.utcnow()
                publication.status = "QUEUED"  # Reset status so Celery retry will process it
                db.commit()
                
                # Retry transient
                raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
            else:
                publication.status = "FAILED"
                publication.error_code = e.code
                publication.error_message = sanitized_msg
                
                attempt.status = "FAILED"
                attempt.error_code = e.code
                attempt.error_message = sanitized_msg
                attempt.completed_at = datetime.datetime.utcnow()
                db.commit()
                
        except Exception as e:
            # Unknown error, log and fail with sanitized message
            sanitized_msg = sanitize_error_message(str(e))
            publication.status = "FAILED"
            publication.error_code = "UNKNOWN_ERROR"
            publication.error_message = sanitized_msg
            
            attempt.status = "FAILED"
            attempt.error_code = "UNKNOWN_ERROR"
            attempt.error_message = sanitized_msg
            attempt.completed_at = datetime.datetime.utcnow()
            db.commit()
            
    finally:
        db.close()


@celery_app.task(name="recover_stale_publications")
def recover_stale_publications(timeout_minutes: int = None):
    db = SessionLocal()
    try:
        service = PublishingService(db)
        return service.recover_stale_publications(timeout_minutes=timeout_minutes)
    finally:
        db.close()

