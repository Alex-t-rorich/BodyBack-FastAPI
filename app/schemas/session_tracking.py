# app/schemas/session_tracking.py
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from .user import UserResponse
from .qr_code import QRCodeSummary
from .session_volume import SessionVolumeSummary

class SessionTrackingBase(BaseModel):
    """Base schema with common session tracking fields"""
    pass

class SessionTrackingCreate(SessionTrackingBase):
    """Schema for creating a new session tracking record"""
    trainer_id: UUID
    qr_code_id: UUID
    session_volume_id: UUID
    session_date: Optional[date] = None

class SessionTrackingUpdate(BaseModel):
    """Schema for updating a session tracking record"""
    session_date: Optional[date] = None

class SessionTrackingResponse(SessionTrackingBase):
    """Schema for session tracking responses"""
    id: UUID
    trainer_id: UUID
    qr_code_id: UUID
    session_volume_id: UUID
    scan_timestamp: datetime
    session_date: date
    created_at: datetime
    updated_at: datetime
    
    # Include related information
    trainer: Optional[UserResponse] = None
    qr_code: Optional[QRCodeSummary] = None
    session_volume: Optional[SessionVolumeSummary] = None
    
    model_config = {'from_attributes': True}

class SessionTrackingSummary(BaseModel):
    """Schema for session tracking summary (minimal info)"""
    id: UUID
    trainer_id: UUID
    qr_code_id: UUID
    session_volume_id: UUID
    scan_timestamp: datetime
    session_date: date
    
    model_config = {'from_attributes': True}

class SessionTrackingStats(BaseModel):
    """Schema for session tracking statistics"""
    total_scans: int = 0
    unique_days: int = 0
    first_scan: Optional[datetime] = None
    last_scan: Optional[datetime] = None
    
    model_config = {'from_attributes': True}