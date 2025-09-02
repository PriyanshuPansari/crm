from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.organization import Organization
from app.models.user import User
from app.models.user_organization import UserOrganization, UserOrganizationRole
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, UserInvite
from app.core.security import hash_password
from uuid import UUID
import secrets
import string


def create_organization(db: Session, org_in: OrganizationCreate, creator_id: UUID) -> Organization:
    """Create a new organization and make the creator an admin"""
    # Create organization
    org = Organization(name=org_in.name)
    db.add(org)
    db.flush()  # Get the ID without committing
    
    # Add the creator to this organization with admin role
    creator = db.query(User).filter(User.id == creator_id).first()
    if creator:
        user_org = UserOrganization(
            user_id=creator_id,
            organization_id=org.id,
            role=UserOrganizationRole.ADMIN
        )
        db.add(user_org)
    
    db.commit()
    db.refresh(org)
    return org


def get_organization_by_id(db: Session, org_id: UUID) -> Organization | None:
    """Get organization by ID"""
    return db.query(Organization).filter(Organization.id == org_id).first()


def get_organizations_by_user(db: Session, user_id: UUID) -> List[Organization]:
    """Get organizations where user is a member"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    return user.organizations


def update_organization(db: Session, org: Organization, org_in: OrganizationUpdate) -> Organization:
    """Update organization details"""
    for field, value in org_in.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    db.commit()
    return org


def delete_organization(db: Session, org: Organization) -> Organization:
    """Delete organization and all associated data"""
    db.delete(org)
    db.commit()
    return org


def invite_user_to_organization(
    db: Session, 
    org_id: UUID, 
    user_invite: UserInvite
) -> tuple[User, str]:
    """Invite a user to an organization with a temporary password"""
    # Generate temporary password
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_invite.email) | (User.username == user_invite.username)
    ).first()
    
    if existing_user:
        # Check if user is already in this organization
        existing_membership = db.query(UserOrganization).filter(
            UserOrganization.user_id == existing_user.id,
            UserOrganization.organization_id == org_id
        ).first()
        
        if existing_membership:
            return existing_user, "User already in organization"
        
        # Add existing user to organization with specified role
        user_org = UserOrganization(
            user_id=existing_user.id,
            organization_id=org_id,
            role=UserOrganizationRole(user_invite.role)
        )
        db.add(user_org)
        db.commit()
        db.refresh(existing_user)
        return existing_user, "User added to organization"
    
    # Create new user
    user = User(
        username=user_invite.username,
        email=user_invite.email,
        hashed_password=hash_password(temp_password),
        is_active=True
    )
    db.add(user)
    db.flush()
    
    # Add user to organization with specified role
    user_org = UserOrganization(
        user_id=user.id,
        organization_id=org_id,
        role=UserOrganizationRole(user_invite.role)
    )
    db.add(user_org)
    
    db.commit()
    db.refresh(user)
    
    return user, temp_password


def get_organization_members(db: Session, org_id: UUID) -> List[dict]:
    """Get all members of an organization with their roles"""
    user_orgs = db.query(UserOrganization).filter(
        UserOrganization.organization_id == org_id
    ).all()
    
    members = []
    for user_org in user_orgs:
        user = user_org.user
        members.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user_org.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "joined_at": user_org.joined_at
        })
    
    return members


def update_user_role(db: Session, user_id: UUID, org_id: UUID, new_role: UserOrganizationRole) -> User:
    """Update a user's role within an organization"""
    user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == user_id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if not user_org:
        raise ValueError("User not found in organization")
    
    user_org.role = new_role
    db.commit()
    db.refresh(user_org)
    return user_org.user


def remove_user_from_organization(db: Session, user_id: UUID, org_id: UUID) -> User:
    """Remove a user from an organization"""
    user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == user_id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if not user_org:
        raise ValueError("User not found in organization")
    
    user = user_org.user
    
    # Remove the user-organization relationship
    db.delete(user_org)
    
    # If user has no organizations left, deactivate them
    remaining_orgs = db.query(UserOrganization).filter(
        UserOrganization.user_id == user_id
    ).count()
    
    if remaining_orgs == 0:
        user.is_active = False
    
    db.commit()
    db.refresh(user)
    return user


def add_user_to_organization(db: Session, user_id: UUID, org_id: UUID, role: UserOrganizationRole = UserOrganizationRole.MEMBER) -> User:
    """Add an existing user to an organization"""
    user = db.query(User).filter(User.id == user_id).first()
    org = db.query(Organization).filter(Organization.id == org_id).first()
    
    if not user or not org:
        raise ValueError("User or organization not found")
    
    # Check if user is already in organization
    existing = db.query(UserOrganization).filter(
        UserOrganization.user_id == user_id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if existing:
        raise ValueError("User is already a member of this organization")
    
    # Create new user-organization relationship
    user_org = UserOrganization(
        user_id=user_id,
        organization_id=org_id,
        role=role
    )
    db.add(user_org)
    user.is_active = True  # Activate user when added to org
    db.commit()
    db.refresh(user)
    return user


def get_user_role_in_organization(db: Session, user_id: UUID, org_id: UUID) -> UserOrganizationRole | None:
    """Get a user's role in a specific organization"""
    user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == user_id,
        UserOrganization.organization_id == org_id
    ).first()
    
    return user_org.role if user_org else None


def is_user_admin_in_organization(db: Session, user_id: UUID, org_id: UUID) -> bool:
    """Check if a user is an admin in a specific organization"""
    role = get_user_role_in_organization(db, user_id, org_id)
    return role == UserOrganizationRole.ADMIN
