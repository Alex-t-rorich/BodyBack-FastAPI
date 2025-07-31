from .base import Base
from .user import User
from .customer import Customer
from .trainer import Trainer

# Export all models for easy imports
__all__ = [
    "Base",
    "User", 
    "Customer",
    "Trainer"
]