from sqlalchemy.orm import Session
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from uuid import UUID

class CRUDNote:
    def create(self, db: Session, *, obj_in: NoteCreate, user_id: UUID, org_id: UUID):
        db_obj = Note(
            title=obj_in.title,
            content=obj_in.content,
            created_by=user_id,
            organization_id=org_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_org(self, db: Session, org_id: UUID):
        return db.query(Note).filter(Note.organization_id == org_id).all()

    def update(self, db: Session, *, db_obj: Note, obj_in: NoteUpdate):
        db_obj.title = obj_in.title
        db_obj.content = obj_in.content
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, db_obj: Note):
        db.delete(db_obj)
        db.commit()
        return db_obj

crud_note = CRUDNote()
