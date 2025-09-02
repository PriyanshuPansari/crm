from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.schemas.note import NoteOut, NoteCreate, NoteUpdate
from app.crud.crud_note import crud_note
from app.api.deps import get_db, get_current_active_user, require_admin
from app.models.note import Note
from app.models.organization import Organization

router = APIRouter()

@router.get("/org/{org_id}", response_model=List[NoteOut])
def read_notes(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # Check if user is a member of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    return crud_note.get_multi_by_org(db, org_id=org_id)


@router.get("/org/{org_id}/{note_id}", response_model=NoteOut)
def get_note(
    org_id: UUID,
    note_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # Check if user is a member of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    db_obj = db.query(Note).filter(
        Note.id == note_id, Note.organization_id == org_id
    ).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_obj


@router.post("/org/{org_id}", response_model=NoteOut)
def create_note(
    org_id: UUID,
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # Check if user is a member of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    return crud_note.create(
        db, obj_in=note_in, user_id=current_user.id, org_id=org_id
    )


@router.put("/org/{org_id}/{note_id}", response_model=NoteOut)
def update_note(
    org_id: UUID,
    note_id: str,
    note_in: NoteUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # Check if user is a member of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    db_obj = db.query(Note).filter(
        Note.id == note_id, Note.organization_id == org_id
    ).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    return crud_note.update(db, db_obj=db_obj, obj_in=note_in)


@router.delete("/org/{org_id}/{note_id}", response_model=NoteOut)
def delete_note(
    org_id: UUID,
    note_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),  # only ADMIN
):
    # Check if user is an admin of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    db_obj = db.query(Note).filter(
        Note.id == note_id, Note.organization_id == org_id
    ).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    return crud_note.delete(db, db_obj=db_obj)


# Backward compatibility endpoints - use user's first organization
@router.get("/", response_model=List[NoteOut])
def read_notes_legacy(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Get notes from user's first organization (for backward compatibility)"""
    if not current_user.organizations:
        raise HTTPException(status_code=403, detail="User not in any organization")
    
    org_id = current_user.organizations[0].id
    return crud_note.get_multi_by_org(db, org_id=org_id)


@router.post("/", response_model=NoteOut)
def create_note_legacy(
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Create note in user's first organization (for backward compatibility)"""
    if not current_user.organizations:
        raise HTTPException(status_code=403, detail="User not in any organization")
    
    org_id = current_user.organizations[0].id
    return crud_note.create(db, obj_in=note_in, org_id=org_id, user_id=current_user.id)


@router.get("/{note_id}", response_model=NoteOut)
def get_note_legacy(
    note_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Get a specific note from user's first organization (for backward compatibility)"""
    if not current_user.organizations:
        raise HTTPException(status_code=403, detail="User not in any organization")
    
    org_id = current_user.organizations[0].id
    db_obj = db.query(Note).filter(
        Note.id == note_id, Note.organization_id == org_id
    ).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_obj


@router.put("/{note_id}", response_model=NoteOut)
def update_note_legacy(
    note_id: str,
    note_in: NoteUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Update a note in user's first organization (for backward compatibility)"""
    if not current_user.organizations:
        raise HTTPException(status_code=403, detail="User not in any organization")
    
    org_id = current_user.organizations[0].id
    db_obj = db.query(Note).filter(
        Note.id == note_id, Note.organization_id == org_id
    ).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    return crud_note.update(db, db_obj=db_obj, obj_in=note_in)


@router.delete("/{note_id}", response_model=NoteOut)
def delete_note_legacy(
    note_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Delete a note from user's first organization (for backward compatibility)"""
    if not current_user.organizations:
        raise HTTPException(status_code=403, detail="User not in any organization")
    
    org_id = current_user.organizations[0].id
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    db_obj = db.query(Note).filter(
        Note.id == note_id, Note.organization_id == org_id
    ).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    return crud_note.delete(db, db_obj=db_obj)
