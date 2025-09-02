from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from app.models.user import Role


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: Optional[Role] = Role.MEMBER


class UserResponse(UserBase):
    id: UUID
    role: Role
    is_active: bool
    organization_id: Optional[UUID]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
