from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.publishing.models import Publication, PublicationAttempt, PublisherConnection
from app.publishing.registry import PublisherRegistry
from app.publishing.exceptions import PublishingError, NotConfiguredError, AuthenticationError
from app.publishing.service import PublishingService
from app.models.all_models import ContentDraft
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
            # Load draft
            draft = db.query(ContentDraft).filter(ContentDraft.id == publication.content_draft_id).first()
            if not draft:
                raise PublishingError("Content draft not found", "INVALID_CONTENT")
                
            # Content prep
            content_dict = {
                "content_type": draft.content_type,
                "title": draft.title,
                "body": draft.body
            }
            
            # Load connection
            connection = service.get_connection(publication.workspace_id, publication.brand_id, publication.platform)
            if not connection or connection.status != "CONNECTED":
                raise NotConfiguredError(f"Connection for {publication.platform} is missing or invalid.")
                
            credentials = service.get_credentials(connection)
            
            # Execute
            connector = PublisherRegistry.get_connector(publication.platform)
            result = connector.publish(credentials, content_dict)
            
            # Success
            publication.status = "PUBLISHED"
            publication.external_post_id = result.get("external_id")
            publication.published_at = datetime.datetime.utcnow()
            
            attempt.status = "SUCCESS"
            attempt.response_metadata = result
            attempt.completed_at = datetime.datetime.utcnow()
            
            db.commit()
            
        except (NotConfiguredError, AuthenticationError) as e:
            # Permanent failure - don't retry auth issues automatically
            publication.status = "FAILED"
            publication.error_code = e.code
            publication.error_message = e.message
            
            attempt.status = "FAILED"
            attempt.error_code = e.code
            attempt.error_message = e.message
            attempt.completed_at = datetime.datetime.utcnow()
            
            db.commit()
            
        except PublishingError as e:
            # Depending on error, could retry. We will fail for INVALID_CONTENT etc.
            if e.code in ("RATE_LIMITED", "NETWORK_ERROR", "PROVIDER_ERROR"):
                attempt.status = "FAILED"
                attempt.error_code = e.code
                attempt.error_message = e.message
                attempt.completed_at = datetime.datetime.utcnow()
                db.commit()
                
                # Retry transient
                raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
            else:
                publication.status = "FAILED"
                publication.error_code = e.code
                publication.error_message = e.message
                
                attempt.status = "FAILED"
                attempt.error_code = e.code
                attempt.error_message = e.message
                attempt.completed_at = datetime.datetime.utcnow()
                db.commit()
                
        except Exception as e:
            # Unknown error, log and fail
            publication.status = "FAILED"
            publication.error_code = "UNKNOWN_ERROR"
            publication.error_message = str(e)
            
            attempt.status = "FAILED"
            attempt.error_code = "UNKNOWN_ERROR"
            attempt.error_message = str(e)
            attempt.completed_at = datetime.datetime.utcnow()
            db.commit()
            
    finally:
        db.close()
