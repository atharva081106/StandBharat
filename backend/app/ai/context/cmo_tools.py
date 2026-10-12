from typing import Dict, Any, List
from sqlalchemy.orm import Session
import uuid

CMO_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_brand_context",
            "description": "Fetch the core business overview, brand voice, and audience details.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_agent",
            "description": "Trigger an asynchronous specialized agent (e.g., SEO, Writer) for a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "The ID of the agent to run, e.g. seo_agent, content_writer"},
                    "input_data": {"type": "object", "description": "JSON payload required by the agent"}
                },
                "required": ["agent_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_opportunities",
            "description": "Fetch open marketing opportunities identified by growth or SEO agents.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_integrations",
            "description": "Inspect integration connection states, available properties, and last sync timestamp.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sync_integration",
            "description": "Request a permitted synchronization for a specific integration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "integration_id": {"type": "string", "description": "The provider ID, e.g. gsc, ga4"}
                },
                "required": ["integration_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_gsc_data",
            "description": "Retrieve actual persisted Google Search Console data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ga4_data",
            "description": "Retrieve actual persisted Google Analytics 4 data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

def execute_cmo_tool(db: Session, workspace_id: uuid.UUID, brand_id: uuid.UUID, user_id: uuid.UUID, tool_name: str, arguments: Dict[str, Any]) -> str:
    import json
    if tool_name == "get_brand_context":
        from app.services.brand_context import BrandContextService
        ctx = BrandContextService.get_unified_context(db, workspace_id, brand_id)
        return json.dumps(ctx, default=str)
    
    elif tool_name == "get_opportunities":
        from app.models.all_models import Opportunity
        ops = db.query(Opportunity).filter(Opportunity.brand_id == brand_id).limit(10).all()
        return json.dumps([{"id": str(o.id), "title": o.title, "impact": o.impact} for o in ops])
        
    elif tool_name == "run_agent":
        from app.models.all_models import AgentTask, AgentRun
        from app.worker import execute_agent_task
        
        agent_id = arguments.get("agent_id")
        input_data = arguments.get("input_data", {})
        
        task = AgentTask(
            workspace_id=workspace_id,
            brand_id=brand_id,
            agent_type=agent_id,
            input_data=input_data,
            status="QUEUED",
            created_by=user_id
        )
        db.add(task)
        
        run = AgentRun(
            workspace_id=workspace_id,
            brand_id=brand_id,
            agent_type=agent_id,
            status="QUEUED"
        )
        db.add(run)
        db.commit()
        
        execute_agent_task.delay(str(task.id), str(run.id))
        return json.dumps({"status": "QUEUED", "task_id": str(task.id), "run_id": str(run.id)})
        
    elif tool_name == "get_integrations":
        from app.models.all_models import Integration
        integs = db.query(Integration).filter(Integration.brand_id == brand_id).all()
        return json.dumps([{
            "provider": i.provider,
            "status": i.status,
            "last_sync_at": str(i.last_sync_at) if i.last_sync_at else None,
            "last_error": i.last_error
        } for i in integs])
        
    elif tool_name == "sync_integration":
        from app.models.all_models import Integration, IntegrationSyncRun
        provider_id = arguments.get("integration_id")
        integ = db.query(Integration).filter(Integration.brand_id == brand_id, Integration.provider == provider_id).first()
        if not integ:
            return json.dumps({"error": f"Integration {provider_id} not connected"})
        
        run = IntegrationSyncRun(
            integration_id=integ.id,
            workspace_id=workspace_id,
            brand_id=brand_id,
            provider_id=provider_id,
            status="QUEUED"
        )
        db.add(run)
        integ.status = "SYNCING"
        db.commit()
        from app.worker import sync_integration
        sync_integration.delay(str(run.id))
        return json.dumps({"status": "SYNC_QUEUED", "sync_run_id": str(run.id)})
        
    elif tool_name == "get_gsc_data":
        from app.models.all_models import SearchMetrics
        metrics = db.query(SearchMetrics).filter(SearchMetrics.brand_id == brand_id).order_by(SearchMetrics.date.desc()).limit(50).all()
        return json.dumps([{
            "date": str(m.date),
            "query": m.query,
            "page": m.page,
            "clicks": m.clicks,
            "impressions": m.impressions,
            "ctr": m.ctr,
            "position": m.position
        } for m in metrics])
        
    elif tool_name == "get_ga4_data":
        from app.models.all_models import TrafficMetrics
        metrics = db.query(TrafficMetrics).filter(TrafficMetrics.brand_id == brand_id).order_by(TrafficMetrics.date.desc()).limit(50).all()
        return json.dumps([{
            "date": str(m.date),
            "source": m.source,
            "medium": m.medium,
            "sessions": m.sessions,
            "active_users": m.active_users,
            "pageviews": m.pageviews,
            "engagement_rate": m.engagement_rate,
            "conversions": m.conversions
        } for m in metrics])
        
    return json.dumps({"error": f"Tool {tool_name} not found or implemented."})
