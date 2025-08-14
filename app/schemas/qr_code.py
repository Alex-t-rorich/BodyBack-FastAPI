# app/schemas/qr_code.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from uuid import UUID

from .user import UserResponse

class QRCodeBase(BaseModel):
    """Base schema with common QR code fields"""
    token: str
    
    @field_validator('token')
    @classmethod
    def validate_token(cls, v):
        """Validate token format and length"""
        if not v or not v.strip():
            raise ValueError('Token cannot be empty')
        if len(v) > 255:
            raise ValueError('Token must be 255 characters or less')
        return v.strip()

class QRCodeCreate(QRCodeBase):
    """Schema for creating a new QR code"""
    user_id: UUID

class QRCodeUpdate(BaseModel):
    """Schema for updating a QR code"""
    token: Optional[str] = None
    
    @field_validator('token')
    @classmethod
    def validate_token(cls, v):
        """Validate token format and length"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Token cannot be empty')
            if len(v) > 255:
                raise ValueError('Token must be 255 characters or less')
            return v.strip()
        return v

class QRCodeResponse(QRCodeBase):
    """Schema for QR code responses"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Include user information
    user: Optional[UserResponse] = None
    
    model_config = {'from_attributes': True}

class QRCodeSummary(BaseModel):
    """Schema for QR code summary (minimal info)"""
    id: UUID
    user_id: UUID
    token: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {'from_attributes': True}