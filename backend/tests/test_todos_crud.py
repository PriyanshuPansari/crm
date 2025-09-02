import pytest
import uuid
from app.models.user import User, Role
from app.models.organization import Organization
from app.core.security import hash_password
from tests.conftest import get_auth_headers


@pytest.fixture
def todo_test_organization(db_session):
    """Create a test organization for todo CRUD tests"""
    unique_name = f"TodoCRUDOrg_{uuid.uuid4().hex[:8]}"
    org = Organization(name=unique_name)
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def todo_admin_user(db_session, todo_test_organization):
    """Create an admin user for todo CRUD tests"""
    unique_username = f"todo_crud_admin_{uuid.uuid4().hex[:8]}"
    unique_email = f"todo_crud_admin_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        username=unique_username,
        email=unique_email,
        hashed_password=hash_password("admin_password"),
        role=Role.ADMIN,
        organization_id=todo_test_organization.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def todo_member_user(db_session, todo_test_organization):
    """Create a member user for todo CRUD tests"""
    unique_username = f"todo_crud_member_{uuid.uuid4().hex[:8]}"
    unique_email = f"todo_crud_member_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        username=unique_username,
        email=unique_email,
        hashed_password=hash_password("member_password"),
        role=Role.MEMBER,
        organization_id=todo_test_organization.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_create_todo_as_member(client, todo_member_user):
    """Test that members can create todos"""
    headers = get_auth_headers(client, todo_member_user.username, "member_password")
    
    response = client.post(
        "/todos/",
        json={
            "title": "Member Todo",
            "description": "Complete homework assignment",
            "completed": False
        },
        headers=headers,
    )
    assert response.status_code == 200
    todo = response.json()
    assert todo["title"] == "Member Todo"
    assert todo["description"] == "Complete homework assignment"
    assert todo["completed"] == False
    assert "id" in todo
    assert "created_at" in todo


def test_create_todo_as_admin(client, todo_admin_user):
    """Test that admins can create todos"""
    headers = get_auth_headers(client, todo_admin_user.username, "admin_password")
    
    response = client.post(
        "/todos/",
        json={
            "title": "Admin Todo",
            "description": "Review team performance",
            "completed": False
        },
        headers=headers,
    )
    assert response.status_code == 200
    todo = response.json()
    assert todo["title"] == "Admin Todo"
    assert todo["description"] == "Review team performance"


def test_list_todos(client, todo_admin_user, todo_member_user):
    """Test that users can list todos from their organization"""
    admin_headers = get_auth_headers(client, todo_admin_user.username, "admin_password")
    member_headers = get_auth_headers(client, todo_member_user.username, "member_password")
    
    # Create todos by both users
    client.post(
        "/todos/",
        json={"title": "Admin Task 1", "description": "First admin task"},
        headers=admin_headers,
    )
    client.post(
        "/todos/",
        json={"title": "Member Task 1", "description": "First member task"},
        headers=member_headers,
    )
    
    # Both should see both todos (same organization)
    response = client.get("/todos/", headers=admin_headers)
    assert response.status_code == 200
    admin_todos = response.json()
    assert len(admin_todos) >= 2
    
    response = client.get("/todos/", headers=member_headers)
    assert response.status_code == 200
    member_todos = response.json()
    assert len(member_todos) >= 2


def test_get_individual_todo(client, todo_member_user):
    """Test getting an individual todo by ID"""
    headers = get_auth_headers(client, todo_member_user.username, "member_password")
    
    # Create a todo
    response = client.post(
        "/todos/",
        json={"title": "Individual Todo", "description": "Test getting single todo"},
        headers=headers,
    )
    assert response.status_code == 200
    todo_id = response.json()["id"]
    
    # Get the specific todo
    response = client.get(f"/todos/{todo_id}", headers=headers)
    assert response.status_code == 200
    todo = response.json()
    assert todo["title"] == "Individual Todo"
    assert todo["id"] == todo_id


def test_update_todo_as_member(client, todo_member_user):
    """Test that members can update todos"""
    headers = get_auth_headers(client, todo_member_user.username, "member_password")
    
    # Create a todo
    response = client.post(
        "/todos/",
        json={"title": "Original Todo", "description": "Original description", "completed": False},
        headers=headers,
    )
    assert response.status_code == 200
    todo_id = response.json()["id"]
    
    # Update the todo
    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "Updated Todo", "description": "Updated description", "completed": True},
        headers=headers,
    )
    assert response.status_code == 200
    updated_todo = response.json()
    assert updated_todo["title"] == "Updated Todo"
    assert updated_todo["description"] == "Updated description"
    assert updated_todo["completed"] == True


