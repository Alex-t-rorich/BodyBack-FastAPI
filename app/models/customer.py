# app/models/customer.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from .base import Base

class Customer(Base):
    __tablename__ = "customers"

    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    trainer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    profile_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
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