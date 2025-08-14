# app/schemas/customer.py
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator
from uuid import UUID

from .user import UserResponse

class CustomerBase(BaseModel):
    """Base schema with common customer fields"""
    trainer_id: Optional[UUID] = None
    profile_picture_url: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = {}

class CustomerCreate(CustomerBase):
    """Schema for creating a new customer"""
    user_id: UUID
    
    @field_validator('profile_data')
    @classmethod
    def validate_profile_data(cls, v):
        if v is None:
            return {}
        return v

class CustomerUpdate(BaseModel):
    """Schema for updating a customer"""
    trainer_id: Optional[UUID] = None
    profile_picture_url: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None
    
    @field_validator('profile_data')
    @classmethod
    def validate_profile_data(cls, v):
        if v is None:
            return {}
        return v

class CustomerResponse(CustomerBase):
    """Schema for customer responses"""
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    # Include user information
    user: UserResponse
    trainer: Optional[UserResponse] = None
    
    model_config = {'from_attributes': True}

class CustomerListResponse(BaseModel):
    """Schema for customer list responses"""
    user_id: UUID
    trainer_id: Optional[UUID] = None
    profile_picture_url: Optional[str] = None
    created_at: datetime
    
    # Basic user info for lists
    user: UserResponse
    
    model_config = {'from_attributes': True}

class CustomerAssignTrainer(BaseModel):
    """Schema for assigning/unassigning trainer to customer"""
    trainer_id: Optional[UUID] = None