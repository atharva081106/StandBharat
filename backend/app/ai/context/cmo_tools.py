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
        
    return json.dumps({"error": f"Tool {tool_name} not found or implemented."})
