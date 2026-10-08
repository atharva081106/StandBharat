from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class AIToolCall(BaseModel):
    id: str
    type: str = "function"
    function: Dict[str, Any] # {"name": "...", "arguments": "{...}"}

class AIRequestMessage(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[AIToolCall]] = None
    tool_call_id: Optional[str] = None

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
    content: Optional[str] = None
    tool_calls: Optional[List[AIToolCall]] = None
    info: AIResponseInfo
