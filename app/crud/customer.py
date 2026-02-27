from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.models.customer import Customer
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerUpdate
from .base import CRUDBase

class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: UUID) -> Optional[Customer]:
        """Get customer by user ID"""
        return (
            db.query(Customer)
            .options(joinedload(Customer.user), joinedload(Customer.trainer))
            .filter(Customer.user_id == user_id)
            .first()
        )
    
    def get_by_trainer_id(self, db: Session, *, trainer_id: UUID, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get customers by trainer ID"""
        return (
            db.query(Customer)
            .options(joinedload(Customer.user), joinedload(Customer.trainer))
            .filter(Customer.trainer_id == trainer_id)
            .filter(Customer.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_without_trainer(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get customers without assigned trainer"""
        return (
            db.query(Customer)
            .options(joinedload(Customer.user))
            .filter(Customer.trainer_id.is_(None))
            .filter(Customer.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_with_trainer(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get customers with assigned trainer"""
        return (
            db.query(Customer)
            .options(joinedload(Customer.user), joinedload(Customer.trainer))
            .filter(Customer.trainer_id.isnot(None))
            .filter(Customer.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def assign_trainer(self, db: Session, *, customer_id: UUID, trainer_id: UUID) -> Optional[Customer]:
        """Assign trainer to customer"""
        customer = db.query(Customer).filter(Customer.user_id == customer_id).first()
        if customer:
            customer.trainer_id = trainer_id
            db.add(customer)
            db.commit()
            db.refresh(customer)
        return customer
    
    def unassign_trainer(self, db: Session, *, customer_id: UUID) -> Optional[Customer]:
        """Remove trainer from customer"""
        customer = db.query(Customer).filter(Customer.user_id == customer_id).first()
        if customer:
            customer.trainer_id = None
            db.add(customer)
            db.commit()
            db.refresh(customer)
        return customer
    
    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get active customers with user and trainer info"""
        return (
            db.query(Customer)
            .options(joinedload(Customer.user), joinedload(Customer.trainer))
            .filter(Customer.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update_profile_data(self, db: Session, *, customer: Customer, profile_data: dict) -> Customer:
        """Update customer profile data"""
        customer.profile_data = profile_data
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    
    def count_by_trainer(self, db: Session, *, trainer_id: UUID) -> int:
        """Count customers for a specific trainer"""
        return (
            db.query(Customer)
            .filter(Customer.trainer_id == trainer_id)
            .filter(Customer.deleted_at.is_(None))
            .count()
        )

customer_crud = CRUDCustomer(Customer)