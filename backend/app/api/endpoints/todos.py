from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, require_admin
from app.schemas.todo import TodoCreate, TodoUpdate, TodoOut
from app.crud import crud_todo
from app.models.user import User
from app.models.organization import Organization

router = APIRouter()


@router.get("/org/{org_id}", response_model=List[TodoOut])
def list_todos(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all todos for the specified organization"""
    # Check if user is a member of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    return crud_todo.get_todos(db, org_id)


@router.get("/{todo_id}", response_model=TodoOut)
def get_todo(
    todo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific todo by ID (organization-scoped)"""
    # Get user's first organization for backward compatibility
    if not current_user.organizations:
        raise HTTPException(status_code=403, detail="User not in any organization")
    
    user_org_id = current_user.organizations[0].id
    todo = crud_todo.get_todo_by_id(db, todo_id, user_org_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.post("/org/{org_id}", response_model=TodoOut)
def create_todo(
    org_id: UUID,
    todo_in: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new todo"""
    # Check if user is a member of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    return crud_todo.create_todo(db, todo_in, current_user.id, org_id)


@router.put("/org/{org_id}/{todo_id}", response_model=TodoOut)
def update_todo(
    org_id: UUID,
    todo_id: UUID,
    todo_in: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a todo (any user can update todos in their organization)"""
    # Check if user is a member of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    todo = crud_todo.get_todo_by_id(db, todo_id, org_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud_todo.update_todo(db, todo, todo_in)


@router.delete("/org/{org_id}/{todo_id}", response_model=TodoOut)
def delete_todo(
    org_id: UUID,
    todo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),  # Only admins can delete
):
    """Delete a todo (admin only)"""
    # Check if user is an admin of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    todo = crud_todo.get_todo_by_id(db, todo_id, org_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud_todo.delete_todo(db, todo)


# Backward compatibility endpoints - use user's first organization
@router.get("/", response_model=List[TodoOut])
def list_todos_legacy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all todos from user's first organization (for backward compatibility)"""
    if not current_user.organizations:
        raise HTTPException(status_code=403, detail="User not in any organization")
    
    user_org_id = current_user.organizations[0].id
    return crud_todo.get_todos(db, user_org_id)


@router.post("/", response_model=TodoOut)
def create_todo_legacy(
    todo_in: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new todo in user's first organization (for backward compatibility)"""
    if not current_user.organizations:
        raise HTTPException(status_code=403, detail="User not in any organization")
    
    user_org_id = current_user.organizations[0].id
    return crud_todo.create_todo(db, todo_in, current_user.id, user_org_id)


@router.put("/org/{org_id}/{todo_id}", response_model=TodoOut)
def update_todo(
    org_id: UUID,
    todo_id: UUID,
    todo_in: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a todo"""
    # Check if user is a member of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    todo = crud_todo.get_todo_by_id(db, todo_id, org_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Allow users to update their own todos, or admins to update any
    if todo.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="You can only update your own todos")
    
    return crud_todo.update_todo(db, todo, todo_in)


@router.delete("/org/{org_id}/{todo_id}", response_model=TodoOut)
def delete_todo(
    org_id: UUID,
    todo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a todo"""
    # Check if user is a member of this organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or current_user not in org.users:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    todo = crud_todo.get_todo_by_id(db, todo_id, org_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Allow users to delete their own todos, or admins to delete any
    if todo.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="You can only delete your own todos")
    
    return crud_todo.delete_todo(db, todo)


@router.delete("/{todo_id}", response_model=TodoOut)
def delete_todo_legacy(
    todo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a todo from user's first organization (for backward compatibility)"""
    if not current_user.organizations:
        raise HTTPException(status_code=403, detail="User not in any organization")
    
    user_org_id = current_user.organizations[0].id
    todo = crud_todo.get_todo_by_id(db, todo_id, user_org_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Allow users to delete their own todos, or admins to delete any
    if todo.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="You can only delete your own todos")
    
    return crud_todo.delete_todo(db, todo)


@router.put("/{todo_id}", response_model=TodoOut)
def update_todo_legacy(
    todo_id: UUID,
    todo_in: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a todo in user's first organization (for backward compatibility)"""
    if not current_user.organizations:
        raise HTTPException(status_code=403, detail="User not in any organization")
    
    user_org_id = current_user.organizations[0].id
    todo = crud_todo.get_todo_by_id(db, todo_id, user_org_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Allow users to update their own todos, or admins to update any
    if todo.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="You can only update your own todos")
    
    return crud_todo.update_todo(db, todo, todo_in)

