# app/crud/user.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from .base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email with role"""
        return (
            db.query(User)
            .options(joinedload(User.role))
            .filter(User.email == email)
            .first()
        )
    
    def get_by_role(self, db: Session, *, role_name: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role name"""
        return (
            db.query(User)
            .options(joinedload(User.role))
            .join(User.role)
            .filter(Role.name == role_name)
            .filter(User.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_trainers(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all trainers"""
        return self.get_by_role(db, role_name="Trainer", skip=skip, limit=limit)
    
    def get_customers(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all customers"""
        return self.get_by_role(db, role_name="Customer", skip=skip, limit=limit)
    
    def get_admins(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all admins"""
        return self.get_by_role(db, role_name="Admin", skip=skip, limit=limit)
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create user with hashed password and role"""
        create_data = obj_in.dict()
        create_data["password_hash"] = get_password_hash(create_data.pop("password"))
        role_name = create_data.pop("role", None)
        
        # Get role_id from role name
        if role_name:
            role = db.query(Role).filter(Role.name == role_name).first()
            if role:
                create_data["role_id"] = role.id
        
        # Create user with role_id
        db_obj = User(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def set_role(self, db: Session, *, user: User, role_name: str) -> User:
        """Set user's role"""
        role = db.query(Role).filter(Role.name == role_name).first()
        if role:
            user.role_id = role.id
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    def remove_role(self, db: Session, *, user: User) -> User:
        """Remove user's role"""
        user.role_id = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def update_password(self, db: Session, *, user: User, new_password: str) -> User:
        """Update user password"""
        from app.core.security import get_password_hash
        
        user.password_hash = get_password_hash(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        from app.core.security import verify_password
        
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.active and user.deleted_at is None
    
    def activate(self, db: Session, *, user: User) -> User:
        """Activate user"""
        user.active = True
        user.deleted_at = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def deactivate(self, db: Session, *, user: User) -> User:
        """Deactivate user"""
        user.active = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

user_crud = CRUDUser(User)