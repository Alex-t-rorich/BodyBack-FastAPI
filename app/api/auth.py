# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_token_for_user
from app.crud.user import user_crud
from app.schemas.auth import Token
from app.schemas.user import UserLogin

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
    
    # Create access token
    access_token = create_token_for_user(
        user_id=user.id,
        email=user.email,
        role=role_name
    )
    
    return {"access_token": access_token, "token_type": "bearer"}