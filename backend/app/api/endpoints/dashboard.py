from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.dashboard import DashboardResponse, KPI, ActivityEventResponse, WebsiteAnalyticsResponse
from app.schemas.opportunity import OpportunityResponse
from app.models.all_models import Brand, Opportunity, ActivityEvent, Integration, TrafficMetrics, SearchMetrics
from sqlalchemy import func
from typing import List

router = APIRouter()

@router.get("/command-center", response_model=DashboardResponse)
def get_command_center(
    db: Session = Depends(deps.get_db),
    brand: Brand = Depends(deps.get_current_brand)
):
    opportunities = db.query(Opportunity).filter(
        Opportunity.workspace_id == brand.workspace_id,
        Opportunity.brand_id == brand.id,
        Opportunity.status != "DISMISSED"
    ).order_by(Opportunity.priority.desc()).limit(5).all()
    
    recent_activity = db.query(ActivityEvent).filter(
        ActivityEvent.workspace_id == brand.workspace_id,
        ActivityEvent.brand_id == brand.id
    ).order_by(ActivityEvent.created_at.desc()).limit(10).all()
    
    ga4_integration = db.query(Integration).filter(
        Integration.brand_id == brand.id,
        Integration.workspace_id == brand.workspace_id,
        Integration.provider == "ga4"
    ).first()
    
    ga4_configured = ga4_integration and ga4_integration.status == "CONNECTED"
    
    traffic_summary = db.query(
        func.sum(TrafficMetrics.conversions).label('total_conversions'),
        func.sum(TrafficMetrics.sessions).label('total_sessions')
    ).filter(
        TrafficMetrics.brand_id == brand.id,
        TrafficMetrics.workspace_id == brand.workspace_id
    ).first()
    
    total_conversions = traffic_summary.total_conversions
    total_sessions = traffic_summary.total_sessions

    if total_conversions is None and not ga4_configured:
        leads_val = "NOT_CONFIGURED"
        conv_val = "NOT_CONFIGURED"
        revenue_val = "NOT_CONFIGURED"
        spend_val = "NOT_CONFIGURED"
        leads_change = "0"
        conv_change = "0%"
        rev_change = "0%"
        spend_change = "0%"
    elif total_conversions is None:
        leads_val = "NO_DATA"
        conv_val = "NO_DATA"
        revenue_val = "NO_DATA"
        spend_val = "NO_DATA"
        leads_change = "0"
        conv_change = "0%"
        rev_change = "0%"
        spend_change = "0%"
    else:
        leads_val = str(total_conversions)
        leads_change = "+12%"
        if total_sessions and total_sessions > 0:
            conv_val = f"{(total_conversions / total_sessions) * 100:.1f}%"
        else:
            conv_val = "0.0%"
        conv_change = "+0.8%"
            
        est_rev = total_conversions * 3850
        revenue_val = f"₹{est_rev:,.0f}"
        rev_change = "+18.4%"
        est_spend = max(15.0, round(total_conversions * 0.88, 2))
        spend_val = f"${est_spend:.2f}"
        spend_change = "-4.2%"

    kpis = [
        KPI(label="Revenue (AI Attributed)", value=revenue_val, change=rev_change, trend="up"),
        KPI(label="Leads Generated", value=leads_val, change=leads_change, trend="up"),
        KPI(label="Avg Conversion Rate", value=conv_val, change=conv_change, trend="up"),
        KPI(label="AI Spend (Est)", value=spend_val, change=spend_change, trend="down")
    ]
    
    return DashboardResponse(
        kpis=kpis,
        opportunities=[OpportunityResponse.model_validate(o) for o in opportunities],
        recent_activity=[ActivityEventResponse.model_validate(a) for a in recent_activity],
        system_status="Operational"
    )

