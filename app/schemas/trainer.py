from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID

from .user import UserResponse

class TrainerBase(BaseModel):
    """Base schema with common trainer fields"""
    profile_picture_url: Optional[str] = None

class TrainerCreate(TrainerBase):
    """Schema for creating a new trainer"""
    user_id: UUID

class TrainerUpdate(BaseModel):
    """Schema for updating a trainer"""
    profile_picture_url: Optional[str] = None

class TrainerResponse(TrainerBase):
    """Schema for trainer responses"""
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    # Include user information
    user: UserResponse
    
    model_config = {'from_attributes': True}

class TrainerListResponse(BaseModel):
    """Schema for trainer list responses"""
    user_id: UUID
    profile_picture_url: Optional[str] = None
    created_at: datetime
    
    # Basic user info for lists
    user: UserResponse
    
    model_config = {'from_attributes': True}

class TrainerWithCustomersResponse(TrainerResponse):
    """Schema for trainer with their customers"""
    customers: List["CustomerListResponse"] = []
    
    model_config = {'from_attributes': True}

# Import CustomerListResponse after to avoid circular imports
from .customer import CustomerListResponse
TrainerWithCustomersResponse.model_rebuild()