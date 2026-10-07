from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_brand, get_current_user
from app.models.all_models import Brand, User
from app.ai.gateway import ai_gateway
from app.ai.config import ai_config
from app.ai.exceptions import AINotConfiguredException
from app.ai.schemas import AIRequestMessage
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.ai.context.brand_context import brand_context_service
from app.ai.context.prompt_context import build_brand_prompt_context
from app.ai.context.agent_results import agent_result_service
from app.models.all_models import ContentProject, ContentDraft, ContentApproval
import json

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class AICmoResponse(BaseModel):
    status: str
    response: str = ""

@router.get("/status")
def get_ai_status(current_user: User = Depends(get_current_user)):
    try:
        provider = ai_gateway._get_provider()
        return {
            "configured": True,
            "provider": ai_config.DEFAULT_PROVIDER
        }
    except AINotConfiguredException:
        return {
            "configured": False,
            "status": "NOT_CONFIGURED"
        }

@router.post("/cmo/chat", response_model=AICmoResponse)
def ai_cmo_chat(
    req: ChatRequest,
    brand: Brand = Depends(get_current_brand),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        ai_gateway._get_provider() # ensure configured
    except AINotConfiguredException:
        return {"status": "AI_NOT_CONFIGURED", "response": ""}
        
    context_obj = brand_context_service.get_brand_context(db, brand.id)
    agent_results = agent_result_service.get_latest_agent_results(db, brand.id)
    
    if context_obj:
        brand_prompt = build_brand_prompt_context(context_obj)
        sys_prompt = f"You are an AI CMO for the brand {brand.name}.\n\nBrand Context:\n{brand_prompt}"
    else:
        sys_prompt = f"You are an AI CMO for the brand {brand.name}."
        
    if agent_results:
        sys_prompt += f"\n\nRecent Agent Findings:\n{json.dumps(agent_results, indent=2)}"
        
    # Fetch content workflow state
    projects = db.query(ContentProject).filter(ContentProject.brand_id == brand.id).order_by(ContentProject.created_at.desc()).limit(10).all()
    if projects:
        content_state = []
        for p in projects:
            drafts = db.query(ContentDraft).filter(ContentDraft.content_project_id == p.id).all()
            approvals = db.query(ContentApproval).filter(ContentApproval.content_project_id == p.id).all()
            content_state.append({
                "project_id": str(p.id),
                "title": p.title,
                "status": p.status,
                "type": p.content_type,
                "drafts": [{"id": str(d.id), "status": d.status} for d in drafts],
                "approvals": [{"id": str(a.id), "status": a.status} for a in approvals]
            })
        sys_prompt += f"\n\nContent Workflow State:\n{json.dumps(content_state, indent=2)}"
        
    # Fetch performance state
    from app.models.performance import PerformanceSnapshot
    performance_snapshots = db.query(PerformanceSnapshot).filter(
        PerformanceSnapshot.brand_id == brand.id,
        PerformanceSnapshot.source_status == "SUCCESS"
    ).order_by(PerformanceSnapshot.captured_at.desc()).limit(20).all()
    
    if performance_snapshots:
        perf_state = []
        for s in performance_snapshots:
            perf_state.append({
                "channel": s.channel,
                "captured_at": str(s.captured_at),
                "impressions": s.impressions,
                "engagements": s.engagements,
                "engagement_rate": s.engagement_rate
            })
        sys_prompt += f"\n\nRecent Publishing Performance:\n{json.dumps(perf_state, indent=2)}"
    else:
        sys_prompt += f"\n\nRecent Publishing Performance:\nI can't evaluate publishing performance yet because analytics access is not configured or no data is available."
        
    messages = [
        AIRequestMessage(role="system", content=sys_prompt),
        AIRequestMessage(role="user", content=req.message)
    ]
    
    try:
        res = ai_gateway.generate(messages=messages, max_tokens=300)
        return {"status": "SUCCESS", "response": res.content}
    except AINotConfiguredException:
        return {"status": "AI_NOT_CONFIGURED", "response": ""}
    except __import__("app.ai.exceptions").ai.exceptions.AIAuthException:
        return {"status": "AI_AUTH_ERROR", "response": ""}
    except __import__("app.ai.exceptions").ai.exceptions.AIRateLimitException:
        return {"status": "AI_RATE_LIMITED", "response": ""}
    except __import__("app.ai.exceptions").ai.exceptions.AIProviderException as e:
        return {"status": "AI_PROVIDER_ERROR", "response": ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
