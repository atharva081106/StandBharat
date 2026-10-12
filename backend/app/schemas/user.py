from pydantic import ConfigDict, BaseModel, EmailStr
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str | None = None
    model_config = ConfigDict(from_attributes=True)
