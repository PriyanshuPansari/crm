from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, require_admin
from app.schemas.todo import TodoCreate, TodoUpdate, TodoOut
from app.crud import crud_todo
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[TodoOut])
def list_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all todos for the current user's organization"""
    return crud_todo.get_todos(db, current_user.organization_id)


@router.get("/{todo_id}", response_model=TodoOut)
def get_todo(
    todo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific todo by ID (organization-scoped)"""
    todo = crud_todo.get_todo_by_id(db, todo_id, current_user.organization_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.post("/", response_model=TodoOut)
def create_todo(
    todo_in: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new todo"""
    return crud_todo.create_todo(db, todo_in, current_user.id, current_user.organization_id)


@router.put("/{todo_id}", response_model=TodoOut)
def update_todo(
    todo_id: UUID,
    todo_in: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a todo (any user can update todos in their organization)"""
    todo = crud_todo.get_todo_by_id(db, todo_id, current_user.organization_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud_todo.update_todo(db, todo, todo_in)


@router.delete("/{todo_id}", response_model=TodoOut)
def delete_todo(
    todo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),  # Only admins can delete
):
    """Delete a todo (admin only)"""
    todo = crud_todo.get_todo_by_id(db, todo_id, current_user.organization_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud_todo.delete_todo(db, todo)
