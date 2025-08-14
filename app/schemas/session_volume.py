# app/schemas/session_volume.py
from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, field_validator
from uuid import UUID

from .user import UserResponse

class SessionVolumeBase(BaseModel):
    """Base schema with common session volume fields"""
    period: date
    session_count: int = 0
    plans: Optional[str] = None
    notes: Optional[str] = None
    status: Literal["draft", "submitted", "read", "approved", "rejected"] = "draft"
    
    @field_validator('session_count')
    @classmethod
    def validate_session_count(cls, v):
        """Validate session count is non-negative"""
        if v < 0:
            raise ValueError('Session count cannot be negative')
        return v
    
    @field_validator('plans')
    @classmethod
    def validate_plans_length(cls, v):
        """Validate plans length"""
        if v and len(v) > 5000:
            raise ValueError('Plans must be 5000 characters or less')
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes_length(cls, v):
        """Validate notes length"""
        if v and len(v) > 5000:
            raise ValueError('Notes must be 5000 characters or less')
        return v

class SessionVolumeCreate(SessionVolumeBase):
    """Schema for creating a new session volume record"""
    trainer_id: UUID
    customer_id: UUID

class SessionVolumeUpdate(BaseModel):
    """Schema for updating a session volume record"""
    period: Optional[date] = None
    session_count: Optional[int] = None
    plans: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[Literal["draft", "submitted", "read", "approved", "rejected"]] = None
    
    @field_validator('session_count')
    @classmethod
    def validate_session_count(cls, v):
        """Validate session count is non-negative"""
        if v is not None and v < 0:
            raise ValueError('Session count cannot be negative')
        return v
    
    @field_validator('plans')
    @classmethod
    def validate_plans_length(cls, v):
        """Validate plans length"""
        if v and len(v) > 5000:
            raise ValueError('Plans must be 5000 characters or less')
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes_length(cls, v):
        """Validate notes length"""
        if v and len(v) > 5000:
            raise ValueError('Notes must be 5000 characters or less')
        return v

class SessionVolumeResponse(SessionVolumeBase):
    """Schema for session volume responses"""
    id: UUID
    trainer_id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    # Include customer and trainer information
    customer: Optional[UserResponse] = None
    trainer: Optional[UserResponse] = None
    
    # Computed properties
    is_active: bool = True
    is_draft: bool = True
    is_submitted: bool = False
    is_approved: bool = False
    is_rejected: bool = False
    
    model_config = {'from_attributes': True}

class SessionVolumeSummary(BaseModel):
    """Schema for session volume summary (minimal info)"""
    id: UUID
    trainer_id: UUID
    customer_id: UUID
    period: date
    session_count: int
    status: str
    has_plans: bool = False
    has_notes: bool = False
    
    model_config = {'from_attributes': True}

class SessionVolumeStatusUpdate(BaseModel):
    """Schema for updating session volume status"""
    status: Literal["draft", "submitted", "read", "approved", "rejected"]
    notes: Optional[str] = None
    
    @field_validator('notes')
    @classmethod
    def validate_notes_length(cls, v):
        """Validate notes length"""
        if v and len(v) > 500:
            raise ValueError('Notes must be 500 characters or less')
        return v