import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

# Import related models to avoid circular import issues
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.note import Note
    from app.models.todo import Todo


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to user-organization associations (with per-org roles)
    user_organizations = relationship("UserOrganization", back_populates="user", cascade="all, delete-orphan")
    
    # Many-to-many relationship with organizations (through UserOrganization)
    organizations = relationship(
        "Organization",
        secondary="user_organizations",
        back_populates="users",
        viewonly=True
    )
    
    notes = relationship("Note", back_populates="user")
    todos = relationship("Todo", back_populates="creator")
    
    def get_role_in_organization(self, org_id):
        """Get user's role in a specific organization"""
        for user_org in self.user_organizations:
            if user_org.organization_id == org_id:
                return user_org.role
        return None
    
    def is_admin_in_organization(self, org_id):
        """Check if user is admin in a specific organization"""
        from app.models.user_organization import UserOrganizationRole
        return self.get_role_in_organization(org_id) == UserOrganizationRole.ADMIN
