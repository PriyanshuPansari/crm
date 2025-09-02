from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.models.user_organization import UserOrganizationRole


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Organization name")


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


class OrganizationOut(OrganizationBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserInvite(BaseModel):
    email: EmailStr
    role: UserOrganizationRole = UserOrganizationRole.MEMBER
    username: str = Field(..., min_length=3, max_length=50)


class UserInviteResponse(BaseModel):
    message: str
    user_id: UUID
    organization_id: UUID
    temporary_password: str


class UserRoleUpdate(BaseModel):
    role: UserOrganizationRole


class OrganizationMemberOut(BaseModel):
    id: UUID
    username: str
    email: str
    role: UserOrganizationRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationWithMembers(OrganizationOut):
    members: List[OrganizationMemberOut] = []
    user_role: Optional[UserOrganizationRole] = None  # User's role in this organization
