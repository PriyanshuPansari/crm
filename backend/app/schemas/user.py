from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List
from app.models.user_organization import UserOrganizationRole


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    # Note: Role is now per-organization, not global


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    organization_ids: List[UUID] = []
    # Note: Role is now per-organization, use organization endpoints to get roles

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        # Extract organization IDs from the organizations relationship
        organization_ids = [org.id for org in obj.organizations] if obj.organizations else []
        return cls(
            id=obj.id,
            username=obj.username,
            email=obj.email,
            is_active=obj.is_active,
            organization_ids=organization_ids
        )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
