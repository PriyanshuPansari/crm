import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base

# Import related models to avoid circular import issues
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.note import Note
    from app.models.todo import Todo


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.MEMBER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))

    organization = relationship("Organization", back_populates="users")
    notes = relationship("Note", back_populates="user")
    todos = relationship("Todo", back_populates="creator")
