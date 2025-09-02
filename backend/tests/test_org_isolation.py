import pytest
import uuid
from app.models.user import User
from app.models.user_organization import UserOrganization, UserOrganizationRole
from app.models.organization import Organization
from app.core.security import hash_password
from tests.conftest import get_auth_headers


@pytest.fixture
def org_a(db_session):
    """Create organization A"""
    org = Organization(name=f"OrgA_{uuid.uuid4().hex[:8]}")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def org_b(db_session):
    """Create organization B"""
    org = Organization(name=f"OrgB_{uuid.uuid4().hex[:8]}")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def org_a_admin(db_session, org_a):
    """Create admin user in organization A"""
    username = f"orga_admin_{uuid.uuid4().hex[:8]}"
    email = f"orga_admin_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password("password"),
        role=Role.ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()
    
    # Add user to organization using many-to-many relationship
    org_a.users.append(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def org_b_member(db_session, org_b):
    """Create member user in organization B"""
    username = f"orgb_member_{uuid.uuid4().hex[:8]}"
    email = f"orgb_member_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password("password"),
        role=Role.MEMBER,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()
    
    # Add user to organization using many-to-many relationship
    org_b.users.append(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_user_cannot_access_other_org_notes(client, org_a_admin, org_b_member):
    """Test that users cannot access notes from other organizations"""
    # Get headers for both users
    admin_headers = get_auth_headers(client, org_a_admin.username, "password")
    member_headers = get_auth_headers(client, org_b_member.username, "password")

    # OrgA admin creates a note
    response = client.post(
        "/notes/",
        json={"title": "OrgA Secret Note", "content": "Confidential information"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    note_id = response.json()["id"]

    # OrgB member tries to GET OrgA note (should fail)
    response = client.get(f"/notes/{note_id}", headers=member_headers)
    assert response.status_code == 404  # Note not found (due to org isolation)

    # OrgB member tries to UPDATE OrgA note (should fail)
    response = client.put(
        f"/notes/{note_id}",
        json={"title": "Hacked Note", "content": "I shouldn't see this"},
        headers=member_headers,
    )
    assert response.status_code == 404  # Note not found (due to org isolation)

    # OrgB member tries to DELETE OrgA note (should fail)
    response = client.delete(f"/notes/{note_id}", headers=member_headers)
    assert response.status_code in [403, 404]  # Either forbidden or not found

    # Verify OrgA admin can still access their note
    response = client.get(f"/notes/{note_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "OrgA Secret Note"


def test_user_cannot_access_other_org_todos(client, org_a_admin, org_b_member):
    """Test that users cannot access todos from other organizations"""
    # Get headers for both users
    admin_headers = get_auth_headers(client, org_a_admin.username, "password")
    member_headers = get_auth_headers(client, org_b_member.username, "password")

    # OrgA admin creates a todo
    response = client.post(
        "/todos/",
        json={"title": "OrgA Secret Todo", "description": "Confidential task", "completed": False},
        headers=admin_headers,
    )
    assert response.status_code == 200
    todo_id = response.json()["id"]

    # OrgB member tries to GET OrgA todo (should fail)
    response = client.get(f"/todos/{todo_id}", headers=member_headers)
    assert response.status_code == 404  # Todo not found (due to org isolation)

    # OrgB member tries to UPDATE OrgA todo (should fail)
    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "Hacked Todo", "description": "I shouldn't see this", "completed": True},
        headers=member_headers,
    )
    assert response.status_code == 404  # Todo not found (due to org isolation)

    # OrgB member tries to DELETE OrgA todo (should fail)
    response = client.delete(f"/todos/{todo_id}", headers=member_headers)
    assert response.status_code in [403, 404]  # Either forbidden or not found

    # Verify OrgA admin can still access their todo
    response = client.get(f"/todos/{todo_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "OrgA Secret Todo"


def test_list_endpoints_respect_org_boundaries(client, org_a_admin, org_b_member):
    """Test that list endpoints only show resources from user's organization"""
    # Get headers for both users
    admin_headers = get_auth_headers(client, org_a_admin.username, "password")
    member_headers = get_auth_headers(client, org_b_member.username, "password")

    # OrgA admin creates resources
    note_response = client.post(
        "/notes/",
        json={"title": "OrgA Note", "content": "OrgA content"},
        headers=admin_headers,
    )
    assert note_response.status_code == 200
    
    todo_response = client.post(
        "/todos/",
        json={"title": "OrgA Todo", "description": "OrgA task"},
        headers=admin_headers,
    )
    assert todo_response.status_code == 200

    # OrgB member creates resources
    note_response = client.post(
        "/notes/",
        json={"title": "OrgB Note", "content": "OrgB content"},
        headers=member_headers,
    )
    assert note_response.status_code == 200
    
    todo_response = client.post(
        "/todos/",
        json={"title": "OrgB Todo", "description": "OrgB task"},
        headers=member_headers,
    )
    assert todo_response.status_code == 200

    # OrgA admin lists notes (should only see OrgA notes)
    response = client.get("/notes/", headers=admin_headers)
    assert response.status_code == 200
    notes = response.json()
    orga_notes = [note for note in notes if note["title"] == "OrgA Note"]
    orgb_notes = [note for note in notes if note["title"] == "OrgB Note"]
    assert len(orga_notes) == 1
    assert len(orgb_notes) == 0

    # OrgA admin lists todos (should only see OrgA todos)
    response = client.get("/todos/", headers=admin_headers)
    assert response.status_code == 200
    todos = response.json()
    orga_todos = [todo for todo in todos if todo["title"] == "OrgA Todo"]
    orgb_todos = [todo for todo in todos if todo["title"] == "OrgB Todo"]
    assert len(orga_todos) == 1
    assert len(orgb_todos) == 0

    # OrgB member lists notes (should only see OrgB notes)
    response = client.get("/notes/", headers=member_headers)
    assert response.status_code == 200
    notes = response.json()
    orga_notes = [note for note in notes if note["title"] == "OrgA Note"]
    orgb_notes = [note for note in notes if note["title"] == "OrgB Note"]
    assert len(orga_notes) == 0
    assert len(orgb_notes) == 1

    # OrgB member lists todos (should only see OrgB todos)
    response = client.get("/todos/", headers=member_headers)
    assert response.status_code == 200
    todos = response.json()
    orga_todos = [todo for todo in todos if todo["title"] == "OrgA Todo"]
    orgb_todos = [todo for todo in todos if todo["title"] == "OrgB Todo"]
    assert len(orga_todos) == 0
    assert len(orgb_todos) == 1


def test_cross_org_admin_cannot_delete_other_org_resources(client, org_a_admin, org_b_member, db_session):
    """Test that even admins cannot delete resources from other organizations"""
    # Get organization B
    org_b = org_b_member.organizations[0]
    
    # Create an admin in organization B
    orgb_admin_username = f"orgb_admin_{uuid.uuid4().hex[:8]}"
    orgb_admin_email = f"orgb_admin_{uuid.uuid4().hex[:8]}@example.com"
    orgb_admin = User(
        username=orgb_admin_username,
        email=orgb_admin_email,
        hashed_password=hash_password("password"),
        role=Role.ADMIN,
        is_active=True
    )
    db_session.add(orgb_admin)
    db_session.flush()
    
    # Add admin to organization B
    org_b.users.append(orgb_admin)
    db_session.commit()
    db_session.refresh(orgb_admin)

    # Get headers for both admins
    orga_admin_headers = get_auth_headers(client, org_a_admin.username, "password")
    orgb_admin_headers = get_auth_headers(client, orgb_admin.username, "password")

    # OrgA admin creates resources
    note_response = client.post(
        "/notes/",
        json={"title": "OrgA Admin Note", "content": "OrgA admin content"},
        headers=orga_admin_headers,
    )
    assert note_response.status_code == 200
    orga_note_id = note_response.json()["id"]
    
    todo_response = client.post(
        "/todos/",
        json={"title": "OrgA Admin Todo", "description": "OrgA admin task"},
        headers=orga_admin_headers,
    )
    assert todo_response.status_code == 200
    orga_todo_id = todo_response.json()["id"]

    # OrgB admin tries to delete OrgA resources (should fail)
    response = client.delete(f"/notes/{orga_note_id}", headers=orgb_admin_headers)
    assert response.status_code == 404  # Not found due to org isolation

    response = client.delete(f"/todos/{orga_todo_id}", headers=orgb_admin_headers)
    assert response.status_code == 404  # Not found due to org isolation

    # OrgA admin can delete their own resources (should succeed)
    response = client.delete(f"/notes/{orga_note_id}", headers=orga_admin_headers)
    assert response.status_code == 200

    response = client.delete(f"/todos/{orga_todo_id}", headers=orga_admin_headers)
    assert response.status_code == 200
