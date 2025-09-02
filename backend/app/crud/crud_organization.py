from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.organization import Organization
from app.models.user import User, Role
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
    
    # Update the creator to be admin of this organization
    creator = db.query(User).filter(User.id == creator_id).first()
    if creator:
        creator.organization_id = org.id
        creator.role = Role.ADMIN
    
    db.commit()
    db.refresh(org)
    return org


def get_organization_by_id(db: Session, org_id: UUID) -> Organization | None:
    """Get organization by ID"""
    return db.query(Organization).filter(Organization.id == org_id).first()


def get_organizations_by_user(db: Session, user_id: UUID) -> List[Organization]:
    """Get organizations where user is a member"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.organization_id:
        return []
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    return [org] if org else []


def update_organization(db: Session, org: Organization, org_in: OrganizationUpdate) -> Organization:
    """Update organization details"""
    for field, value in org_in.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    db.commit()
    db.refresh(org)
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
        raise ValueError("User with this email or username already exists")
    
    # Create new user
    user = User(
        username=user_invite.username,
        email=user_invite.email,
        hashed_password=hash_password(temp_password),
        role=user_invite.role,
        organization_id=org_id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user, temp_password


def get_organization_members(db: Session, org_id: UUID) -> List[User]:
    """Get all members of an organization"""
    return db.query(User).filter(User.organization_id == org_id).all()


def update_user_role(db: Session, user_id: UUID, org_id: UUID, new_role: Role) -> User:
    """Update a user's role within an organization"""
    user = db.query(User).filter(
        User.id == user_id, 
        User.organization_id == org_id
    ).first()
    
    if not user:
        raise ValueError("User not found in organization")
    
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


def remove_user_from_organization(db: Session, user_id: UUID, org_id: UUID) -> User:
    """Remove a user from an organization"""
    user = db.query(User).filter(
        User.id == user_id, 
        User.organization_id == org_id
    ).first()
    
    if not user:
        raise ValueError("User not found in organization")
    
    # Remove from organization (set to None)
    user.organization_id = None
    user.is_active = False  # Deactivate user when removed from org
    db.commit()
    db.refresh(user)
    return user
