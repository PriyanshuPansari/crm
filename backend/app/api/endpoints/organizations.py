from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_active_user, require_admin
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
from app.models.user import User, Role
from app.models.organization import Organization

router = APIRouter()


@router.post("/", response_model=OrganizationOut)
def create_organization(
    org_in: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new organization. User becomes admin of the new organization."""
    if current_user.organization_id:
        raise HTTPException(
            status_code=400, 
            detail="User already belongs to an organization"
        )
    
    try:
        org = crud_organization.create_organization(db, org_in, current_user.id)
        return org
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my", response_model=OrganizationWithMembers)
def get_my_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's organization with members list"""
    if not current_user.organization_id:
        raise HTTPException(status_code=404, detail="User not in any organization")
    
    org = crud_organization.get_organization_by_id(db, current_user.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    members = crud_organization.get_organization_members(db, org.id)
    org_dict = {
        "id": org.id,
        "name": org.name,
        "created_at": org.created_at,
        "members": [
            {
                "id": member.id,
                "username": member.username,
                "email": member.email,
                "role": member.role,
                "is_active": member.is_active,
                "created_at": member.created_at
            }
            for member in members
        ]
    }
    return org_dict


@router.put("/", response_model=OrganizationOut)
def update_organization(
    org_in: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update organization details (admin only)"""
    org = crud_organization.get_organization_by_id(db, current_user.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    try:
        updated_org = crud_organization.update_organization(db, org, org_in)
        return updated_org
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invite", response_model=UserInviteResponse)
def invite_user(
    user_invite: UserInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Invite a user to the organization (admin only)"""
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="Admin not in any organization")
    
    try:
        user, temp_password = crud_organization.invite_user_to_organization(
            db, current_user.organization_id, user_invite
        )
        return UserInviteResponse(
            message="User invited successfully",
            user_id=user.id,
            organization_id=current_user.organization_id,
            temporary_password=temp_password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/members/{user_id}/role", response_model=OrganizationMemberOut)
def update_member_role(
    user_id: UUID,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a member's role in the organization (admin only)"""
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="Admin not in any organization")
    
    # Prevent admin from changing their own role if they're the only admin
    if user_id == current_user.id:
        admin_count = db.query(User).filter(
            User.organization_id == current_user.organization_id,
            User.role == Role.ADMIN,
            User.is_active == True
        ).count()
        
        if admin_count <= 1 and role_update.role != Role.ADMIN:
            raise HTTPException(
                status_code=400, 
                detail="Cannot remove admin role from the last admin in organization"
            )
    
    try:
        user = crud_organization.update_user_role(
            db, user_id, current_user.organization_id, role_update.role
        )
        return OrganizationMemberOut(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/members/{user_id}", response_model=OrganizationMemberOut)
def remove_member(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Remove a member from the organization (admin only)"""
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="Admin not in any organization")
    
    # Prevent admin from removing themselves if they're the only admin
    if user_id == current_user.id:
        admin_count = db.query(User).filter(
            User.organization_id == current_user.organization_id,
            User.role == Role.ADMIN,
            User.is_active == True
        ).count()
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=400, 
                detail="Cannot remove the last admin from organization"
            )
    
    try:
        user = crud_organization.remove_user_from_organization(
            db, user_id, current_user.organization_id
        )
        return OrganizationMemberOut(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/members", response_model=List[OrganizationMemberOut])
def list_organization_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all members of the current user's organization"""
    if not current_user.organization_id:
        raise HTTPException(status_code=404, detail="User not in any organization")
    
    members = crud_organization.get_organization_members(db, current_user.organization_id)
    return [
        OrganizationMemberOut(
            id=member.id,
            username=member.username,
            email=member.email,
            role=member.role,
            is_active=member.is_active,
            created_at=member.created_at
        )
        for member in members
    ]


@router.delete("/", response_model=OrganizationOut)
def delete_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete the organization and all associated data (admin only)"""
    org = crud_organization.get_organization_by_id(db, current_user.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Additional safety check - only allow if user is admin
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only organization admins can delete the organization")
    
    try:
        deleted_org = crud_organization.delete_organization(db, org)
        return deleted_org
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
