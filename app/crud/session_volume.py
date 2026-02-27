from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from uuid import UUID
from datetime import date

from app.models.session_volume import SessionVolume
from app.models.user import User
from app.schemas.session_volume import SessionVolumeCreate, SessionVolumeUpdate
from .base import CRUDBase

class CRUDSessionVolume(CRUDBase[SessionVolume, SessionVolumeCreate, SessionVolumeUpdate]):
    def get_by_user_and_trainer(self, db: Session, *, user_id: UUID, trainer_id: UUID) -> Optional[SessionVolume]:
        """Get session volume record by user and trainer"""
        return (
            db.query(SessionVolume)
            .options(joinedload(SessionVolume.user), joinedload(SessionVolume.trainer))
            .filter(
                and_(
                    SessionVolume.user_id == user_id,
                    SessionVolume.trainer_id == trainer_id,
                    SessionVolume.deleted_at.is_(None)
                )
            )
            .first()
        )
    
    def get_by_user(self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100) -> List[SessionVolume]:
        """Get all session volume records for a user"""
        return (
            db.query(SessionVolume)
            .options(joinedload(SessionVolume.user), joinedload(SessionVolume.trainer))
            .filter(
                and_(
                    SessionVolume.user_id == user_id,
                    SessionVolume.deleted_at.is_(None)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_trainer(self, db: Session, *, trainer_id: UUID, skip: int = 0, limit: int = 100) -> List[SessionVolume]:
        """Get all session volume records for a trainer"""
        return (
            db.query(SessionVolume)
            .options(joinedload(SessionVolume.user), joinedload(SessionVolume.trainer))
            .filter(
                and_(
                    SessionVolume.trainer_id == trainer_id,
                    SessionVolume.deleted_at.is_(None)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def increment_session_count(self, db: Session, *, session_volume: SessionVolume, count: int = 1, note: Optional[str] = None) -> SessionVolume:
        """Increment session count and optionally add a note"""
        session_volume.increment_session_count(count)
        if note:
            session_volume.add_note(note)
        
        db.add(session_volume)
        db.commit()
        db.refresh(session_volume)
        return session_volume
    
    def get_total_sessions_for_user(self, db: Session, *, user_id: UUID) -> int:
        """Get total session count for a user across all trainers"""
        result = (
            db.query(func.sum(SessionVolume.session_count))
            .filter(
                and_(
                    SessionVolume.user_id == user_id,
                    SessionVolume.deleted_at.is_(None)
                )
            )
            .scalar()
        )
        return result or 0
    
    def get_total_sessions_for_trainer(self, db: Session, *, trainer_id: UUID) -> int:
        """Get total session count for a trainer across all users"""
        result = (
            db.query(func.sum(SessionVolume.session_count))
            .filter(
                and_(
                    SessionVolume.trainer_id == trainer_id,
                    SessionVolume.deleted_at.is_(None)
                )
            )
            .scalar()
        )
        return result or 0
    
    def get_user_trainer_pairs(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[SessionVolume]:
        """Get all unique user-trainer pairs with session volumes"""
        return (
            db.query(SessionVolume)
            .options(joinedload(SessionVolume.user), joinedload(SessionVolume.trainer))
            .filter(SessionVolume.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_sessions_with_notes(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[SessionVolume]:
        """Get session volumes that have notes"""
        return (
            db.query(SessionVolume)
            .options(joinedload(SessionVolume.user), joinedload(SessionVolume.trainer))
            .filter(
                and_(
                    SessionVolume.notes.isnot(None),
                    SessionVolume.deleted_at.is_(None)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_high_volume_sessions(self, db: Session, *, min_sessions: int = 10, skip: int = 0, limit: int = 100) -> List[SessionVolume]:
        """Get session volumes with high session counts"""
        return (
            db.query(SessionVolume)
            .options(joinedload(SessionVolume.user), joinedload(SessionVolume.trainer))
            .filter(
                and_(
                    SessionVolume.session_count >= min_sessions,
                    SessionVolume.deleted_at.is_(None)
                )
            )
            .order_by(SessionVolume.session_count.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_active_records(self, db: Session) -> int:
        """Count all active session volume records"""
        return (
            db.query(SessionVolume)
            .filter(SessionVolume.deleted_at.is_(None))
            .count()
        )
    
    def get_trainer_clients_count(self, db: Session, *, trainer_id: UUID) -> int:
        """Get number of unique clients for a trainer"""
        return (
            db.query(SessionVolume.user_id)
            .filter(
                and_(
                    SessionVolume.trainer_id == trainer_id,
                    SessionVolume.deleted_at.is_(None)
                )
            )
            .distinct()
            .count()
        )
    
    def soft_delete(self, db: Session, *, db_obj: SessionVolume) -> SessionVolume:
        """Soft delete a session volume record"""
        db_obj.deleted_at = func.now()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def restore(self, db: Session, *, db_obj: SessionVolume) -> SessionVolume:
        """Restore a soft deleted session volume record"""
        db_obj.deleted_at = None
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_or_create_for_period(
        self,
        db: Session,
        *,
        trainer_id: UUID,
        customer_id: UUID,
        period: date
    ) -> SessionVolume:
        """Get or create session volume for a specific period"""
        existing = (
            db.query(SessionVolume)
            .filter(
                and_(
                    SessionVolume.trainer_id == trainer_id,
                    SessionVolume.customer_id == customer_id,
                    SessionVolume.period == period,
                    SessionVolume.deleted_at.is_(None)
                )
            )
            .first()
        )
        
        if existing:
            return existing
        
        # Create new session volume
        volume_data = SessionVolumeCreate(
            trainer_id=trainer_id,
            customer_id=customer_id,
            period=period,
            session_count=0
        )
        
        return self.create(db, obj_in=volume_data)
    
    def increment_session_count(self, db: Session, *, session_volume_id: UUID) -> SessionVolume:
        """Increment session count for a volume"""
        volume = self.get(db, id=session_volume_id)
        if volume:
            volume.session_count += 1
            db.add(volume)
            db.commit()
            db.refresh(volume)
        return volume
    
    def decrement_session_count(self, db: Session, *, session_volume_id: UUID) -> SessionVolume:
        """Decrement session count for a volume (when deleting sessions)"""
        volume = self.get(db, id=session_volume_id)
        if volume and volume.session_count > 0:
            volume.session_count -= 1
            db.add(volume)
            db.commit()
            db.refresh(volume)
        return volume
    
    def get_with_relations(self, db: Session, *, id: UUID) -> Optional[SessionVolume]:
        """Get session volume with related data"""
        return (
            db.query(SessionVolume)
            .options(
                joinedload(SessionVolume.customer),
                joinedload(SessionVolume.trainer)
            )
            .filter(SessionVolume.id == id, SessionVolume.deleted_at.is_(None))
            .first()
        )
    
    def get_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        trainer_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        status: Optional[str] = None,
        start_period: Optional[date] = None,
        end_period: Optional[date] = None
    ) -> List[SessionVolume]:
        """Get session volumes with filters"""
        query = (
            db.query(SessionVolume)
            .options(
                joinedload(SessionVolume.customer),
                joinedload(SessionVolume.trainer)
            )
            .filter(SessionVolume.deleted_at.is_(None))
        )
        
        if trainer_id:
            query = query.filter(SessionVolume.trainer_id == trainer_id)
            
        if customer_id:
            query = query.filter(SessionVolume.customer_id == customer_id)
            
        if status:
            query = query.filter(SessionVolume.status == status)
            
        if start_period:
            query = query.filter(SessionVolume.period >= start_period)
            
        if end_period:
            query = query.filter(SessionVolume.period <= end_period)
        
        return (
            query
            .order_by(SessionVolume.period.desc(), SessionVolume.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_period(
        self,
        db: Session,
        *,
        period: date,
        trainer_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None
    ) -> List[SessionVolume]:
        """Get session volumes for a specific period"""
        query = (
            db.query(SessionVolume)
            .options(
                joinedload(SessionVolume.customer),
                joinedload(SessionVolume.trainer)
            )
            .filter(
                SessionVolume.period == period,
                SessionVolume.deleted_at.is_(None)
            )
        )
        
        if trainer_id:
            query = query.filter(SessionVolume.trainer_id == trainer_id)
            
        if customer_id:
            query = query.filter(SessionVolume.customer_id == customer_id)
        
        return query.order_by(SessionVolume.created_at.desc()).all()

session_volume_crud = CRUDSessionVolume(SessionVolume)