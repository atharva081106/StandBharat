from pydantic import ConfigDict, BaseModel
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
    website_url: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: Optional[str] = None
    tagline: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

    def get(self, item: str, default: Optional[str] = None) -> Optional[str]:
        return getattr(self, item, default)

    def __getitem__(self, item: str):
        val = getattr(self, item, None)
        if val is not None:
            return val
        raise KeyError(item)
