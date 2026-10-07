from typing import Any, Dict, Optional
from pydantic import BaseModel

class AgentResult(BaseModel):
    status: str # SUCCESS, FAILED
    output_data: Dict[str, Any] = {}
    error: Optional[str] = None