def test_update_todo_as_admin(client, todo_admin_user):
    """Test that admins can update todos"""
    headers = get_auth_headers(client, todo_admin_user.username, "admin_password")
    
    # Create a todo
    response = client.post(
        "/todos/",
        json={"title": "Admin Original", "description": "Admin task", "completed": False},
        headers=headers,
    )
    assert response.status_code == 200
    todo_id = response.json()["id"]
    
    # Update the todo
    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "Admin Updated", "description": "Updated admin task", "completed": True},
        headers=headers,
    )
    assert response.status_code == 200
    updated_todo = response.json()
    assert updated_todo["title"] == "Admin Updated"
    assert updated_todo["completed"] == True


def test_member_cannot_delete_todo(client, todo_member_user):
    """Test that members cannot delete todos (admin only operation)"""
    headers = get_auth_headers(client, todo_member_user.username, "member_password")
    
    # Create a todo
    response = client.post(
        "/todos/",
        json={"title": "Todo to Delete", "description": "This should not be deletable by member"},
        headers=headers,
    )
    assert response.status_code == 200
    todo_id = response.json()["id"]
    
    # Try to delete (should fail)
    response = client.delete(f"/todos/{todo_id}", headers=headers)
    assert response.status_code == 403  # Forbidden


def test_admin_can_delete_todo(client, todo_admin_user):
    """Test that admins can delete todos"""
    headers = get_auth_headers(client, todo_admin_user.username, "admin_password")
    
    # Create a todo
    response = client.post(
        "/todos/",
        json={"title": "Admin Deletable Todo", "description": "Admin can delete this"},
        headers=headers,
    )
    assert response.status_code == 200
    todo_id = response.json()["id"]
    
    # Delete the todo (should succeed)
    response = client.delete(f"/todos/{todo_id}", headers=headers)
    assert response.status_code == 200
    deleted_todo = response.json()
    assert deleted_todo["id"] == todo_id


def test_admin_can_delete_member_todo(client, todo_admin_user, todo_member_user):
    """Test that admins can delete todos created by members"""
    admin_headers = get_auth_headers(client, todo_admin_user.username, "admin_password")
    member_headers = get_auth_headers(client, todo_member_user.username, "member_password")
    
    # Member creates a todo
    response = client.post(
        "/todos/",
        json={"title": "Member's Todo", "description": "Created by member"},
        headers=member_headers,
    )
    assert response.status_code == 200
    todo_id = response.json()["id"]
    
    # Admin deletes member's todo (should succeed)
    response = client.delete(f"/todos/{todo_id}", headers=admin_headers)
    assert response.status_code == 200


def test_todo_not_found_errors(client, todo_member_user):
    """Test proper 404 errors for non-existent todos"""
    headers = get_auth_headers(client, todo_member_user.username, "member_password")
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    # Try to get non-existent todo
    response = client.get(f"/todos/{fake_uuid}", headers=headers)
    assert response.status_code == 404
    
    # Try to update non-existent todo
    response = client.put(
        f"/todos/{fake_uuid}",
        json={"title": "Updated", "description": "Should not work"},
        headers=headers,
    )
    assert response.status_code == 404


def test_todo_validation_errors(client, todo_member_user):
    """Test validation errors for invalid todo data"""
    headers = get_auth_headers(client, todo_member_user.username, "member_password")
    
    # Try to create todo without required title
    response = client.post(
        "/todos/",
        json={"description": "No title provided"},
        headers=headers,
    )
    assert response.status_code == 422  # Unprocessable Entity
    
    # Try to create todo with empty title
    response = client.post(
        "/todos/",
        json={"title": "", "description": "Empty title"},
        headers=headers,
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_unauthorized_access_to_todos(client):
    """Test that unauthenticated requests are rejected"""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    # Try to list todos without auth
    response = client.get("/todos/")
    assert response.status_code == 401
    
    # Try to create todo without auth
    response = client.post("/todos/", json={"title": "Unauthorized"})
    assert response.status_code == 401
    
    # Try to get specific todo without auth
    response = client.get(f"/todos/{fake_uuid}")
    assert response.status_code == 401
    
    # Try to update todo without auth
    response = client.put(f"/todos/{fake_uuid}", json={"title": "Hacked"})
    assert response.status_code == 401
    
    # Try to delete todo without auth
    response = client.delete(f"/todos/{fake_uuid}")
    assert response.status_code == 401
