# app/schemas/__init__.py
from .user import UserCreate, UserUpdate, UserResponse, UserBase
from .customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerBase
from .trainer import TrainerCreate, TrainerUpdate, TrainerResponse, TrainerBase

# Export all schemas for easy imports
__all__ = [
    # User schemas
    "UserBase",
    "UserCreate", 
    "UserUpdate",
    "UserResponse",
    
    # Customer schemas
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate", 
    "CustomerResponse",
    
    # Trainer schemas
    "TrainerBase",
    "TrainerCreate",
    "TrainerUpdate",
    "TrainerResponse"
]