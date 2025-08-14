# app/models/session_tracking.py
from datetime import datetime, date
from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, DateTime, Date, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base

class SessionTracking(Base):
    __tablename__ = "session_tracking"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    trainer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    qr_code_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("qr_codes.id", ondelete="CASCADE"), nullable=False)
    session_volume_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("session_volumes.id", ondelete="CASCADE"), nullable=False)
    
    scan_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    session_date: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    trainer = relationship("User", back_populates="session_trackings")
    qr_code = relationship("QRCode", back_populates="session_trackings")
    session_volume = relationship("SessionVolume", back_populates="session_trackings")
    
    def __repr__(self):
        return f"<SessionTracking(id={self.id}, qr_code_id={self.qr_code_id}, trainer_id={self.trainer_id}, scan_timestamp={self.scan_timestamp})>"