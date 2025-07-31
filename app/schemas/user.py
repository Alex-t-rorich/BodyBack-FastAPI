# app/schemas/user.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from uuid import UUID

class UserBase(BaseModel):
    """Base schema with common user fields"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    active: bool = True

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str
    roles: List[str]
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('roles')
    def validate_roles(cls, v):
        valid_roles = ['admin', 'trainer', 'customer']
        if not v:
            raise ValueError('At least one role must be specified')
        for role in v:
            if role not in valid_roles:
                raise ValueError(f'Invalid role: {role}. Must be one of {valid_roles}')
        return v

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    active: Optional[bool] = None
    roles: Optional[List[str]] = None
    
    @validator('roles')
    def validate_roles(cls, v):
        if v is not None:
            valid_roles = ['admin', 'trainer', 'customer']
            for role in v:
                if role not in valid_roles:
                    raise ValueError(f'Invalid role: {role}. Must be one of {valid_roles}')
        return v

class UserResponse(UserBase):
    """Schema for user responses"""
    id: UUID
    roles: List[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserPasswordUpdate(BaseModel):
    """Schema for password updates"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v