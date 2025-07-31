# app/models/trainer.py
from datetime import datetime
from sqlalchemy import Column, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

class Trainer(Base):
    __tablename__ = "trainers"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    profile_picture_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="trainer")
    
    def __repr__(self):
        return f"<Trainer(user_id={self.user_id})>"
    
    @property
    def is_active(self) -> bool:
        """Check if trainer is active (not soft deleted)"""
        return self.deleted_at is None