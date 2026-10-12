from pydantic import ConfigDict, BaseModel
import uuid
from typing import Optional

class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    owner_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
