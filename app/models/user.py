# app/models/user.py
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    roles = Column(ARRAY(Text), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    phone_number = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="user", uselist=False)
    trainer = relationship("Trainer", back_populates="user", uselist=False)
    trained_customers = relationship("Customer", foreign_keys="Customer.trainer_id", back_populates="trainer")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', roles={self.roles})>"
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        return self.roles and role in self.roles
    
    def is_trainer(self) -> bool:
        """Check if user is a trainer"""
        return self.has_role("trainer")
    
    def is_customer(self) -> bool:
        """Check if user is a customer"""
        return self.has_role("customer")
    
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.has_role("admin")