from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from uuid import UUID

from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.models.organization import Organization

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Alias for compatibility
get_current_active_user = require_active_user


def require_admin(current_user: User = Depends(require_active_user)) -> User:
    # This dependency is now deprecated for organization-specific operations
    # Use require_organization_admin instead for organization-specific admin checks
    # Keep this for backward compatibility with non-organization endpoints
    from app.models.user_organization import UserOrganization, UserOrganizationRole
    
    # Check if user is admin in any organization
    admin_in_any_org = any(
        uo.role == UserOrganizationRole.ADMIN 
        for uo in current_user.user_organizations
    )
    
    if not admin_in_any_org:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


def require_organization_member(org_id: UUID):
    """Dependency factory to check if user is a member of a specific organization"""
    def _require_organization_member(
        current_user: User = Depends(require_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        from app.models.user_organization import UserOrganization
        
        # Check if user is a member of the organization
        user_org = db.query(UserOrganization).filter(
            UserOrganization.user_id == current_user.id,
            UserOrganization.organization_id == org_id
        ).first()
        
        if not user_org:
            raise HTTPException(status_code=403, detail="Not a member of this organization")
        
        return current_user
    return _require_organization_member


def require_organization_admin(org_id: UUID):
    """Dependency factory to check if user is an admin of a specific organization"""
    def _require_organization_admin(
        current_user: User = Depends(require_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        from app.models.user_organization import UserOrganization, UserOrganizationRole
        
        # Check if user is an admin of the organization
        user_org = db.query(UserOrganization).filter(
            UserOrganization.user_id == current_user.id,
            UserOrganization.organization_id == org_id
        ).first()
        
        if not user_org:
            raise HTTPException(status_code=403, detail="Not a member of this organization")
            
        if user_org.role != UserOrganizationRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin privileges required for this organization")
        
        return current_user
    return _require_organization_admin
