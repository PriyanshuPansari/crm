from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.note import NoteOut, NoteCreate, NoteUpdate
from app.crud.crud_note import crud_note
from app.api.deps import get_db, get_current_active_user, require_admin
from app.models.note import Note

router = APIRouter()

@router.get("/", response_model=List[NoteOut])
def read_notes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return crud_note.get_multi_by_org(db, org_id=current_user.organization_id)


@router.get("/{note_id}", response_model=NoteOut)
def get_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    db_obj = db.query(Note).filter(
        Note.id == note_id, Note.organization_id == current_user.organization_id
    ).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_obj


@router.post("/", response_model=NoteOut)
def create_note(
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return crud_note.create(
        db, obj_in=note_in, user_id=current_user.id, org_id=current_user.organization_id
    )


@router.put("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: str,
    note_in: NoteUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    db_obj = db.query(Note).filter(
        Note.id == note_id, Note.organization_id == current_user.organization_id
    ).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    return crud_note.update(db, db_obj=db_obj, obj_in=note_in)


@router.delete("/{note_id}", response_model=NoteOut)
def delete_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),  # only ADMIN
):
    db_obj = db.query(Note).filter(
        Note.id == note_id, Note.organization_id == current_user.organization_id
    ).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    return crud_note.delete(db, db_obj=db_obj)
