# app/models/customer.py
from datetime import datetime
from sqlalchemy import Column, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base

class Customer(Base):
    __tablename__ = "customers"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    profile_picture_url = Column(Text, nullable=True)
    profile_data = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="customer")
    trainer = relationship("User", foreign_keys=[trainer_id], back_populates="trained_customers")
    
    def __repr__(self):
        return f"<Customer(user_id={self.user_id}, trainer_id={self.trainer_id})>"
    
    @property
    def is_active(self) -> bool:
        """Check if customer is active (not soft deleted)"""
        return self.deleted_at is None
    
    def has_trainer(self) -> bool:
        """Check if customer has an assigned trainer"""
        return self.trainer_id is not None