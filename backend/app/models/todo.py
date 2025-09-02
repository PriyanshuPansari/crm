import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

# Import related models to avoid circular import issues
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class Todo(Base):
    __tablename__ = "todos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization", back_populates="todos")
    creator = relationship("User", back_populates="todos")
