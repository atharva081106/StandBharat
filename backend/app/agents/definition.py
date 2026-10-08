from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentDefinition(BaseModel):
    id: str
    name: str
    description: str
    category: str
    capabilities: List[str]
    required_integrations: List[str] = Field(default_factory=list)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)
    approval_policy: str = "DEFAULT" # e.g. "DEFAULT", "ALWAYS_REQUIRE", "NEVER_REQUIRE"
