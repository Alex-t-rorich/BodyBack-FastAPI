# app/core/auth.py
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.crud.user import user_crud
from app.models.user import User

# Security scheme for bearer token
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the token
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    
    # Get user ID from token
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception
    
    # Get user from database
    user = user_crud.get(db, id=user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not user_crud.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

def require_role(required_role: str):
    """Dependency factory for role-based access control"""
    async def role_dependency(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_dependency

# Convenience dependencies for common roles
require_admin = require_role("Admin")
require_trainer = require_role("Trainer")
require_customer = require_role("Customer")

# Dependency for trainer or admin access
async def require_trainer_or_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require trainer or admin role"""
    if not (current_user.has_role("Trainer") or current_user.has_role("Admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trainer or Admin access required"
        )
    return current_user