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
    LoginResponse,
    ChangePassword, 
    ForgotPassword, 
    ResetPassword,
    RefreshToken,
    MessageResponse
)
from app.schemas.user import UserLogin

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user and return JWT token"""
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

    if not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive or suspended"
        )

    role_name = user.role.name if user.role else None
    access_token, refresh_token = create_tokens_for_user(
        user_id=user.id,
        email=user.email,
        role=role_name
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "email": user.email,
        "role": role_name,
        "first_name": user.first_name,
        "last_name": user.last_name
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
):
    """Refresh access token using a refresh token"""
    payload = verify_refresh_token(refresh_data.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    role_name = user.role.name if user.role else None
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
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    hashed_password = get_password_hash(password_data.new_password)
    user_crud.update(db, db_obj=current_user, obj_in={"password_hash": hashed_password})
    
    return {"message": "Password changed successfully"}

@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """Logout user"""
    return {"message": "Successfully logged out"}

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    forgot_data: ForgotPassword,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request a password reset token"""
    user = user_crud.get_by_email(db, email=forgot_data.email)

    message = "If an account exists with this email, a password reset link has been sent"
    
    if user and user_crud.is_active(user):
        reset_token = password_reset_token_crud.create_for_user(
            db,
            user_id=user.id,
            expires_in_hours=24
        )
        logger.info(f"Password reset token generated for {user.email}: {reset_token.token}")
        print(f"Password reset token for {user.email}: {reset_token.token}")
    
    return {"message": message}

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: ResetPassword,
    db: Session = Depends(get_db)
):
    """Reset password using a reset token"""
    user = password_reset_token_crud.validate_token(db, token=reset_data.token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    hashed_password = get_password_hash(reset_data.new_password)
    user_crud.update(db, db_obj=user, obj_in={"password_hash": hashed_password})
    logger.info(f"Password reset successfully for user {user.email}")
    
    return {"message": "Password reset successfully"}