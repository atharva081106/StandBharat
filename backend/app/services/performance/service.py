from typing import Dict, Any, Optional
import uuid
from sqlalchemy.orm import Session
from app.models.performance import PerformanceSnapshot
from app.publishing.models import Publication, PublisherConnection
from .provider import PerformanceProvider
from .linkedin_provider import LinkedInPerformanceProvider

class PerformanceService:
    def __init__(self, db: Session):
        self.db = db
        self.providers: Dict[str, PerformanceProvider] = {
            "linkedin": LinkedInPerformanceProvider()
        }
        
    def get_provider(self, channel: str) -> Optional[PerformanceProvider]:
        return self.providers.get(channel)

    async def sync_publication_performance(self, publication_id: str) -> Optional[PerformanceSnapshot]:
        publication = self.db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            return None
            
        if publication.status != "PUBLISHED" or not publication.external_post_id:
            return None

        connection = self.db.query(PublisherConnection).filter(
            PublisherConnection.workspace_id == publication.workspace_id,
            PublisherConnection.brand_id == publication.brand_id,
            PublisherConnection.platform == publication.platform
        ).first()

        provider = self.get_provider(publication.platform)
        if not provider:
            return None

        metrics = await provider.get_publication_metrics(publication.external_post_id, connection)
        
        source_status = metrics.pop("source_status", "ERROR")
        
        snapshot = PerformanceSnapshot(
            workspace_id=publication.workspace_id,
            brand_id=publication.brand_id,
            publication_id=publication.id,
            channel=publication.platform,
            external_post_id=publication.external_post_id,
            source=f"{publication.platform}_api",
            source_status=source_status,
            raw_payload=metrics.pop("raw_payload", None)
        )
        
        if source_status == "SUCCESS":
            for key, value in metrics.items():
                if hasattr(snapshot, key):
                    setattr(snapshot, key, value)
                    
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        
        return snapshot
