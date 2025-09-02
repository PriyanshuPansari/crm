from sqlalchemy.orm import Session
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate
from uuid import UUID


def create_todo(db: Session, todo_in: TodoCreate, user_id: UUID, org_id: UUID) -> Todo:
    """Create a new todo"""
    todo = Todo(
        **todo_in.model_dump(),
        created_by=user_id,
        organization_id=org_id,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def get_todos(db: Session, org_id: UUID) -> list[Todo]:
    """Get all todos for an organization"""
    return db.query(Todo).filter(Todo.organization_id == org_id).all()


def update_todo(db: Session, todo: Todo, todo_in: TodoUpdate) -> Todo:
    """Update a todo"""
    for field, value in todo_in.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo: Todo) -> Todo:
    """Delete a todo"""
    db.delete(todo)
    db.commit()
    return todo


def get_todo_by_id(db: Session, todo_id: UUID, org_id: UUID) -> Todo | None:
    """Get a todo by ID within an organization"""
    return db.query(Todo).filter(
        Todo.id == todo_id, 
        Todo.organization_id == org_id
    ).first()
