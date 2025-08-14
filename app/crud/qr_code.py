# app/crud/qr_code.py
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
import secrets
import string

from app.models.qr_code import QRCode
from app.schemas.qr_code import QRCodeCreate, QRCodeUpdate
from .base import CRUDBase

class CRUDQRCode(CRUDBase[QRCode, QRCodeCreate, QRCodeUpdate]):
    def get_by_token(self, db: Session, *, token: str) -> Optional[QRCode]:
        """Get QR code by token"""
        return (
            db.query(QRCode)
            .options(joinedload(QRCode.user))
            .filter(QRCode.token == token)
            .first()
        )
    
    def get_by_user(self, db: Session, *, user_id: UUID) -> Optional[QRCode]:
        """Get QR code for a user (one-to-one relationship)"""
        return (
            db.query(QRCode)
            .options(joinedload(QRCode.user))
            .filter(QRCode.user_id == user_id)
            .first()
        )
    
    def generate_unique_token(self, db: Session, *, length: int = 32) -> str:
        """Generate a unique token for QR code"""
        while True:
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
            existing = db.query(QRCode).filter(QRCode.token == token).first()
            if not existing:
                return token
    
    def create_for_user(self, db: Session, *, user_id: UUID) -> QRCode:
        """Create a permanent QR code for a user"""
        # Check if user already has a QR code
        existing_qr = self.get_by_user(db, user_id=user_id)
        if existing_qr:
            return existing_qr
        
        token = self.generate_unique_token(db)
        qr_code = QRCode(
            user_id=user_id,
            token=token
        )
        
        db.add(qr_code)
        db.commit()
        db.refresh(qr_code)
        return qr_code

qr_code_crud = CRUDQRCode(QRCode)