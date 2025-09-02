from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title cannot be empty")
    description: Optional[str] = None
    completed: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Title cannot be empty")
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoOut(TodoBase):
    id: UUID
    organization_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
