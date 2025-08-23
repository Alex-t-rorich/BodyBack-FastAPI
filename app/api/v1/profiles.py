# app/api/profiles.py
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.core.config import settings
from app.crud.profile import profile_crud
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdate, ProfileCreate

router = APIRouter()

@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    profile = profile_crud.get_by_user_id(db, user_id=current_user.id)
    
    if not profile:
        # Create a default profile if it doesn't exist
        profile = profile_crud.create_for_user(
            db, 
            user_id=current_user.id,
            obj_in=ProfileCreate(
                user_id=current_user.id,
                bio=None,
                profile_picture_url=None,
                emergency_contact=None,
                preferences={}
            )
        )
    
    return profile

@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    profile = profile_crud.get_by_user_id(db, user_id=current_user.id)
    
    if not profile:
        # Create profile if it doesn't exist
        profile = profile_crud.create_for_user(
            db,
            user_id=current_user.id,
            obj_in=ProfileCreate(
                user_id=current_user.id,
                **profile_update.model_dump()
            )
        )
    else:
        # Update existing profile
        profile = profile_crud.update(db, db_obj=profile, obj_in=profile_update)
    
    return profile

@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific user's profile.
    Regular users can only view their own profile.
    Trainers and Admins can view any profile.
    """
    # Check permissions
    if (user_id != current_user.id and 
        not current_user.has_role("Admin") and 
        not current_user.has_role("Trainer")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this profile"
        )
    
    # Check if user exists
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    profile = profile_crud.get_by_user_id(db, user_id=user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found for this user"
        )
    
    return profile

@router.post("/upload-picture", response_model=ProfileResponse)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a profile picture.
    Accepts image files (jpg, jpeg, png, gif).
    Max file size is controlled by MAX_FILE_SIZE_MB in settings.
    """
    # Validate file type
    allowed_extensions = ["jpg", "jpeg", "png", "gif"]
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (if MAX_FILE_SIZE_MB is set)
    if hasattr(settings, 'MAX_FILE_SIZE_MB'):
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
        
        # Read file content to check size
        contents = await file.read()
        if len(contents) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Reset file pointer
        await file.seek(0)
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR if hasattr(settings, 'UPLOAD_DIR') else "uploads")
    profile_pics_dir = upload_dir / "profile_pictures"
    profile_pics_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    import uuid
    unique_filename = f"{current_user.id}_{uuid.uuid4()}.{file_extension}"
    file_path = profile_pics_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    finally:
        file.file.close()
    
    # Update profile with file URL
    # In production, this would be a CDN URL or proper static file serving URL
    file_url = f"/static/profile_pictures/{unique_filename}"
    
    profile = profile_crud.get_by_user_id(db, user_id=current_user.id)
    
    if not profile:
        # Create profile with picture
        profile = profile_crud.create_for_user(
            db,
            user_id=current_user.id,
            obj_in=ProfileCreate(
                user_id=current_user.id,
                profile_picture_url=file_url,
                bio=None,
                emergency_contact=None,
                preferences={}
            )
        )
    else:
        # Delete old picture file if it exists
        if profile.profile_picture_url:
            old_filename = profile.profile_picture_url.split("/")[-1]
            old_file_path = profile_pics_dir / old_filename
            if old_file_path.exists():
                try:
                    old_file_path.unlink()
                except Exception:
                    pass  # Ignore errors when deleting old file
        
        # Update profile with new picture URL
        profile = profile_crud.update_profile_picture(
            db, 
            profile=profile, 
            picture_url=file_url
        )
    
    return profile

@router.delete("/picture")
async def delete_profile_picture(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete the current user's profile picture.
    This removes the file and clears the URL from the profile.
    """
    profile = profile_crud.get_by_user_id(db, user_id=current_user.id)
    
    if not profile or not profile.profile_picture_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile picture to delete"
        )
    
    # Delete the file
    upload_dir = Path(settings.UPLOAD_DIR if hasattr(settings, 'UPLOAD_DIR') else "uploads")
    profile_pics_dir = upload_dir / "profile_pictures"
    
    filename = profile.profile_picture_url.split("/")[-1]
    file_path = profile_pics_dir / filename
    
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            # Log error but continue to clear the URL from database
            print(f"Error deleting file: {e}")
    
    # Clear the URL from the profile
    profile = profile_crud.update_profile_picture(
        db,
        profile=profile,
        picture_url=None
    )
    
    return {"message": "Profile picture deleted successfully"}