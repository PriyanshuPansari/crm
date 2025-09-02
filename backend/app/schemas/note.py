from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: str | None = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass

class NoteOut(NoteBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True
