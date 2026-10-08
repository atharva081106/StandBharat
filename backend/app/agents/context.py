from typing import Any, Dict, Optional
from pydantic import BaseModel
import uuid
from app.schemas.brand_brain import BrandContextResponse

class AgentContext(BaseModel):
    run_id: uuid.UUID
    workspace_id: uuid.UUID
    brand_id: uuid.UUID
    user_id: uuid.UUID
    input_data: Dict[str, Any] = {}
    brand_context: Optional[BrandContextResponse] = None
    task_id: Optional[uuid.UUID] = None
