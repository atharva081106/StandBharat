from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.deps import get_current_brand, get_current_user
from app.models.all_models import Brand, User, AgentTask, AgentRun
from app.db.session import SessionLocal
from pydantic import BaseModel
from app.agents.registry import agent_registry
from app.worker import execute_generic_agent
import uuid

router = APIRouter()

class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    capabilities: List[str]

@router.get("/", response_model=List[AgentResponse])
def list_agents(current_user: User = Depends(get_current_user)):
    agents = agent_registry.list_agents()
    return [{"id": a.agent_id, "name": a.name, "description": a.description, "capabilities": a.capabilities} for a in agents]

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    try:
        a = agent_registry.get_agent(agent_id)
        return {"id": a.agent_id, "name": a.name, "description": a.description, "capabilities": a.capabilities}
    except Exception:
        raise HTTPException(status_code=404, detail="Agent not found")

class RunRequest(BaseModel):
    input_data: dict

@router.post("/{agent_id}/run")
def run_agent(
    agent_id: str,
    req: RunRequest,
    brand: Brand = Depends(get_current_brand),
    current_user: User = Depends(get_current_user)
):
    try:
        agent = agent_registry.get_agent(agent_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    db = SessionLocal()
    try:
        task = AgentTask(
            workspace_id=brand.workspace_id,
            brand_id=brand.id,
            agent_type=agent.agent_id,
            task_type="manual_run",
            input_data=req.input_data,
            created_by=current_user.id
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        run = AgentRun(
            workspace_id=brand.workspace_id,
            brand_id=brand.id,
            agent_id=agent.agent_id,
            input_context=req.input_data
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        
        execute_generic_agent.delay(str(run.id))
        
        return {"task_id": str(task.id), "run_id": str(run.id)}
    finally:
        db.close()
