from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.auth import get_current_active_user, require_admin, require_trainer_or_admin
from app.core.database import get_db
from app.crud.session_volume import session_volume_crud
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.session_volume import (
    SessionVolumeResponse, SessionVolumeCreate, SessionVolumeUpdate,
    SessionVolumeStatusUpdate
)

router = APIRouter()

class StatusChangeResponse(BaseModel):
    """Schema for status change responses"""
    success: bool
    message: str
    new_status: str
    updated_at: str

@router.get("", response_model=List[SessionVolumeResponse])
async def list_session_volumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    trainer_id: Optional[UUID] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    start_period: Optional[date] = Query(None),
    end_period: Optional[date] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List session volumes with optional filters.
    
    - Trainers can see volumes they created
    - Customers can see volumes where they're the customer
    - Admins can see all volumes
    """
    # Apply role-based filtering
    if current_user.has_role("Admin"):
        # Admins can see all volumes with any filters
        pass
    elif current_user.has_role("Trainer"):
        # Trainers can only see their own volumes
        trainer_id = current_user.id
    elif current_user.has_role("Customer"):
        # Customers can only see volumes where they're the customer
        customer_id = current_user.id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view session volumes"
        )
    
    return session_volume_crud.get_filtered(
        db,
        skip=skip,
        limit=limit,
        trainer_id=trainer_id,
        customer_id=customer_id,
        status=status,
        start_period=start_period,
        end_period=end_period
    )

@router.post("", response_model=SessionVolumeResponse)
async def create_session_volume(
    volume_data: SessionVolumeCreate,
    current_user: User = Depends(require_trainer_or_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new session volume.
    Only trainers and admins can create volumes.
    Trainers can only create volumes for themselves.
    """
    # Trainers can only create volumes for themselves
    if current_user.has_role("Trainer") and not current_user.has_role("Admin"):
        volume_data.trainer_id = current_user.id
    
    # Validate trainer exists and is active
    trainer_user = user_crud.get(db, id=volume_data.trainer_id)
    if not trainer_user or not user_crud.is_active(trainer_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trainer not found or inactive"
        )
    
    if not trainer_user.has_role("Trainer"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a trainer"
        )
    
    # Validate customer exists and is active
    customer_user = user_crud.get(db, id=volume_data.customer_id)
    if not customer_user or not user_crud.is_active(customer_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer not found or inactive"
        )
    
    if not customer_user.has_role("Customer"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a customer"
        )
    
    # Check for existing volume for same trainer-customer-period
    from sqlalchemy import and_
    existing = db.query(session_volume_crud.model).filter(
        and_(
            session_volume_crud.model.trainer_id == volume_data.trainer_id,
            session_volume_crud.model.customer_id == volume_data.customer_id,
            session_volume_crud.model.period == volume_data.period,
            session_volume_crud.model.deleted_at.is_(None)
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Session volume already exists for this trainer-customer-period"
        )

    return session_volume_crud.create(db, obj_in=volume_data)

@router.get("/{volume_id}", response_model=SessionVolumeResponse)
async def get_session_volume(
    volume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific session volume.
    Users can only see volumes they're involved in.
    """
    volume = session_volume_crud.get_with_relations(db, id=volume_id)
    if not volume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session volume not found"
        )
    
    # Permission check - users can see volumes they're involved in
    if not (current_user.has_role("Admin") or 
            current_user.id == volume.trainer_id or 
            current_user.id == volume.customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this session volume"
        )
    
    return volume

@router.put("/{volume_id}", response_model=SessionVolumeResponse)
async def update_session_volume(
    volume_id: UUID,
    volume_update: SessionVolumeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update session volume details (plans, notes).
    Only the trainer who created it or admins can update.
    Cannot update submitted/approved volumes.
    """
    volume = session_volume_crud.get(db, id=volume_id)
    if not volume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session volume not found"
        )
    
    # Permission check
    if not (current_user.has_role("Admin") or current_user.id == volume.trainer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the trainer who created this volume or admins can update it"
        )
    
    # Cannot update submitted or approved volumes
    if volume.status in ["submitted", "read", "approved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update volume with status '{volume.status}'. Only draft or rejected volumes can be updated."
        )
    
    return session_volume_crud.update(db, db_obj=volume, obj_in=volume_update)

@router.delete("/{volume_id}")
async def delete_session_volume(
    volume_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a session volume.
    Admin only - soft delete to maintain audit trail.
    Cannot delete approved volumes.
    """
    volume = session_volume_crud.get(db, id=volume_id)
    if not volume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session volume not found"
        )
    
    # Cannot delete approved volumes
    if volume.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete approved session volumes"
        )
    
    # Soft delete the volume
    session_volume_crud.soft_delete(db, db_obj=volume)
    
    return {"message": "Session volume deleted successfully"}

@router.post("/{volume_id}/submit", response_model=StatusChangeResponse)
async def submit_session_volume(
    volume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit a session volume to customer for review.
    Only the trainer who created it can submit.
    """
    volume = session_volume_crud.get(db, id=volume_id)
    if not volume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session volume not found"
        )
    
    # Permission check
    if not (current_user.has_role("Admin") or current_user.id == volume.trainer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the trainer who created this volume can submit it"
        )
    
    # Can only submit draft volumes
    if volume.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit volume with status '{volume.status}'. Only draft volumes can be submitted."
        )
    
    # Submit the volume
    volume.submit()
    db.add(volume)
    db.commit()
    db.refresh(volume)
    
    return {
        "success": True,
        "message": "Session volume submitted to customer for review",
        "new_status": volume.status,
        "updated_at": volume.updated_at.isoformat()
    }

