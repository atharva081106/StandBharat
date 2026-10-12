import logging
import uuid
from typing import Dict, Any, List, Optional
from app.integrations.provider import IntegrationProvider

logger = logging.getLogger(__name__)

class GA4Provider(IntegrationProvider):
    provider_id = "ga4"
    name = "Google Analytics 4"
    category = "ANALYTICS"
    capabilities = ["read", "metrics", "sync"]
    auth_type = "oauth2"
    required_scopes = [
        "https://www.googleapis.com/auth/analytics.readonly"
    ]

    def connect(self, workspace_id: str, credentials: Dict[str, Any]) -> bool:
        return True

    def validate(self, workspace_id: str) -> bool:
        return True

    def refresh(self, workspace_id: str) -> bool:
        return True

    def sync(self, workspace_id: str, brand_id: Optional[str] = None, integration_id: Optional[str] = None) -> Dict[str, Any]:
        from app.db.session import SessionLocal
        from app.models.all_models import Integration, TrafficMetrics
        from app.core.encryption import decrypt, encrypt
        import json
        import datetime
        from google.oauth2.credentials import Credentials
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
        from google.api_core.exceptions import ResourceExhausted
        
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
                    logger.warning(f"GA4 credential refresh warning: {refresh_err}")

            # 3. GA4 Property Resolution: Configured or Auto-Discovered via Admin API
            property_id = None
            if integ.config and integ.config.get("property_id"):
                property_id = str(integ.config.get("property_id")).strip()
                if property_id.startswith("properties/"):
                    property_id = property_id.split("/")[-1]
            else:
                try:
                    from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
                    admin_client = AnalyticsAdminServiceClient(credentials=creds)
                    summaries = admin_client.list_account_summaries()
                    discovered = []
                    for account in summaries:
                        for prop_sum in account.property_summaries:
                            p_id = prop_sum.property.split("/")[-1] if "/" in prop_sum.property else prop_sum.property
                            discovered.append({
                                "property_id": p_id,
                                "display_name": prop_sum.display_name
                            })
                    
                    if not discovered:
                        return {"status": "failed", "error": "No accessible GA4 properties found for this Google account"}
                    
                    chosen = discovered[0]
                    property_id = chosen["property_id"]
                    if not integ.config:
                        integ.config = {}
                    else:
                        integ.config = dict(integ.config)
                    integ.config["property_id"] = property_id
                    integ.config["property_name"] = chosen.get("display_name", "")
                    integ.config["discovered_properties"] = discovered
                    db.commit()
                except Exception as disc_err:
                    return {"status": "failed", "error": f"No GA4 property configured and discovery failed: {str(disc_err)}"}

            # 4. Query GA4 Data API
            client = BetaAnalyticsDataClient(credentials=creds)
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=30)
            
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[
                    Dimension(name="date"),
                    Dimension(name="sessionSource"),
                    Dimension(name="sessionMedium"),
                    Dimension(name="landingPage")
                ],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="activeUsers"),
                    Metric(name="screenPageViews"),
                    Metric(name="engagementRate"),
                    Metric(name="conversions")
                ],
                date_ranges=[DateRange(start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))],
            )
            
            try:
                response = client.run_report(request)
            except ResourceExhausted as rex:
                return {"status": "rate_limited", "error": f"GA4 API quota exhausted: {str(rex)}"}
            
            # Check if token refreshed during client execution and persist
            if creds.token and creds.token != original_token:
                creds_json["token"] = creds.token
                integ.credentials_encrypted = encrypt(json.dumps(creds_json))
                db.commit()

            # 5. Upsert Records into TrafficMetrics with strict brand and workspace isolation
            records_processed = 0
            for row in response.rows:
                date_str = row.dimension_values[0].value
                source = row.dimension_values[1].value
                medium = row.dimension_values[2].value
                landing_page = row.dimension_values[3].value
                
                sessions = int(row.metric_values[0].value)
                active_users = int(row.metric_values[1].value)
                pageviews = int(row.metric_values[2].value)
                engagement_rate = float(row.metric_values[3].value)
                conversions = int(float(row.metric_values[4].value))
                
                date_val = datetime.datetime.strptime(date_str, "%Y%m%d")
                
                metric = db.query(TrafficMetrics).filter(
                    TrafficMetrics.brand_id == integ.brand_id,
                    TrafficMetrics.date == date_val,
                    TrafficMetrics.source == source,
                    TrafficMetrics.medium == medium,
                    TrafficMetrics.landing_page == landing_page
                ).first()
                
                if not metric:
                    metric = TrafficMetrics(
                        workspace_id=integ.workspace_id,
                        brand_id=integ.brand_id,
                        date=date_val,
                        source=source,
                        medium=medium,
                        landing_page=landing_page
                    )
                    db.add(metric)
                
                metric.sessions = sessions
                metric.active_users = active_users
                metric.pageviews = pageviews
                metric.engagement_rate = engagement_rate
                metric.conversions = conversions
                
                records_processed += 1
                
            db.commit()
            return {"status": "success", "records_processed": records_processed}
        except Exception as e:
            logger.error(f"GA4Provider sync error: {str(e)}", exc_info=True)
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()

    def publish(self, workspace_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("GA4 does not support publishing")

    def get_metrics(self, workspace_id: str, entity_id: str = None, brand_id: str = None) -> Dict[str, Any]:
        from app.db.session import SessionLocal
        from app.models.all_models import TrafficMetrics, Integration
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
                func.sum(TrafficMetrics.sessions).label("sessions"),
                func.sum(TrafficMetrics.pageviews).label("pageviews"),
                func.avg(TrafficMetrics.engagement_rate).label("engagement_rate")
            ).filter(TrafficMetrics.brand_id == integ.brand_id).first()
            
            return {
                "sessions": result.sessions or 0,
                "pageviews": result.pageviews or 0,
                "engagement_rate": result.engagement_rate or 0.0
            }
        finally:
            db.close()
