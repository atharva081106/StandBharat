import logging
import uuid
from typing import Dict, Any, List, Optional
from app.integrations.provider import IntegrationProvider

logger = logging.getLogger(__name__)

class GSCProvider(IntegrationProvider):
    provider_id = "gsc"
    name = "Google Search Console"
    category = "ANALYTICS"
    capabilities = ["read", "metrics", "sync"]
    auth_type = "oauth2"
    required_scopes = [
        "https://www.googleapis.com/auth/webmasters.readonly"
    ]

    def connect(self, workspace_id: str, credentials: Dict[str, Any]) -> bool:
        return True

    def validate(self, workspace_id: str) -> bool:
        return True

    def refresh(self, workspace_id: str) -> bool:
        return True

    def sync(self, workspace_id: str, brand_id: Optional[str] = None, integration_id: Optional[str] = None) -> Dict[str, Any]:
        from app.db.session import SessionLocal
        from app.models.all_models import Integration, SearchMetrics
        from app.core.encryption import decrypt, encrypt
        import json
        import datetime
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        db = SessionLocal()
        try:
            # 1. Scoped Integration Resolution (avoids multi-brand collisions)
            if integration_id:
                integ = db.query(Integration).filter(
                    Integration.id == uuid.UUID(integration_id)
                ).first()
            elif brand_id:
                integ = db.query(Integration).filter(
                    Integration.brand_id == uuid.UUID(brand_id),
                    Integration.provider == self.provider_id
                ).first()
            else:
                integ = db.query(Integration).filter(
                    Integration.workspace_id == uuid.UUID(workspace_id), 
                    Integration.provider == self.provider_id
                ).first()

            if not integ or not integ.credentials_encrypted:
                return {"status": "failed", "error": "No credentials"}
                
            creds_json = json.loads(decrypt(integ.credentials_encrypted))
            original_token = creds_json.get("token")
            creds = Credentials(**creds_json)
            
            # 2. Safe Refresh-Token Validation & Persistence
            if creds.expired and creds.refresh_token:
                try:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                    if creds.token and creds.token != original_token:
                        creds_json["token"] = creds.token
                        integ.credentials_encrypted = encrypt(json.dumps(creds_json))
                        db.commit()
                except Exception as refresh_err:
                    logger.warning(f"GSC credential refresh warning: {refresh_err}")

            service = build('searchconsole', 'v1', credentials=creds)
            
            # 3. Verified Site Auto-Discovery or Configured Site
            site_url = None
            if integ.config and integ.config.get("siteUrl"):
                site_url = integ.config.get("siteUrl")
            else:
                try:
                    sites = service.sites().list().execute()
                    site_list = sites.get("siteEntry", [])
                    if not site_list:
                        return {"status": "failed", "error": "No verified sites found in Search Console"}
                    site_url = site_list[0].get("siteUrl")
                    if not integ.config:
                        integ.config = {}
                    else:
                        integ.config = dict(integ.config)
                    integ.config["siteUrl"] = site_url
                    integ.config["verified_sites"] = [s.get("siteUrl") for s in site_list if s.get("siteUrl")]
                    db.commit()
                except Exception as site_err:
                    return {"status": "failed", "error": f"Failed to list Search Console sites: {str(site_err)}"}
                
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=30)
            
            request = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'dimensions': ['query', 'page', 'date'],
                'rowLimit': 5000
            }
            
            try:
                response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
            except HttpError as herr:
                if herr.resp.status in (429, 503):
                    return {"status": "rate_limited", "error": f"GSC API rate limit reached: {str(herr)}"}
                raise herr
            
            # Check if token refreshed during client execution and persist
            if creds.token and creds.token != original_token:
                creds_json["token"] = creds.token
                integ.credentials_encrypted = encrypt(json.dumps(creds_json))
                db.commit()

            rows = response.get('rows', [])
            records_processed = 0
            for row in rows:
                keys = row.get("keys", [])
                query = keys[0] if len(keys) > 0 else None
                page = keys[1] if len(keys) > 1 else None
                date_str = keys[2] if len(keys) > 2 else None
                
                if date_str:
                    date_val = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    metric = db.query(SearchMetrics).filter(
                        SearchMetrics.brand_id == integ.brand_id,
                        SearchMetrics.date == date_val,
                        SearchMetrics.query == query,
                        SearchMetrics.page == page
                    ).first()
                    
                    if not metric:
                        metric = SearchMetrics(
                            workspace_id=integ.workspace_id,
                            brand_id=integ.brand_id,
                            date=date_val,
                            query=query,
                            page=page
                        )
                        db.add(metric)
                    
                    metric.clicks = row.get("clicks", 0)
                    metric.impressions = row.get("impressions", 0)
                    metric.ctr = row.get("ctr", 0.0)
                    metric.position = row.get("position", 0.0)
                    
                    records_processed += 1
                    
            db.commit()
            return {"status": "success", "records_processed": records_processed}
        except Exception as e:
            logger.error(f"GSCProvider sync error: {str(e)}", exc_info=True)
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()

    def publish(self, workspace_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("GSC does not support publishing")

    def get_metrics(self, workspace_id: str, entity_id: str = None, brand_id: str = None) -> Dict[str, Any]:
        from app.db.session import SessionLocal
        from app.models.all_models import SearchMetrics, Integration
        from sqlalchemy import func
        db = SessionLocal()
        try:
            query = db.query(Integration).filter(
                Integration.provider == self.provider_id
            )
            if brand_id:
                query = query.filter(Integration.brand_id == uuid.UUID(brand_id))
            else:
                query = query.filter(Integration.workspace_id == uuid.UUID(workspace_id))
            integ = query.first()
            if not integ:
                return {}
            result = db.query(
                func.sum(SearchMetrics.clicks).label("clicks"),
                func.sum(SearchMetrics.impressions).label("impressions"),
                func.avg(SearchMetrics.position).label("position")
            ).filter(SearchMetrics.brand_id == integ.brand_id).first()
            
            return {
                "clicks": result.clicks or 0,
                "impressions": result.impressions or 0,
                "position": result.position or 0.0
            }
        finally:
            db.close()
