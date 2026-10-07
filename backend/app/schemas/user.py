from pydantic import BaseModel, EmailStr
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str | None = None
    class Config:
        from_attributes = True
