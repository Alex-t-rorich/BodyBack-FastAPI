from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.models.trainer import Trainer
from app.models.customer import Customer
from app.models.user import User
from app.schemas.trainer import TrainerCreate, TrainerUpdate
from .base import CRUDBase

class CRUDTrainer(CRUDBase[Trainer, TrainerCreate, TrainerUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: UUID) -> Optional[Trainer]:
        """Get trainer by user ID"""
        return (
            db.query(Trainer)
            .options(joinedload(Trainer.user))
            .filter(Trainer.user_id == user_id)
            .first()
        )
    
    def get_with_customers(self, db: Session, *, trainer_id: UUID) -> Optional[Trainer]:
        """Get trainer with their customers"""
        trainer = (
            db.query(Trainer)
            .options(joinedload(Trainer.user))
            .filter(Trainer.user_id == trainer_id)
            .first()
        )
        
        if trainer:
            # Get customers for this trainer
            customers = (
                db.query(Customer)
                .options(joinedload(Customer.user))
                .filter(Customer.trainer_id == trainer_id)
                .filter(Customer.deleted_at.is_(None))
                .all()
            )
            # Manually add customers to avoid complex SQLAlchemy relationships
            trainer.customers = customers
            
        return trainer
    
    def get_all_with_customer_count(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Trainer]:
        """Get trainers with customer count"""
        trainers = (
            db.query(Trainer)
            .options(joinedload(Trainer.user))
            .filter(Trainer.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Add customer count to each trainer
        for trainer in trainers:
            trainer.customer_count = (
                db.query(Customer)
                .filter(Customer.trainer_id == trainer.user_id)
                .filter(Customer.deleted_at.is_(None))
                .count()
            )
        
        return trainers
    
    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Trainer]:
        """Get active trainers with user info"""
        return (
            db.query(Trainer)
            .options(joinedload(Trainer.user))
            .filter(Trainer.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_customers(self, db: Session, *, trainer_id: UUID, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get customers for a specific trainer"""
        return (
            db.query(Customer)
            .options(joinedload(Customer.user))
            .filter(Customer.trainer_id == trainer_id)
            .filter(Customer.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def has_customers(self, db: Session, *, trainer_id: UUID) -> bool:
        """Check if trainer has any customers"""
        return (
            db.query(Customer)
            .filter(Customer.trainer_id == trainer_id)
            .filter(Customer.deleted_at.is_(None))
            .count() > 0
        )
    
    def get_available_for_assignment(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Trainer]:
        """Get trainers available for customer assignment"""
        return (
            db.query(Trainer)
            .options(joinedload(Trainer.user))
            .filter(Trainer.deleted_at.is_(None))
            .join(User)
            .filter(User.active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

trainer_crud = CRUDTrainer(Trainer)