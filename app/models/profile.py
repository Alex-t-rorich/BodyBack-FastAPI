# app/models/profile.py
from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from sqlalchemy import Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
import uuid

from .base import Base

class Profile(Base):
    __tablename__ = "profiles"
    
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    profile_picture_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferences: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<Profile(user_id={self.user_id}, bio_length={len(self.bio) if self.bio else 0})>"
    
    @property
    def is_complete(self) -> bool:
        """Check if profile has essential information"""
        return bool(self.bio and self.profile_picture_url)
    
    def has_emergency_contact(self) -> bool:
        """Check if profile has emergency contact information"""
        return bool(self.emergency_contact)
    
    def get_preference(self, key: str, default=None):
        """Get a specific preference value"""
        if not self.preferences:
            return default
        return self.preferences.get(key, default)
    
    def set_preference(self, key: str, value):
        """Set a specific preference value"""
        if not self.preferences:
            self.preferences = {}
        self.preferences[key] = value