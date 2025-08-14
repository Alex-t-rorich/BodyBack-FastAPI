# app/models/user.py
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    first_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    role_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    profile = relationship("Profile", back_populates="user", uselist=False)
    customer = relationship("Customer", foreign_keys="Customer.user_id", back_populates="user", uselist=False)
    trainer = relationship("Trainer", back_populates="user", uselist=False)
    trained_customers = relationship("Customer", foreign_keys="Customer.trainer_id", back_populates="trainer")
    
    # Session management relationships
    qr_code = relationship("QRCode", back_populates="user", uselist=False, cascade="all, delete-orphan")
    session_trackings = relationship("SessionTracking", foreign_keys="SessionTracking.trainer_id", back_populates="trainer", cascade="all, delete-orphan")
    session_volumes_as_customer = relationship("SessionVolume", foreign_keys="SessionVolume.customer_id", back_populates="customer", cascade="all, delete-orphan")
    session_volumes_as_trainer = relationship("SessionVolume", foreign_keys="SessionVolume.trainer_id", back_populates="trainer", cascade="all, delete-orphan")
    
    def __repr__(self):
        role_name = self.role.name if self.role else 'No Role'
        return f"<User(id={self.id}, email='{self.email}', role={role_name})>"
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    @property
    def role_name(self) -> Optional[str]:
        """Get role name"""
        return self.role.name if self.role else None
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        return bool(self.role and self.role.name == role_name)
    
    def is_trainer(self) -> bool:
        """Check if user is a trainer"""
        return self.has_role("Trainer")
    
    def is_customer(self) -> bool:
        """Check if user is a customer"""
        return self.has_role("Customer")
    
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.has_role("Admin")