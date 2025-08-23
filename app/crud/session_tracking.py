# app/crud/session_tracking.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc, Date, distinct
from uuid import UUID
from datetime import date, datetime

from app.models.session_tracking import SessionTracking
from app.schemas.session_tracking import SessionTrackingCreate, SessionTrackingUpdate, SessionTrackingStats
from .base import CRUDBase

class CRUDSessionTracking(CRUDBase[SessionTracking, SessionTrackingCreate, SessionTrackingUpdate]):
    def get_by_trainer(self, db: Session, *, trainer_id: UUID, skip: int = 0, limit: int = 100) -> List[SessionTracking]:
        """Get all session tracking records by a trainer"""
        return (
            db.query(SessionTracking)
            .options(
                joinedload(SessionTracking.trainer),
                joinedload(SessionTracking.qr_code),
                joinedload(SessionTracking.session_volume)
            )
            .filter(SessionTracking.trainer_id == trainer_id)
            .order_by(desc(SessionTracking.scan_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_qr_code(self, db: Session, *, qr_code_id: UUID, skip: int = 0, limit: int = 100) -> List[SessionTracking]:
        """Get all session tracking records for a QR code"""
        return (
            db.query(SessionTracking)
            .options(
                joinedload(SessionTracking.trainer),
                joinedload(SessionTracking.qr_code),
                joinedload(SessionTracking.session_volume)
            )
            .filter(SessionTracking.qr_code_id == qr_code_id)
            .order_by(desc(SessionTracking.scan_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_session_volume(self, db: Session, *, session_volume_id: UUID, skip: int = 0, limit: int = 100) -> List[SessionTracking]:
        """Get all session tracking records for a session volume"""
        return (
            db.query(SessionTracking)
            .options(
                joinedload(SessionTracking.trainer),
                joinedload(SessionTracking.qr_code),
                joinedload(SessionTracking.session_volume)
            )
            .filter(SessionTracking.session_volume_id == session_volume_id)
            .order_by(desc(SessionTracking.scan_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_date(self, db: Session, *, session_date: date, trainer_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[SessionTracking]:
        """Get session tracking records for a specific date"""
        query = db.query(SessionTracking).options(
            joinedload(SessionTracking.trainer),
            joinedload(SessionTracking.qr_code),
            joinedload(SessionTracking.session_volume)
        ).filter(SessionTracking.session_date == session_date)
        
        if trainer_id:
            query = query.filter(SessionTracking.trainer_id == trainer_id)
        
        return (
            query
            .order_by(desc(SessionTracking.scan_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_date_range(
        self, 
        db: Session, 
        *, 
        start_date: date, 
        end_date: date,
        trainer_id: Optional[UUID] = None,
        session_volume_id: Optional[UUID] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[SessionTracking]:
        """Get session tracking records for a date range"""
        query = db.query(SessionTracking).options(
            joinedload(SessionTracking.trainer),
            joinedload(SessionTracking.qr_code),
            joinedload(SessionTracking.session_volume)
        ).filter(
            and_(
                SessionTracking.session_date >= start_date,
                SessionTracking.session_date <= end_date
            )
        )
        
        if trainer_id:
            query = query.filter(SessionTracking.trainer_id == trainer_id)
        
        if session_volume_id:
            query = query.filter(SessionTracking.session_volume_id == session_volume_id)
        
        return (
            query
            .order_by(desc(SessionTracking.scan_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_scan(
        self, 
        db: Session, 
        *, 
        trainer_id: UUID,
        qr_code_id: UUID,
        session_volume_id: UUID,
        session_date: Optional[date] = None
    ) -> SessionTracking:
        """Create a new session tracking record for a scan"""
        if session_date is None:
            session_date = date.today()
        
        tracking = SessionTracking(
            trainer_id=trainer_id,
            qr_code_id=qr_code_id,
            session_volume_id=session_volume_id,
            session_date=session_date
        )
        
        db.add(tracking)
        db.commit()
        db.refresh(tracking)
        return tracking
    
    def check_duplicate_scan(
        self,
        db: Session,
        *,
        qr_code_id: UUID,
        session_volume_id: UUID,
        session_date: date
    ) -> bool:
        """Check if a scan already exists for the same QR code, volume, and date"""
        existing = db.query(SessionTracking).filter(
            and_(
                SessionTracking.qr_code_id == qr_code_id,
                SessionTracking.session_volume_id == session_volume_id,
                SessionTracking.session_date == session_date
            )
        ).first()
        
        return existing is not None
    
    def get_session_count(
        self,
        db: Session,
        *,
        session_volume_id: UUID,
        unique_days: bool = True
    ) -> int:
        """Get count of sessions for a volume"""
        if unique_days:
            # Count unique days (eliminates duplicate scans on same day)
            return (
                db.query(func.count(func.distinct(SessionTracking.session_date)))
                .filter(SessionTracking.session_volume_id == session_volume_id)
                .scalar() or 0
            )
        else:
            # Count all scans
            return (
                db.query(func.count(SessionTracking.id))
                .filter(SessionTracking.session_volume_id == session_volume_id)
                .scalar() or 0
            )
    
    def get_with_relations(self, db: Session, *, id: UUID) -> Optional[SessionTracking]:
        """Get session tracking record with all related data"""
        return (
            db.query(SessionTracking)
            .options(
                joinedload(SessionTracking.trainer),
                joinedload(SessionTracking.qr_code).joinedload('user'),
                joinedload(SessionTracking.session_volume)
            )
            .filter(SessionTracking.id == id)
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
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[SessionTracking]:
        """Get session tracking records with filters"""
        query = (
            db.query(SessionTracking)
            .options(
                joinedload(SessionTracking.trainer),
                joinedload(SessionTracking.qr_code).joinedload('user'),
                joinedload(SessionTracking.session_volume)
            )
        )
        
        if trainer_id:
            query = query.filter(SessionTracking.trainer_id == trainer_id)
            
        if customer_id:
            query = query.join(SessionTracking.qr_code).filter(
                SessionTracking.qr_code.has(user_id=customer_id)
            )
            
        if start_date:
            query = query.filter(SessionTracking.session_date >= start_date)
            
        if end_date:
            query = query.filter(SessionTracking.session_date <= end_date)
        
        return (
            query
            .order_by(desc(SessionTracking.session_date), desc(SessionTracking.scan_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_customer(
        self,
        db: Session,
        *,
        customer_id: UUID,
        trainer_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[SessionTracking]:
        """Get sessions for a specific customer"""
        query = (
            db.query(SessionTracking)
            .join(SessionTracking.qr_code)
            .options(
                joinedload(SessionTracking.trainer),
                joinedload(SessionTracking.qr_code).joinedload('user'),
                joinedload(SessionTracking.session_volume)
            )
            .filter(SessionTracking.qr_code.has(user_id=customer_id))
        )
        
        if trainer_id:
            query = query.filter(SessionTracking.trainer_id == trainer_id)
            
        if start_date:
            query = query.filter(SessionTracking.session_date >= start_date)
            
        if end_date:
            query = query.filter(SessionTracking.session_date <= end_date)
        
        return (
            query
            .order_by(desc(SessionTracking.session_date), desc(SessionTracking.scan_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_stats(
        self,
        db: Session,
        *,
        trainer_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> SessionTrackingStats:
        """Get session tracking statistics"""
        query = db.query(SessionTracking)
        
        if trainer_id:
            query = query.filter(SessionTracking.trainer_id == trainer_id)
            
        if customer_id:
            query = query.join(SessionTracking.qr_code).filter(
                SessionTracking.qr_code.has(user_id=customer_id)
            )
            
        if start_date:
            query = query.filter(SessionTracking.session_date >= start_date)
            
        if end_date:
            query = query.filter(SessionTracking.session_date <= end_date)
        
        # Get basic stats
        total_scans = query.count()
        
        if total_scans == 0:
            return SessionTrackingStats(
                total_scans=0,
                unique_days=0,
                first_scan=None,
                last_scan=None
            )
        
        # Get unique days
        unique_days = query.with_entities(distinct(SessionTracking.session_date)).count()
        
        # Get first and last scan timestamps
        scan_times = query.with_entities(
            func.min(SessionTracking.scan_timestamp).label('first_scan'),
            func.max(SessionTracking.scan_timestamp).label('last_scan')
        ).first()
        
        return SessionTrackingStats(
            total_scans=total_scans,
            unique_days=unique_days,
            first_scan=scan_times.first_scan,
            last_scan=scan_times.last_scan
        )
    
    def check_daily_limit(
        self,
        db: Session,
        *,
        trainer_id: UUID,
        qr_code_id: UUID,
        session_date: date
    ) -> bool:
        """Check if session already exists for this trainer-customer-date combination"""
        existing = db.query(SessionTracking).filter(
            and_(
                SessionTracking.trainer_id == trainer_id,
                SessionTracking.qr_code_id == qr_code_id,
                SessionTracking.session_date == session_date
            )
        ).first()
        
        return existing is not None
    
    def get_tracking_stats(
        self,
        db: Session,
        *,
        session_volume_id: Optional[UUID] = None,
        trainer_id: Optional[UUID] = None,
        qr_code_id: Optional[UUID] = None
    ) -> dict:
        """Get session tracking statistics (legacy method)"""
        query = db.query(SessionTracking)
        
        if session_volume_id:
            query = query.filter(SessionTracking.session_volume_id == session_volume_id)
        if trainer_id:
            query = query.filter(SessionTracking.trainer_id == trainer_id)
        if qr_code_id:
            query = query.filter(SessionTracking.qr_code_id == qr_code_id)
        
        total_scans = query.count()
        unique_days = db.query(func.count(func.distinct(SessionTracking.session_date))).filter(
            query.whereclause if query.whereclause is not None else True
        ).scalar() or 0
        
        first_scan = query.order_by(SessionTracking.scan_timestamp).first()
        last_scan = query.order_by(desc(SessionTracking.scan_timestamp)).first()
        
        return {
            "total_scans": total_scans,
            "unique_days": unique_days,
            "first_scan": first_scan.scan_timestamp if first_scan else None,
            "last_scan": last_scan.scan_timestamp if last_scan else None
        }

session_tracking_crud = CRUDSessionTracking(SessionTracking)