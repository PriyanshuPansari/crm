import pytest
import uuid
from app.models.user import User, Role
from app.models.organization import Organization
from app.core.security import hash_password
from tests.conftest import get_auth_headers


@pytest.fixture
def standalone_user(db_session):
    """Create a user not belonging to any organization"""
    unique_username = f"standalone_{uuid.uuid4().hex[:8]}"
    unique_email = f"standalone_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        username=unique_username,
        email=unique_email,
        hashed_password=hash_password("standalone_password"),
        role=Role.MEMBER,
        organization_id=None,  # No organization
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def existing_org_admin(db_session):
    """Create an organization with an admin user"""
    # Create organization
    org_name = f"ExistingOrg_{uuid.uuid4().hex[:8]}"
    org = Organization(name=org_name)
    db_session.add(org)
    db_session.flush()
    
    # Create admin user
    admin_username = f"existing_admin_{uuid.uuid4().hex[:8]}"
    admin_email = f"existing_admin_{uuid.uuid4().hex[:8]}@example.com"
    admin_user = User(
        username=admin_username,
        email=admin_email,
        hashed_password=hash_password("admin_password"),
        role=Role.ADMIN,
        organization_id=org.id,
        is_active=True
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    db_session.refresh(org)
    return admin_user


def test_create_organization(client, standalone_user):
    """Test creating a new organization"""
    headers = get_auth_headers(client, standalone_user.username, "standalone_password")
    
    response = client.post(
        "/organizations/",
        json={"name": "My New Organization"},
        headers=headers,
    )
    assert response.status_code == 200
    org_data = response.json()
    assert org_data["name"] == "My New Organization"
    assert "id" in org_data
    assert "created_at" in org_data


def test_cannot_create_org_if_already_member(client, existing_org_admin):
    """Test that users already in an organization cannot create another one"""
    headers = get_auth_headers(client, existing_org_admin.username, "admin_password")
    
    response = client.post(
        "/organizations/",
        json={"name": "Another Organization"},
        headers=headers,
    )
    assert response.status_code == 400
    assert "already belongs to an organization" in response.json()["detail"]


def test_get_my_organization(client, existing_org_admin):
    """Test getting current user's organization with members"""
    headers = get_auth_headers(client, existing_org_admin.username, "admin_password")
    
    response = client.get("/organizations/my", headers=headers)
    assert response.status_code == 200
    org_data = response.json()
    assert "name" in org_data
    assert "members" in org_data
    assert len(org_data["members"]) >= 1
    # Check that admin is in the members list
    admin_found = any(member["username"] == existing_org_admin.username for member in org_data["members"])
    assert admin_found


def test_invite_user_to_organization(client, existing_org_admin):
    """Test inviting a user to an organization"""
    headers = get_auth_headers(client, existing_org_admin.username, "admin_password")
    
    new_user_email = f"invited_{uuid.uuid4().hex[:8]}@example.com"
    new_username = f"invited_user_{uuid.uuid4().hex[:8]}"
    
    response = client.post(
        "/organizations/invite",
        json={
            "email": new_user_email,
            "username": new_username,
            "role": "MEMBER"
        },
        headers=headers,
    )
    assert response.status_code == 200
    invite_data = response.json()
    assert invite_data["message"] == "User invited successfully"
    assert "user_id" in invite_data
    assert "temporary_password" in invite_data
    assert "organization_id" in invite_data
    
    # Verify the user can login with temporary password
    login_response = client.post(
        "/auth/login",
        data={"username": new_username, "password": invite_data["temporary_password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200


def test_member_cannot_invite_users(client, db_session, existing_org_admin):
    """Test that members cannot invite users (admin only)"""
    # Create a member user in the same organization
    member_username = f"org_member_{uuid.uuid4().hex[:8]}"
    member_email = f"org_member_{uuid.uuid4().hex[:8]}@example.com"
    member_user = User(
        username=member_username,
        email=member_email,
        hashed_password=hash_password("member_password"),
        role=Role.MEMBER,
        organization_id=existing_org_admin.organization_id,
        is_active=True
    )
    db_session.add(member_user)
    db_session.commit()
    
    member_headers = get_auth_headers(client, member_username, "member_password")
    
    response = client.post(
        "/organizations/invite",
        json={
            "email": "should_not_work@example.com",
            "username": "should_not_work",
            "role": "MEMBER"
        },
        headers=member_headers,
    )
    assert response.status_code == 403  # Forbidden


def test_update_member_role(client, existing_org_admin, db_session):
    """Test updating a member's role (admin only)"""
    headers = get_auth_headers(client, existing_org_admin.username, "admin_password")
    
    # First invite a member
    new_user_email = f"role_test_{uuid.uuid4().hex[:8]}@example.com"
    new_username = f"role_test_{uuid.uuid4().hex[:8]}"
    
    invite_response = client.post(
        "/organizations/invite",
        json={
            "email": new_user_email,
            "username": new_username,
            "role": "MEMBER"
        },
        headers=headers,
    )
    assert invite_response.status_code == 200
    user_id = invite_response.json()["user_id"]
    
    # Update role to ADMIN
    response = client.put(
        f"/organizations/members/{user_id}/role",
        json={"role": "ADMIN"},
        headers=headers,
    )
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["role"] == "ADMIN"
    assert updated_user["username"] == new_username


def test_cannot_remove_last_admin(client, existing_org_admin):
    """Test that the last admin cannot change their own role or be removed"""
    headers = get_auth_headers(client, existing_org_admin.username, "admin_password")
    
    # Try to change own role to MEMBER
    response = client.put(
        f"/organizations/members/{existing_org_admin.id}/role",
        json={"role": "MEMBER"},
        headers=headers,
    )
    assert response.status_code == 400
    assert "last admin" in response.json()["detail"]
    
    # Try to remove self
    response = client.delete(
        f"/organizations/members/{existing_org_admin.id}",
        headers=headers,
    )
    assert response.status_code == 400
    assert "last admin" in response.json()["detail"]


def test_list_organization_members(client, existing_org_admin):
    """Test listing organization members"""
    headers = get_auth_headers(client, existing_org_admin.username, "admin_password")
    
    response = client.get("/organizations/members", headers=headers)
    assert response.status_code == 200
    members = response.json()
    assert len(members) >= 1
    # Admin should be in the list
    admin_found = any(member["username"] == existing_org_admin.username for member in members)
    assert admin_found


def test_remove_member_from_organization(client, existing_org_admin, db_session):
    """Test removing a member from organization"""
    headers = get_auth_headers(client, existing_org_admin.username, "admin_password")
    
    # First invite a member
    new_user_email = f"remove_test_{uuid.uuid4().hex[:8]}@example.com"
    new_username = f"remove_test_{uuid.uuid4().hex[:8]}"
    
    invite_response = client.post(
        "/organizations/invite",
        json={
            "email": new_user_email,
            "username": new_username,
            "role": "MEMBER"
        },
        headers=headers,
    )
    assert invite_response.status_code == 200
    user_id = invite_response.json()["user_id"]
    
    # Remove the member
    response = client.delete(
        f"/organizations/members/{user_id}",
        headers=headers,
    )
    assert response.status_code == 200
    removed_user = response.json()
    assert removed_user["is_active"] == False
    assert removed_user["username"] == new_username


def test_update_organization_details(client, existing_org_admin):
    """Test updating organization details (admin only)"""
    headers = get_auth_headers(client, existing_org_admin.username, "admin_password")
    
    new_name = f"Updated_Org_{uuid.uuid4().hex[:8]}"
    response = client.put(
        "/organizations/",
        json={"name": new_name},
        headers=headers,
    )
    assert response.status_code == 200
    updated_org = response.json()
    assert updated_org["name"] == new_name


def test_member_cannot_update_organization(client, db_session, existing_org_admin):
    """Test that members cannot update organization details"""
    # Create a member user
    member_username = f"update_test_member_{uuid.uuid4().hex[:8]}"
    member_email = f"update_test_member_{uuid.uuid4().hex[:8]}@example.com"
    member_user = User(
        username=member_username,
        email=member_email,
        hashed_password=hash_password("member_password"),
        role=Role.MEMBER,
        organization_id=existing_org_admin.organization_id,
        is_active=True
    )
    db_session.add(member_user)
    db_session.commit()
    
    member_headers = get_auth_headers(client, member_username, "member_password")
    
    response = client.put(
        "/organizations/",
        json={"name": "Should Not Work"},
        headers=member_headers,
    )
    assert response.status_code == 403  # Forbidden


def test_unauthorized_access_to_org_endpoints(client):
    """Test that unauthenticated requests are rejected"""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    # Try to create organization without auth
    response = client.post("/organizations/", json={"name": "Unauthorized"})
    assert response.status_code == 401
    
    # Try to get organization without auth
    response = client.get("/organizations/my")
    assert response.status_code == 401
    
    # Try to invite user without auth
    response = client.post("/organizations/invite", json={"email": "test@test.com", "username": "test", "role": "MEMBER"})
    assert response.status_code == 401
    
    # Try to update role without auth
    response = client.put(f"/organizations/members/{fake_uuid}/role", json={"role": "ADMIN"})
    assert response.status_code == 401
    
    # Try to remove member without auth
    response = client.delete(f"/organizations/members/{fake_uuid}")
    assert response.status_code == 401


def test_invite_duplicate_user_fails(client, existing_org_admin, db_session):
    """Test that inviting a user with existing email/username fails"""
    headers = get_auth_headers(client, existing_org_admin.username, "admin_password")
    
    # Try to invite with existing admin's email
    response = client.post(
        "/organizations/invite",
        json={
            "email": existing_org_admin.email,
            "username": "new_username",
            "role": "MEMBER"
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_validate_organization_name(client, standalone_user):
    """Test organization name validation"""
    headers = get_auth_headers(client, standalone_user.username, "standalone_password")
    
    # Try to create organization with empty name
    response = client.post(
        "/organizations/",
        json={"name": ""},
        headers=headers,
    )
    assert response.status_code == 422  # Validation error
