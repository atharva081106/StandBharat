from pydantic import BaseModel
import uuid
from typing import Optional

class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    owner_id: uuid.UUID

    class Config:
        from_attributes = True