@router.post("/{volume_id}/approve", response_model=StatusChangeResponse)
async def approve_session_volume(
    volume_id: UUID,
    approval_data: Optional[SessionVolumeStatusUpdate] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Customer approves a submitted session volume.
    Only the customer can approve their own volumes.
    """
    volume = session_volume_crud.get(db, id=volume_id)
    if not volume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session volume not found"
        )
    
    # Permission check - only the customer can approve
    if not (current_user.has_role("Admin") or current_user.id == volume.customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the customer can approve their session volume"
        )
    
    # Can only approve submitted or read volumes
    if volume.status not in ["submitted", "read"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve volume with status '{volume.status}'. Only submitted or read volumes can be approved."
        )
    
    # Mark as read first if it was just submitted
    if volume.status == "submitted":
        volume.mark_as_read()
    
    # Approve the volume
    volume.approve()
    
    # Add approval notes if provided
    if approval_data and approval_data.notes:
        current_notes = volume.notes or ""
        approval_note = f"\n--- Customer Approval ({datetime.utcnow().date()}) ---\n{approval_data.notes}"
        volume.notes = current_notes + approval_note
    
    db.add(volume)
    db.commit()
    db.refresh(volume)
    
    return {
        "success": True,
        "message": "Session volume approved successfully",
        "new_status": volume.status,
        "updated_at": volume.updated_at.isoformat()
    }

@router.post("/{volume_id}/reject", response_model=StatusChangeResponse)
async def reject_session_volume(
    volume_id: UUID,
    rejection_data: SessionVolumeStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Customer rejects a submitted session volume.
    Only the customer can reject their own volumes.
    Rejection reason is required.
    """
    volume = session_volume_crud.get(db, id=volume_id)
    if not volume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session volume not found"
        )
    
    # Permission check - only the customer can reject
    if not (current_user.has_role("Admin") or current_user.id == volume.customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the customer can reject their session volume"
        )
    
    # Can only reject submitted or read volumes
    if volume.status not in ["submitted", "read"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject volume with status '{volume.status}'. Only submitted or read volumes can be rejected."
        )
    
    # Rejection reason is required
    if not rejection_data.notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required"
        )
    
    # Mark as read first if it was just submitted
    if volume.status == "submitted":
        volume.mark_as_read()
    
    # Reject the volume
    volume.reject()
    
    # Add rejection notes
    current_notes = volume.notes or ""
    rejection_note = f"\n--- Customer Rejection ({datetime.utcnow().date()}) ---\n{rejection_data.notes}"
    volume.notes = current_notes + rejection_note
    
    db.add(volume)
    db.commit()
    db.refresh(volume)
    
    return {
        "success": True,
        "message": "Session volume rejected",
        "new_status": volume.status,
        "updated_at": volume.updated_at.isoformat()
    }

@router.post("/{volume_id}/reopen", response_model=StatusChangeResponse)
async def reopen_session_volume(
    volume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reopen a rejected session volume back to draft status.
    Only the trainer who created it can reopen.
    """
    volume = session_volume_crud.get(db, id=volume_id)
    if not volume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session volume not found"
        )
    
    # Permission check
    if not (current_user.has_role("Admin") or current_user.id == volume.trainer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the trainer who created this volume can reopen it"
        )
    
    # Can only reopen rejected volumes
    if volume.status != "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reopen volume with status '{volume.status}'. Only rejected volumes can be reopened."
        )
    
    # Reopen the volume
    volume.reopen()
    
    # Add reopen note
    current_notes = volume.notes or ""
    reopen_note = f"\n--- Volume Reopened ({datetime.utcnow().date()}) ---\nVolume reopened for revision."
    volume.notes = current_notes + reopen_note
    
    db.add(volume)
    db.commit()
    db.refresh(volume)
    
    return {
        "success": True,
        "message": "Session volume reopened for editing",
        "new_status": volume.status,
        "updated_at": volume.updated_at.isoformat()
    }

@router.get("/period/{year}/{month}", response_model=List[SessionVolumeResponse])
async def get_volumes_by_period(
    year: int,
    month: int,
    trainer_id: Optional[UUID] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get session volumes for a specific period (year/month).
    
    - Trainers can see their own volumes for the period
    - Customers can see volumes where they're the customer
    - Admins can see all volumes with optional filters
    """
    # Validate year and month
    if not (1 <= month <= 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12"
        )
    
    if not (2020 <= year <= 2030):  # Reasonable year range
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year must be between 2020 and 2030"
        )
    
    # Create period date (first day of the month)
    try:
        period_date = date(year, month, 1)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date"
        )
    
    # Apply role-based filtering
    if current_user.has_role("Admin"):
        # Admins can see all volumes with any filters
        pass
    elif current_user.has_role("Trainer"):
        # Trainers can only see their own volumes
        trainer_id = current_user.id
    elif current_user.has_role("Customer"):
        # Customers can only see volumes where they're the customer
        customer_id = current_user.id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view session volumes"
        )
    
    return session_volume_crud.get_by_period(
        db,
        period=period_date,
        trainer_id=trainer_id,
        customer_id=customer_id
    )