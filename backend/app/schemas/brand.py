from pydantic import BaseModel
import uuid
from typing import Optional

class BrandCreate(BaseModel):
    workspace_id: uuid.UUID
    name: str
    website_url: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None

class BrandResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    website_url: Optional[str]
    description: Optional[str]
    industry: Optional[str]
    status: str

    class Config:
        from_attributes = True
