import pytest
import uuid
from app.models.user import User
from app.models.user_organization import UserOrganization, UserOrganizationRole
from app.models.organization import Organization
from app.core.security import hash_password
from tests.conftest import get_auth_headers


@pytest.fixture
def test_organization(db_session):
    """Create a test organization with unique name"""
    unique_name = f"TestOrg_{uuid.uuid4().hex[:8]}"
    org = Organization(name=unique_name)
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def admin_user(db_session, test_organization):
    """Create an admin user"""
    unique_username = f"admin_user_{uuid.uuid4().hex[:8]}"
    unique_email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        username=unique_username,
        email=unique_email,
        hashed_password=hash_password("admin_password"),
        is_active=True
    )
    db_session.add(user)
    db_session.flush()
    
    # Add user to organization with admin role
    user_org = UserOrganization(
        user_id=user.id,
        organization_id=test_organization.id,
        role=UserOrganizationRole.ADMIN
    )
    db_session.add(user_org)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def member_user(db_session, test_organization):
    """Create a member user"""
    unique_username = f"member_user_{uuid.uuid4().hex[:8]}"
    unique_email = f"member_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        username=unique_username,
        email=unique_email,
        hashed_password=hash_password("member_password"),
        is_active=True
    )
    db_session.add(user)
    db_session.flush()
    
    # Add user to organization with member role
    user_org = UserOrganization(
        user_id=user.id,
        organization_id=test_organization.id,
        role=UserOrganizationRole.MEMBER
    )
    db_session.add(user_org)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_admin_can_create_and_delete_notes(client, admin_user):
    """Test that admin users can create and delete notes"""
    # Get admin headers
    headers = get_auth_headers(client, admin_user.username, "admin_password")

    # Create note
    response = client.post(
        "/notes/",
        json={"title": "Admin Note", "content": "Secret admin stuff"},
        headers=headers,
    )
    assert response.status_code == 200
    note_data = response.json()
    assert note_data["title"] == "Admin Note"
    assert note_data["content"] == "Secret admin stuff"
    note_id = note_data["id"]

    # Delete note (should succeed for admin)
    response = client.delete(f"/notes/{note_id}", headers=headers)
    assert response.status_code == 200


def test_member_can_create_but_not_delete_notes(client, admin_user, member_user):
    """Test that member users can create notes but cannot delete them"""
    # Get member headers
    member_headers = get_auth_headers(client, member_user.username, "member_password")
    
    # Member creates a note
    response = client.post(
        "/notes/",
        json={"title": "Member Note", "content": "Just a thought"},
        headers=member_headers,
    )
    assert response.status_code == 200
    note_data = response.json()
    assert note_data["title"] == "Member Note"
    note_id = note_data["id"]

    # Member tries to delete their own note (should fail)
    response = client.delete(f"/notes/{note_id}", headers=member_headers)
    assert response.status_code == 403  # Forbidden


def test_member_cannot_delete_admin_notes(client, admin_user, member_user):
    """Test that member users cannot delete notes created by admins"""
    # Get headers for both users
    admin_headers = get_auth_headers(client, admin_user.username, "admin_password")
    member_headers = get_auth_headers(client, member_user.username, "member_password")

    # Admin creates a note
    response = client.post(
        "/notes/",
        json={"title": "Admin Secret", "content": "Top secret information"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    note_id = response.json()["id"]

    # Member tries to delete admin's note (should fail)
    response = client.delete(f"/notes/{note_id}", headers=member_headers)
    assert response.status_code == 403  # Forbidden

    # Admin can delete their own note (should succeed)
    response = client.delete(f"/notes/{note_id}", headers=admin_headers)
    assert response.status_code == 200


def test_users_can_only_see_notes_from_their_organization(client, admin_user, member_user, db_session):
    """Test that users can only see notes from their own organization"""
    # Create another organization and user
    other_org_name = f"OtherOrg_{uuid.uuid4().hex[:8]}"
    other_org = Organization(name=other_org_name)
    db_session.add(other_org)
    db_session.commit()
    db_session.refresh(other_org)
    
    other_username = f"other_user_{uuid.uuid4().hex[:8]}"
    other_email = f"other_{uuid.uuid4().hex[:8]}@example.com"
    other_user = User(
        username=other_username,
        email=other_email,
        hashed_password=hash_password("other_password"),
        role=Role.MEMBER,
        is_active=True
    )
    db_session.add(other_user)
    db_session.flush()
    
    # Add user to the other organization
    other_org.users.append(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    # Get headers for users from different orgs
    member_headers = get_auth_headers(client, member_user.username, "member_password")
    other_headers = get_auth_headers(client, other_user.username, "other_password")

    # Member creates a note
    response = client.post(
        "/notes/",
        json={"title": "Org1 Note", "content": "Organization 1 content"},
        headers=member_headers,
    )
    assert response.status_code == 200

    # Other user creates a note
    response = client.post(
        "/notes/",
        json={"title": "Org2 Note", "content": "Organization 2 content"},
        headers=other_headers,
    )
    assert response.status_code == 200

    # Member gets notes (should only see their org's notes)
    response = client.get("/notes/", headers=member_headers)
    assert response.status_code == 200
    notes = response.json()
    # Should only see notes from their organization
    for note in notes:
        assert note["title"] in ["Org1 Note"]

    # Other user gets notes (should only see their org's notes)
    response = client.get("/notes/", headers=other_headers)
    assert response.status_code == 200
    notes = response.json()
    # Should only see notes from their organization
    for note in notes:
        assert note["title"] in ["Org2 Note"]
