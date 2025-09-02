import uuid
from sqlalchemy import Column, ForeignKey, Table, DateTime, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

# Import Role enum for per-organization roles
import enum

class UserOrganizationRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

class UserOrganization(Base):
    """Model for user-organization relationships with per-organization roles"""
    __tablename__ = 'user_organizations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    role = Column(Enum(UserOrganizationRole), default=UserOrganizationRole.MEMBER, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="user_organizations")
    organization = relationship("Organization", back_populates="user_organizations")

# Keep the association table for backward compatibility during migration
user_organization_association = Table(
    'user_organizations_old',
    Base.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), nullable=False),
    Column('organization_id', UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False),
    Column('role', Enum(UserOrganizationRole), default=UserOrganizationRole.MEMBER, nullable=False),
    Column('joined_at', DateTime(timezone=True), server_default=func.now()),
    # Ensure a user can't be added to the same organization twice
    schema=None
)
