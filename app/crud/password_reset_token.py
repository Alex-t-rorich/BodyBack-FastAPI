# app/crud/password_reset_token.py
import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User

class CRUDPasswordResetToken(CRUDBase[PasswordResetToken, None, None]):
    def create_for_user(
        self, 
        db: Session, 
        *, 
        user_id: UUID,
        expires_in_hours: int = 24
    ) -> PasswordResetToken:
        """Create a password reset token for a user"""
        # Invalidate any existing tokens for this user
        db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.used == False
        ).update({"used": True})
        
        # Generate new token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        db_obj = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            used=False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_token(
        self, 
        db: Session, 
        *, 
        token: str
    ) -> Optional[PasswordResetToken]:
        """Get a password reset token by token string"""
        return db.query(self.model).filter(
            self.model.token == token
        ).first()
    
    def validate_token(
        self, 
        db: Session, 
        *, 
        token: str
    ) -> Optional[User]:
        """Validate a token and return the associated user if valid"""
        reset_token = self.get_by_token(db, token=token)
        
        if not reset_token:
            return None
        
        if not reset_token.is_valid:
            return None
        
        # Mark token as used
        reset_token.used = True
        db.commit()
        
        return reset_token.user
    
    def cleanup_expired(self, db: Session) -> int:
        """Delete expired tokens (cleanup task)"""
        result = db.query(self.model).filter(
            self.model.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        return result

password_reset_token_crud = CRUDPasswordResetToken(PasswordResetToken)