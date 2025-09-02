import pytest
import uuid
from app.models.user import User, Role
from app.models.organization import Organization
from app.core.security import hash_password
from tests.conftest import get_auth_headers


@pytest.fixture
def test_todo_organization(db_session):
    """Create a test organization for todo tests"""
    unique_name = f"TodoTestOrg_{uuid.uuid4().hex[:8]}"
    org = Organization(name=unique_name)
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def todo_admin_user(db_session, test_todo_organization):
    """Create an admin user for todo tests"""
    unique_username = f"todo_admin_{uuid.uuid4().hex[:8]}"
    unique_email = f"todo_admin_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        username=unique_username,
        email=unique_email,
        hashed_password=hash_password("admin_password"),
        role=Role.ADMIN,
        organization_id=test_todo_organization.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def todo_member_user(db_session, test_todo_organization):
    """Create a member user for todo tests"""
    unique_username = f"todo_member_{uuid.uuid4().hex[:8]}"
    unique_email = f"todo_member_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        username=unique_username,
        email=unique_email,
        hashed_password=hash_password("member_password"),
        role=Role.MEMBER,
        organization_id=test_todo_organization.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_member_can_create_but_not_delete_todo(client, todo_admin_user, todo_member_user):
    """Test that member users can create todos but cannot delete them"""
    # Get member headers
    member_headers = get_auth_headers(client, todo_member_user.username, "member_password")

    # Member creates a todo
    response = client.post(
        "/todos/",
        json={"title": "MemberTask", "description": "do homework", "completed": False},
        headers=member_headers,
    )
    assert response.status_code == 200
    todo_data = response.json()
    assert todo_data["title"] == "MemberTask"
    assert todo_data["description"] == "do homework"
    assert todo_data["completed"] == False
    todo_id = todo_data["id"]

    # Member tries to delete the todo (should fail)
    response = client.delete(f"/todos/{todo_id}", headers=member_headers)
    assert response.status_code == 403  # Forbidden


def test_admin_can_delete_todo(client, todo_admin_user):
    """Test that admin users can create and delete todos"""
    # Get admin headers
    admin_headers = get_auth_headers(client, todo_admin_user.username, "admin_password")

    # Admin creates a todo
    response = client.post(
        "/todos/",
        json={"title": "AdminTask", "description": "secret work", "completed": False},
        headers=admin_headers,
    )
    assert response.status_code == 200
    todo_data = response.json()
    assert todo_data["title"] == "AdminTask"
    todo_id = todo_data["id"]

    # Admin deletes the todo (should succeed)
    response = client.delete(f"/todos/{todo_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == todo_id


def test_member_can_update_todos(client, todo_member_user):
    """Test that member users can update todos"""
    # Get member headers
    member_headers = get_auth_headers(client, todo_member_user.username, "member_password")

    # Member creates a todo
    response = client.post(
        "/todos/",
        json={"title": "UpdateTask", "description": "original description", "completed": False},
        headers=member_headers,
    )
    assert response.status_code == 200
    todo_id = response.json()["id"]

    # Member updates the todo (should succeed)
    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "UpdatedTask", "description": "updated description", "completed": True},
        headers=member_headers,
    )
    assert response.status_code == 200
    updated_todo = response.json()
    assert updated_todo["title"] == "UpdatedTask"
    assert updated_todo["description"] == "updated description"
    assert updated_todo["completed"] == True


def test_users_can_only_see_todos_from_their_organization(client, todo_member_user, db_session):
    """Test that users can only see todos from their own organization"""
    # Create another organization and user
    other_org_name = f"OtherTodoOrg_{uuid.uuid4().hex[:8]}"
    other_org = Organization(name=other_org_name)
    db_session.add(other_org)
    db_session.commit()
    db_session.refresh(other_org)
    
    other_username = f"other_todo_user_{uuid.uuid4().hex[:8]}"
    other_email = f"other_todo_{uuid.uuid4().hex[:8]}@example.com"
    other_user = User(
        username=other_username,
        email=other_email,
        hashed_password=hash_password("other_password"),
        role=Role.MEMBER,
        organization_id=other_org.id,
        is_active=True
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    # Get headers for users from different orgs
    member_headers = get_auth_headers(client, todo_member_user.username, "member_password")
    other_headers = get_auth_headers(client, other_user.username, "other_password")

    # Member creates a todo
    response = client.post(
        "/todos/",
        json={"title": "Org1 Todo", "description": "Organization 1 task"},
        headers=member_headers,
    )
    assert response.status_code == 200

    # Other user creates a todo
    response = client.post(
        "/todos/",
        json={"title": "Org2 Todo", "description": "Organization 2 task"},
        headers=other_headers,
    )
    assert response.status_code == 200

    # Member gets todos (should only see their org's todos)
    response = client.get("/todos/", headers=member_headers)
    assert response.status_code == 200
    todos = response.json()
    # Should only see todos from their organization
    org1_todos = [todo for todo in todos if todo["title"] == "Org1 Todo"]
    assert len(org1_todos) == 1
    # Should not see todos from other organization
    org2_todos = [todo for todo in todos if todo["title"] == "Org2 Todo"]
    assert len(org2_todos) == 0

    # Other user gets todos (should only see their org's todos)
    response = client.get("/todos/", headers=other_headers)
    assert response.status_code == 200
    todos = response.json()
    # Should only see todos from their organization
    org2_todos = [todo for todo in todos if todo["title"] == "Org2 Todo"]
    assert len(org2_todos) == 1
    # Should not see todos from other organization
    org1_todos = [todo for todo in todos if todo["title"] == "Org1 Todo"]
    assert len(org1_todos) == 0
