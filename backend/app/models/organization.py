import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

# Import related models to avoid circular import issues
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.note import Note
    from app.models.todo import Todo


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to user-organization associations (with per-org roles)
    user_organizations = relationship("UserOrganization", back_populates="organization", cascade="all, delete-orphan")
    
    # Many-to-many relationship with users (through UserOrganization)
    users = relationship(
        "User",
        secondary="user_organizations",
        back_populates="organizations",
        viewonly=True
    )
    
    notes = relationship("Note", back_populates="org")
    todos = relationship("Todo", back_populates="organization")
    
    def get_user_role(self, user_id):
        """Get a user's role in this organization"""
        for user_org in self.user_organizations:
            if user_org.user_id == user_id:
                return user_org.role
        return None
    
    def get_admins(self):
        """Get all admin users in this organization"""
        from app.models.user_organization import UserOrganizationRole
        return [uo.user for uo in self.user_organizations if uo.role == UserOrganizationRole.ADMIN]
