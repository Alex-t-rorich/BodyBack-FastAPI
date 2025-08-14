# app/schemas/profile.py
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator
from uuid import UUID

from .user import UserResponse

class ProfileBase(BaseModel):
    """Base schema with common profile fields"""
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    emergency_contact: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}
    
    @field_validator('bio')
    @classmethod
    def validate_bio_length(cls, v):
        """Validate bio length"""
        if v and len(v) > 1000:
            raise ValueError('Bio must be 1000 characters or less')
        return v
    
    @field_validator('profile_picture_url')
    @classmethod
    def validate_profile_picture_url(cls, v):
        """Basic URL validation for profile picture"""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Profile picture URL must start with http:// or https://')
        return v
    
    @field_validator('preferences', mode='before')
    @classmethod
    def validate_preferences(cls, v):
        """Validate preferences structure"""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError('Preferences must be a dictionary')
        return v

class ProfileCreate(ProfileBase):
    """Schema for creating a new profile"""
    user_id: UUID

class ProfileUpdate(BaseModel):
    """Schema for updating a profile"""
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    emergency_contact: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}
    
    @field_validator('bio')
    @classmethod
    def validate_bio_length(cls, v):
        """Validate bio length"""
        if v and len(v) > 1000:
            raise ValueError('Bio must be 1000 characters or less')
        return v
    
    @field_validator('profile_picture_url')
    @classmethod
    def validate_profile_picture_url(cls, v):
        """Basic URL validation for profile picture"""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Profile picture URL must start with http:// or https://')
        return v
    
    @field_validator('preferences', mode='before')
    @classmethod
    def validate_preferences(cls, v):
        """Validate preferences structure"""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError('Preferences must be a dictionary')
        return v

class ProfileResponse(ProfileBase):
    """Schema for profile responses"""
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Include user information
    user: UserResponse
    
    model_config = {'from_attributes': True}

class ProfileSummary(BaseModel):
    """Schema for profile summary (minimal info)"""
    user_id: UUID
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    has_emergency_contact: bool = False
    is_complete: bool = False
    
    model_config = {'from_attributes': True}

class PreferenceUpdate(BaseModel):
    """Schema for updating a single preference"""
    key: str
    value: Any
    
    @field_validator('key')
    @classmethod
    def validate_key(cls, v):
        """Validate preference key"""
        if not v or not v.strip():
            raise ValueError('Preference key cannot be empty')
        if len(v) > 100:
            raise ValueError('Preference key must be 100 characters or less')
        return v.strip()