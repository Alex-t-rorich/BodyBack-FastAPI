from .user import user_crud
from .customer import customer_crud
from .trainer import trainer_crud

# Export all CRUD operations for easy imports
__all__ = [
    "user_crud",
    "customer_crud", 
    "trainer_crud"
]