# app/api/v1/sessions.py
from datetime import datetime, date, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from pydantic import BaseModel

from app.core.auth import get_current_active_user, require_admin, require_trainer_or_admin
from app.core.database import get_db
from app.crud.session_tracking import session_tracking_crud
from app.crud.session_volume import session_volume_crud
from app.crud.qr_code import qr_code_crud
from app.crud.user import user_crud
from app.models.user import User
from app.models.session_tracking import SessionTracking
from app.schemas.session_tracking import (
    SessionTrackingResponse, SessionTrackingCreate, SessionTrackingUpdate,
    SessionTrackingStats
)

router = APIRouter()

class TrackSessionRequest(BaseModel):
    """Schema for tracking a session via QR scan"""
    qr_token: str
    session_date: Optional[date] = None

class TrackSessionResponse(BaseModel):
    """Schema for session tracking response"""
    success: bool
    session_id: UUID
    message: str
    customer_name: str
    session_date: date
    monthly_volume_id: UUID
    total_sessions_this_month: int

@router.post("/track", response_model=TrackSessionResponse)
async def track_session(
    track_request: TrackSessionRequest,
    current_user: User = Depends(require_trainer_or_admin),
    db: Session = Depends(get_db)
):
    """
    Record a training session via QR code scan.
    
    Business rules:
    - Only 1 scan per trainer-customer pair per day
    - Automatically creates/updates monthly session volume
    - Only trainers and admins can track sessions
    """
    session_date = track_request.session_date or date.today()
    
    # Validate QR code
    qr_code = qr_code_crud.get_by_token(db, token=track_request.qr_token)
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid QR code"
        )
    
    customer = qr_code.user
    if not customer or not user_crud.is_active(customer):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer not found or inactive"
        )
    
    # Check for existing session on the same date
    existing_session = db.query(SessionTracking).filter(
        and_(
            SessionTracking.trainer_id == current_user.id,
            SessionTracking.qr_code_id == qr_code.id,
            SessionTracking.session_date == session_date
        )
    ).first()
    
    if existing_session:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Session already recorded for {customer.full_name} on {session_date}"
        )
    
    # Get or create monthly session volume
    period = session_date.replace(day=1)  # First day of month
    session_volume = session_volume_crud.get_or_create_for_period(
        db, 
        trainer_id=current_user.id,
        customer_id=customer.id,
        period=period
    )
    
    # Create session tracking record
    session_data = SessionTrackingCreate(
        trainer_id=current_user.id,
        qr_code_id=qr_code.id,
        session_volume_id=session_volume.id,
        session_date=session_date
    )
    
    session_record = session_tracking_crud.create(db, obj_in=session_data)
    
    # Update session volume count
    session_volume_crud.increment_session_count(db, session_volume_id=session_volume.id)
    
    return {
        "success": True,
        "session_id": session_record.id,
        "message": f"Session recorded for {customer.full_name}",
        "customer_name": customer.full_name,
        "session_date": session_date,
        "monthly_volume_id": session_volume.id,
        "total_sessions_this_month": session_volume.session_count + 1
    }

@router.get("", response_model=List[SessionTrackingResponse])
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    trainer_id: Optional[UUID] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all session tracking records with optional filters.
    Admin only - for oversight and reporting.
    """
    return session_tracking_crud.get_filtered(
        db,
        skip=skip,
        limit=limit,
        trainer_id=trainer_id,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{session_id}", response_model=SessionTrackingResponse)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific session.
    Users can only see their own sessions (as trainer or customer).
    """
    session_record = session_tracking_crud.get_with_relations(db, id=session_id)
    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Permission check - users can see sessions they're involved in
    customer = session_record.qr_code.user
    if not (current_user.has_role("Admin") or 
            current_user.id == session_record.trainer_id or 
            current_user.id == customer.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this session"
        )
    
    return session_record

@router.put("/{session_id}", response_model=SessionTrackingResponse)
async def update_session(
    session_id: UUID,
    session_update: SessionTrackingUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update session details.
    Admin only - for correcting mistakes.
    """
    session_record = session_tracking_crud.get(db, id=session_id)
    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session_tracking_crud.update(db, db_obj=session_record, obj_in=session_update)

@router.delete("/{session_id}")
async def delete_session(
    session_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a session record.
    Admin only - soft delete to maintain audit trail.
    Decrements the associated session volume count.
    """
    session_record = session_tracking_crud.get(db, id=session_id)
    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Decrement session volume count
    session_volume_crud.decrement_session_count(db, session_volume_id=session_record.session_volume_id)
    
    # Soft delete the session
    session_tracking_crud.remove(db, id=session_id)
    
    return {"message": "Session deleted successfully"}

@router.get("/customer/{customer_id}", response_model=List[SessionTrackingResponse])
async def get_customer_sessions(
    customer_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all sessions for a specific customer.
    - Customers can see their own sessions
    - Trainers can see sessions with customers they've trained
    - Admins can see all customer sessions
    """
    # Permission check
    if not current_user.has_role("Admin"):
        if current_user.id != customer_id and current_user.has_role("Customer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view your own sessions"
            )
    
    return session_tracking_crud.get_by_customer(
        db,
        customer_id=customer_id,
        trainer_id=current_user.id if current_user.has_role("Trainer") else None,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/trainer/{trainer_id}", response_model=List[SessionTrackingResponse])
async def get_trainer_sessions(
    trainer_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all sessions conducted by a specific trainer.
    - Trainers can see their own sessions
    - Admins can see all trainer sessions
    """
    # Permission check
    if not current_user.has_role("Admin") and current_user.id != trainer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own sessions"
        )
    
    return session_tracking_crud.get_by_trainer(
        db,
        trainer_id=trainer_id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/stats", response_model=SessionTrackingStats)
async def get_session_stats(
    trainer_id: Optional[UUID] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get session statistics.
    - Trainers can see their own stats
    - Customers can see their own stats
    - Admins can see all stats with filters
    """
    # Apply permission-based filters
    if current_user.has_role("Trainer") and not current_user.has_role("Admin"):
        trainer_id = current_user.id
    elif current_user.has_role("Customer") and not current_user.has_role("Admin"):
        customer_id = current_user.id
    
    return session_tracking_crud.get_stats(
        db,
        trainer_id=trainer_id,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date
    )