from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_active_user, require_admin
from app.models.user_organization import UserOrganization, UserOrganizationRole
from app.schemas.organization import (
    OrganizationCreate, 
    OrganizationUpdate, 
    OrganizationOut, 
    OrganizationWithMembers,
    UserInvite, 
    UserInviteResponse, 
    UserRoleUpdate,
    OrganizationMemberOut
)
from app.crud import crud_organization
from app.models.user import User
from app.models.organization import Organization

router = APIRouter()


@router.post("/", response_model=OrganizationOut)
def create_organization(
    org_in: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new organization. User becomes admin of the new organization."""
    try:
        org = crud_organization.create_organization(db, org_in, current_user.id)
        return org
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my", response_model=List[OrganizationWithMembers])
def get_my_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's organizations with members list"""
    user_orgs = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id
    ).all()
    
    if not user_orgs:
        return []
    
    organizations_with_members = []
    for user_org in user_orgs:
        org = user_org.organization
        members = crud_organization.get_organization_members(db, org.id)
        
        org_dict = {
            "id": org.id,
            "name": org.name,
            "created_at": org.created_at,
            "user_role": user_org.role,  # Add user's role in this organization
            "members": members
        }
        organizations_with_members.append(org_dict)
    
    return organizations_with_members


@router.get("/{org_id}", response_model=OrganizationWithMembers)
def get_organization(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get organization details and members (for organization members only)"""
    org = crud_organization.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if current user is member of this organization
    user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if not user_org:
        raise HTTPException(status_code=403, detail="You are not a member of this organization")
    
    members = crud_organization.get_organization_members(db, org.id)
    return {
        "id": org.id,
        "name": org.name,
        "created_at": org.created_at,
        "user_role": user_org.role,  # Add user's role in this organization
        "members": members
    }


@router.put("/{org_id}", response_model=OrganizationOut)
def update_organization(
    org_id: UUID,
    org_in: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update organization details (admin only)"""
    org = crud_organization.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if user is admin of this organization
    user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if not user_org or user_org.role != UserOrganizationRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin privileges required for this organization")
    
    try:
        updated_org = crud_organization.update_organization(db, org, org_in)
        return updated_org
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{org_id}/invite", response_model=UserInviteResponse)
def invite_user(
    org_id: UUID,
    user_invite: UserInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Invite a user to the organization (admin only)"""
    org = crud_organization.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if user is admin of this organization
    user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if not user_org or user_org.role != UserOrganizationRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin privileges required for this organization")
    
    try:
        user, temp_password = crud_organization.invite_user_to_organization(
            db, org_id, user_invite
        )
        return UserInviteResponse(
            message="User invited successfully",
            user_id=user.id,
            organization_id=org_id,
            temporary_password=temp_password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{org_id}/members/{user_id}/role", response_model=OrganizationMemberOut)
def update_member_role(
    org_id: UUID,
    user_id: UUID,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a member's role in the organization (admin only)"""
    org = crud_organization.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if current user is admin of this organization
    current_user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if not current_user_org or current_user_org.role != UserOrganizationRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin privileges required for this organization")
    
    # Prevent admin from changing their own role if they're the only admin
    if user_id == current_user.id:
        admin_count = len([
            uo for uo in org.user_organizations 
            if uo.role == UserOrganizationRole.ADMIN and uo.user.is_active
        ])
        
        if admin_count <= 1 and role_update.role != UserOrganizationRole.ADMIN:
            raise HTTPException(
                status_code=400, 
                detail="Cannot remove admin role from the last admin in organization"
            )
    
    try:
        user = crud_organization.update_user_role(
            db, user_id, org_id, UserOrganizationRole(role_update.role)
        )
        
        # Get the updated user's role in this organization
        updated_user_org = db.query(UserOrganization).filter(
            UserOrganization.user_id == user_id,
            UserOrganization.organization_id == org_id
        ).first()
        
        return OrganizationMemberOut(
            id=user.id,
            username=user.username,
            email=user.email,
            role=updated_user_org.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{org_id}/members/{user_id}", response_model=OrganizationMemberOut)
def remove_member(
    org_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove a member from the organization (admin only)"""
    org = crud_organization.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if current user is admin of this organization
    current_user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if not current_user_org or current_user_org.role != UserOrganizationRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin privileges required for this organization")
    
    # Prevent admin from removing themselves if they're the only admin
    if user_id == current_user.id:
        admin_count = len([
            uo for uo in org.user_organizations 
            if uo.role == UserOrganizationRole.ADMIN and uo.user.is_active
        ])
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=400, 
                detail="Cannot remove the last admin from organization"
            )
    
    try:
        user = crud_organization.remove_user_from_organization(
            db, user_id, org_id
        )
        
        # For the removed user, we'll return their info with a default role
        # since they're no longer in the organization
        return OrganizationMemberOut(
            id=user.id,
            username=user.username,
            email=user.email,
            role=UserOrganizationRole.MEMBER,  # Default role since they're removed
            is_active=user.is_active,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{org_id}/members", response_model=List[OrganizationMemberOut])
def list_organization_members(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all members of the specified organization"""
    org = crud_organization.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if user is a member of this organization
    user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if not user_org:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    members = crud_organization.get_organization_members(db, org_id)
    return [
        OrganizationMemberOut(
            id=member["id"],
            username=member["username"],
            email=member["email"],
            role=member["role"],
            is_active=member["is_active"],
            created_at=member["created_at"]
        )
        for member in members
    ]


@router.delete("/{org_id}", response_model=OrganizationOut)
def delete_organization(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete the organization and all associated data (admin only)"""
    org = crud_organization.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if current user is admin of this organization
    user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if not user_org or user_org.role != UserOrganizationRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin privileges required for this organization")
    
    try:
        deleted_org = crud_organization.delete_organization(db, org)
        return deleted_org
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{org_id}/members/{user_id}", response_model=OrganizationMemberOut)
def add_user_to_organization(
    org_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add an existing user to the organization (admin only)"""
    org = crud_organization.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if current user is admin of this organization
    user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == org_id
    ).first()
    
    if not user_org or user_org.role != UserOrganizationRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin privileges required for this organization")
    
    try:
        user = crud_organization.add_user_to_organization(db, user_id, org_id)
        
        # Get the user's role in this organization
        added_user_org = db.query(UserOrganization).filter(
            UserOrganization.user_id == user_id,
            UserOrganization.organization_id == org_id
        ).first()
        
        return OrganizationMemberOut(
            id=user.id,
            username=user.username,
            email=user.email,
            role=added_user_org.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
