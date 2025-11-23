# app/models/trainer.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base

class Trainer(Base):
    __tablename__ = "trainers"

    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="trainer")
    
    def __repr__(self):
        return f"<Trainer(user_id={self.user_id})>"
    
    @property
    def is_active(self) -> bool:
        """Check if trainer is active (not soft deleted)"""
        return self.deleted_at is None