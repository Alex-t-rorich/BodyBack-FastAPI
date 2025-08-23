# app/api/auth.py
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.core.security import (
    create_token_for_user, 
    create_tokens_for_user,
    verify_refresh_token,
    verify_password, 
    get_password_hash
)
from app.crud.user import user_crud
from app.crud.password_reset_token import password_reset_token_crud
from app.models.user import User
from app.schemas.auth import (
    Token, 
    ChangePassword, 
    ForgotPassword, 
    ResetPassword,
    RefreshToken,
    MessageResponse
)
from app.schemas.user import UserLogin

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user and return JWT token"""
    # Authenticate user
    user = user_crud.authenticate(
        db, 
        email=user_credentials.email, 
        password=user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Get role name for token
    role_name = user.role.name if user.role else None
    
    # Create both access and refresh tokens
    access_token, refresh_token = create_tokens_for_user(
        user_id=user.id,
        email=user.email,
        role=role_name
    )
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
):
    """Refresh access token using a refresh token"""
    # Verify refresh token
    payload = verify_refresh_token(refresh_data.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from token payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is still active
    if not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Get role name for new token
    role_name = user.role.name if user.role else None
    
    # Create new access and refresh tokens
    access_token, new_refresh_token = create_tokens_for_user(
        user_id=user.id,
        email=user.email,
        role=role_name
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change the current user's password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Check that new password is different
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    hashed_password = get_password_hash(password_data.new_password)
    user_crud.update(db, db_obj=current_user, obj_in={"password_hash": hashed_password})
    
    return {"message": "Password changed successfully"}

@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout user. 
    Note: With JWT, we can't truly invalidate tokens server-side without maintaining a blacklist.
    This endpoint serves as a placeholder for client-side token removal.
    For production, consider implementing a token blacklist in Redis.
    """
    # In a production environment, you might want to:
    # 1. Add the token to a blacklist (Redis)
    # 2. Clear any server-side sessions
    # 3. Log the logout event
    
    return {"message": "Successfully logged out"}

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    forgot_data: ForgotPassword,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request a password reset token.
    In production, this would send an email with the reset link.
    """
    user = user_crud.get_by_email(db, email=forgot_data.email)
    
    # Always return success even if user doesn't exist (security best practice)
    message = "If an account exists with this email, a password reset link has been sent"
    
    if user and user_crud.is_active(user):
        # Create reset token in database
        reset_token = password_reset_token_crud.create_for_user(
            db, 
            user_id=user.id,
            expires_in_hours=24
        )
        
        # TODO: Add background task to send email
        # background_tasks.add_task(send_reset_email, email=user.email, token=reset_token.token)
        
        # For development, log the token
        logger.info(f"Password reset token generated for {user.email}: {reset_token.token}")
        print(f"Password reset token for {user.email}: {reset_token.token}")
    
    return {"message": message}

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: ResetPassword,
    db: Session = Depends(get_db)
):
    """
    Reset password using a reset token.
    """
    # Validate token and get user
    user = password_reset_token_crud.validate_token(db, token=reset_data.token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    hashed_password = get_password_hash(reset_data.new_password)
    user_crud.update(db, db_obj=user, obj_in={"password_hash": hashed_password})
    
    logger.info(f"Password reset successfully for user {user.email}")
    
    return {"message": "Password reset successfully"}