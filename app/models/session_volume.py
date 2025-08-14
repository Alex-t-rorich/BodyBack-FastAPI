# app/models/session_volume.py
from datetime import datetime, date
from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, Integer, Text, DateTime, Date, func, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base

class SessionVolume(Base):
    __tablename__ = "session_volumes"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    trainer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    period: Mapped[date] = mapped_column(Date, nullable=False)
    session_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    plans: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Add check constraint for status
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'submitted', 'read', 'approved', 'rejected')", name="session_volumes_status_check"),
    )
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], back_populates="session_volumes_as_customer")
    trainer = relationship("User", foreign_keys=[trainer_id], back_populates="session_volumes_as_trainer")
    session_trackings = relationship("SessionTracking", back_populates="session_volume", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SessionVolume(id={self.id}, customer_id={self.customer_id}, trainer_id={self.trainer_id}, period={self.period}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if session volume record is active (not soft deleted)"""
        return self.deleted_at is None
    
    @property
    def is_draft(self) -> bool:
        """Check if session volume is in draft status"""
        return self.status == "draft"
    
    @property
    def is_submitted(self) -> bool:
        """Check if session volume has been submitted"""
        return self.status in ["submitted", "read", "approved", "rejected"]
    
    @property
    def is_approved(self) -> bool:
        """Check if session volume has been approved"""
        return self.status == "approved"
    
    @property
    def is_rejected(self) -> bool:
        """Check if session volume has been rejected"""
        return self.status == "rejected"
    
    def submit(self):
        """Submit the session volume to customer"""
        if self.status == "draft":
            self.status = "submitted"
    
    def mark_as_read(self):
        """Mark the session volume as read by customer"""
        if self.status == "submitted":
            self.status = "read"
    
    def approve(self):
        """Approve the session volume"""
        if self.status in ["submitted", "read"]:
            self.status = "approved"
    
    def reject(self):
        """Reject the session volume"""
        if self.status in ["submitted", "read"]:
            self.status = "rejected"
    
    def reopen(self):
        """Reopen a rejected volume back to draft"""
        if self.status == "rejected":
            self.status = "draft"