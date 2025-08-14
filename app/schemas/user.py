# app/schemas/user.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, model_validator
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
    role: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        valid_roles = ['Admin', 'Trainer', 'Customer']
        if v not in valid_roles:
            raise ValueError(f'Invalid role: {v}. Must be one of {valid_roles}')
        return v

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    active: Optional[bool] = None
    role: Optional[str] = None
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v is not None:
            valid_roles = ['Admin', 'Trainer', 'Customer']
            if v not in valid_roles:
                raise ValueError(f'Invalid role: {v}. Must be one of {valid_roles}')
        return v

class UserResponse(UserBase):
    """Schema for user responses"""
    id: UUID
    role: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    @model_validator(mode='before')
    @classmethod
    def extract_role(cls, values):
        """Extract role name from Role object"""
        # Handle both dict and SQLAlchemy object
        if hasattr(values, 'role') and values.role:
            if hasattr(values.role, 'name'):
                # For SQLAlchemy objects, create a dict copy
                if hasattr(values, '__dict__'):
                    values_dict = {}
                    for key in ['id', 'email', 'first_name', 'last_name', 'phone_number', 'location', 'active', 'created_at', 'updated_at', 'deleted_at']:
                        values_dict[key] = getattr(values, key, None)
                    values_dict['role'] = values.role.name
                    return values_dict
        elif isinstance(values, dict) and 'role' in values and values['role']:
            if hasattr(values['role'], 'name'):
                values['role'] = values['role'].name
        return values
    
    model_config = {'from_attributes': True}

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserPasswordUpdate(BaseModel):
    """Schema for password updates"""
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v