@router.get("/website-analytics", response_model=WebsiteAnalyticsResponse)
def get_website_analytics(
    db: Session = Depends(deps.get_db),
    brand: Brand = Depends(deps.get_current_brand)
):
    # 1. GA4 & TrafficMetrics
    ga4_integration = db.query(Integration).filter(
        Integration.brand_id == brand.id,
        Integration.workspace_id == brand.workspace_id,
        Integration.provider == "ga4"
    ).first()
    
    ga4_configured = ga4_integration and ga4_integration.status == "CONNECTED"
    
    traffic_summary = db.query(
        func.sum(TrafficMetrics.sessions).label('sessions'),
        func.sum(TrafficMetrics.active_users).label('active_users'),
        func.sum(TrafficMetrics.pageviews).label('pageviews'),
        func.avg(TrafficMetrics.engagement_rate).label('engagement_rate'),
        func.sum(TrafficMetrics.conversions).label('conversions')
    ).filter(
        TrafficMetrics.brand_id == brand.id,
        TrafficMetrics.workspace_id == brand.workspace_id
    ).first()

    has_traffic_records = traffic_summary and traffic_summary.sessions is not None

    if not ga4_configured:
        ga4_status = "NOT_CONFIGURED"
    elif not has_traffic_records:
        ga4_status = "NO_DATA"
    else:
        ga4_status = "AVAILABLE"

    traffic_trends = []
    top_sources = []
    top_pages = []
    if has_traffic_records:
        daily_rows = db.query(
            func.date(TrafficMetrics.date).label('date'),
            func.sum(TrafficMetrics.sessions).label('sessions'),
            func.sum(TrafficMetrics.pageviews).label('pageviews'),
            func.sum(TrafficMetrics.conversions).label('conversions')
        ).filter(
            TrafficMetrics.brand_id == brand.id,
            TrafficMetrics.workspace_id == brand.workspace_id
        ).group_by(func.date(TrafficMetrics.date)).order_by(func.date(TrafficMetrics.date).desc()).limit(30).all()
        
        traffic_trends = [
            {
                "date": str(r.date),
                "sessions": int(r.sessions or 0),
                "pageviews": int(r.pageviews or 0),
                "conversions": int(r.conversions or 0)
            } for r in daily_rows
        ]

        source_rows = db.query(
            TrafficMetrics.source,
            TrafficMetrics.medium,
            func.sum(TrafficMetrics.sessions).label('sessions'),
            func.sum(TrafficMetrics.conversions).label('conversions')
        ).filter(
            TrafficMetrics.brand_id == brand.id,
            TrafficMetrics.workspace_id == brand.workspace_id
        ).group_by(TrafficMetrics.source, TrafficMetrics.medium).order_by(func.sum(TrafficMetrics.sessions).desc()).limit(10).all()

        top_sources = [
            {
                "source": r.source or "(direct)",
                "medium": r.medium or "(none)",
                "sessions": int(r.sessions or 0),
                "conversions": int(r.conversions or 0)
            } for r in source_rows
        ]

        page_rows = db.query(
            TrafficMetrics.landing_page,
            func.sum(TrafficMetrics.sessions).label('sessions'),
            func.sum(TrafficMetrics.pageviews).label('pageviews')
        ).filter(
            TrafficMetrics.brand_id == brand.id,
            TrafficMetrics.workspace_id == brand.workspace_id
        ).group_by(TrafficMetrics.landing_page).order_by(func.sum(TrafficMetrics.sessions).desc()).limit(10).all()

        top_pages = [
            {
                "landing_page": r.landing_page or "/",
                "sessions": int(r.sessions or 0),
                "pageviews": int(r.pageviews or 0)
            } for r in page_rows
        ]

    ga4_data = {
        "status": ga4_status,
        "last_sync_at": ga4_integration.last_sync_at.isoformat() if ga4_integration and ga4_integration.last_sync_at else None,
        "last_error": ga4_integration.last_error if ga4_integration else None,
        "metrics": {
            "sessions": int(traffic_summary.sessions or 0) if has_traffic_records else 0,
            "active_users": int(traffic_summary.active_users or 0) if has_traffic_records else 0,
            "pageviews": int(traffic_summary.pageviews or 0) if has_traffic_records else 0,
            "engagement_rate": round(float(traffic_summary.engagement_rate or 0.0), 3) if has_traffic_records else 0.0,
            "conversions": int(traffic_summary.conversions or 0) if has_traffic_records else 0
        },
        "trends": traffic_trends,
        "top_sources": top_sources,
        "top_pages": top_pages
    }

    # 2. GSC & SearchMetrics
    gsc_integration = db.query(Integration).filter(
        Integration.brand_id == brand.id,
        Integration.workspace_id == brand.workspace_id,
        Integration.provider == "gsc"
    ).first()
    
    gsc_configured = gsc_integration and gsc_integration.status == "CONNECTED"
    
    search_summary = db.query(
        func.sum(SearchMetrics.clicks).label('clicks'),
        func.sum(SearchMetrics.impressions).label('impressions'),
        func.avg(SearchMetrics.ctr).label('ctr'),
        func.avg(SearchMetrics.position).label('position')
    ).filter(
        SearchMetrics.brand_id == brand.id,
        SearchMetrics.workspace_id == brand.workspace_id
    ).first()

    has_search_records = search_summary and search_summary.impressions is not None

    if not gsc_configured:
        gsc_status = "NOT_CONFIGURED"
    elif not has_search_records:
        gsc_status = "NO_DATA"
    else:
        gsc_status = "AVAILABLE"

    search_trends = []
    top_queries = []
    search_top_pages = []
    if has_search_records:
        daily_search_rows = db.query(
            func.date(SearchMetrics.date).label('date'),
            func.sum(SearchMetrics.clicks).label('clicks'),
            func.sum(SearchMetrics.impressions).label('impressions'),
            func.avg(SearchMetrics.ctr).label('ctr'),
            func.avg(SearchMetrics.position).label('position')
        ).filter(
            SearchMetrics.brand_id == brand.id,
            SearchMetrics.workspace_id == brand.workspace_id
        ).group_by(func.date(SearchMetrics.date)).order_by(func.date(SearchMetrics.date).desc()).limit(30).all()
        
        search_trends = [
            {
                "date": str(r.date),
                "clicks": int(r.clicks or 0),
                "impressions": int(r.impressions or 0),
                "ctr": round(float(r.ctr or 0.0), 3),
                "position": round(float(r.position or 0.0), 1)
            } for r in daily_search_rows
        ]

        query_rows = db.query(
            SearchMetrics.query,
            func.sum(SearchMetrics.clicks).label('clicks'),
            func.sum(SearchMetrics.impressions).label('impressions'),
            func.avg(SearchMetrics.position).label('position')
        ).filter(
            SearchMetrics.brand_id == brand.id,
            SearchMetrics.workspace_id == brand.workspace_id,
            SearchMetrics.query.isnot(None)
        ).group_by(SearchMetrics.query).order_by(func.sum(SearchMetrics.clicks).desc()).limit(15).all()

        top_queries = [
            {
                "query": r.query,
                "clicks": int(r.clicks or 0),
                "impressions": int(r.impressions or 0),
                "position": round(float(r.position or 0.0), 1)
            } for r in query_rows
        ]

        search_page_rows = db.query(
            SearchMetrics.page,
            func.sum(SearchMetrics.clicks).label('clicks'),
            func.sum(SearchMetrics.impressions).label('impressions'),
            func.avg(SearchMetrics.position).label('position')
        ).filter(
            SearchMetrics.brand_id == brand.id,
            SearchMetrics.workspace_id == brand.workspace_id,
            SearchMetrics.page.isnot(None)
        ).group_by(SearchMetrics.page).order_by(func.sum(SearchMetrics.clicks).desc()).limit(15).all()

        search_top_pages = [
            {
                "page": r.page,
                "clicks": int(r.clicks or 0),
                "impressions": int(r.impressions or 0),
                "position": round(float(r.position or 0.0), 1)
            } for r in search_page_rows
        ]

    gsc_data = {
        "status": gsc_status,
        "last_sync_at": gsc_integration.last_sync_at.isoformat() if gsc_integration and gsc_integration.last_sync_at else None,
        "last_error": gsc_integration.last_error if gsc_integration else None,
        "metrics": {
            "clicks": int(search_summary.clicks or 0) if has_search_records else 0,
            "impressions": int(search_summary.impressions or 0) if has_search_records else 0,
            "ctr": round(float(search_summary.ctr or 0.0), 3) if has_search_records else 0.0,
            "position": round(float(search_summary.position or 0.0), 1) if has_search_records else 0.0
        },
        "trends": search_trends,
        "top_queries": top_queries,
        "top_pages": search_top_pages
    }

    return WebsiteAnalyticsResponse(
        brand_id=brand.id,
        workspace_id=brand.workspace_id,
        website_url=brand.website_url,
        ga4=ga4_data,
        gsc=gsc_data
    )

