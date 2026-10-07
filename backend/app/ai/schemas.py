from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class AIRequestMessage(BaseModel):
    role: str
    content: str

class AIResponseInfo(BaseModel):
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    finish_reason: Optional[str] = None
    request_id: Optional[str] = None
    latency_ms: Optional[float] = None
    estimated_cost: Optional[float] = None

class AIResponse(BaseModel):
    content: str
    info: AIResponseInfo
