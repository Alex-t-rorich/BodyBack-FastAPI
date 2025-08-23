# app/api/v1/qr_codes.py
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.auth import get_current_active_user, require_trainer_or_admin
from app.core.database import get_db
from app.crud.qr_code import qr_code_crud
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.qr_code import QRCodeResponse

router = APIRouter()

class ScanQRCodeRequest(BaseModel):
    """Schema for scanning a QR code"""
    token: str

class ScanQRCodeResponse(BaseModel):
    """Schema for QR code scan response"""
    valid: bool
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_role: Optional[str] = None
    message: str
    scanned_at: str

class QRCodeDisplayResponse(BaseModel):
    """Schema for QR code display (customer view)"""
    token: str
    qr_url: Optional[str] = None  # URL for QR code image generation
    user_name: str
    created_at: str
    instructions: str

@router.get("/me", response_model=QRCodeDisplayResponse)
async def get_my_qr_code(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's QR code for display.
    
    This endpoint is primarily for customers to show their QR code to trainers,
    but any authenticated user can get their QR code.
    
    If user doesn't have a QR code, one is automatically created.
    """
    # Get or create QR code for user
    qr_code = qr_code_crud.get_by_user(db, user_id=current_user.id)
    
    if not qr_code:
        # Auto-create QR code if it doesn't exist
        qr_code = qr_code_crud.create_for_user(db, user_id=current_user.id)
    
    # Determine user display name
    user_name = current_user.full_name
    
    # Generate instructions based on user role
    instructions = ""
    if current_user.has_role("Customer"):
        instructions = "Show this QR code to your trainer to record training sessions."
    elif current_user.has_role("Trainer"):
        instructions = "This is your trainer QR code for identification purposes."
    else:
        instructions = "This is your unique QR code for system identification."
    
    # In a production system, qr_url would be generated to create actual QR code image
    # For example: qr_url = f"/api/v1/qr-codes/{qr_code.token}/image"
    qr_url = None
    
    return {
        "token": qr_code.token,
        "qr_url": qr_url,
        "user_name": user_name,
        "created_at": qr_code.created_at.isoformat(),
        "instructions": instructions
    }

@router.post("/scan", response_model=ScanQRCodeResponse)
async def scan_qr_code(
    scan_request: ScanQRCodeRequest,
    current_user: User = Depends(require_trainer_or_admin),
    db: Session = Depends(get_db)
):
    """
    Scan and validate a QR code.
    
    This endpoint is used by trainers to scan customer QR codes to:
    1. Validate the QR code is legitimate
    2. Get customer information
    3. Record training sessions (future functionality)
    
    Only trainers and admins can scan QR codes.
    """
    scan_time = datetime.utcnow()
    
    # Validate the QR code token
    qr_code = qr_code_crud.get_by_token(db, token=scan_request.token)
    
    if not qr_code:
        return {
            "valid": False,
            "user_id": None,
            "user_name": None,
            "user_role": None,
            "message": "Invalid QR code",
            "scanned_at": scan_time.isoformat()
        }
    
    # Get the user associated with the QR code
    user = qr_code.user
    if not user:
        return {
            "valid": False,
            "user_id": None,
            "user_name": None,
            "user_role": None,
            "message": "QR code user not found",
            "scanned_at": scan_time.isoformat()
        }
    
    # Check if user is active
    if not user_crud.is_active(user):
        return {
            "valid": False,
            "user_id": str(user.id),
            "user_name": user.full_name,
            "user_role": user.role_name,
            "message": "User account is inactive",
            "scanned_at": scan_time.isoformat()
        }
    
    # Additional validation for trainer scanning customer codes
    if current_user.has_role("Trainer") and user.has_role("Customer"):
        # Check if this trainer is assigned to this customer
        from app.crud.customer import customer_crud
        customer = customer_crud.get_by_user_id(db, user_id=user.id)
        
        if customer and customer.trainer_id and customer.trainer_id != current_user.id:
            # Customer has a different trainer assigned
            assigned_trainer = user_crud.get(db, id=customer.trainer_id)
            trainer_name = assigned_trainer.full_name if assigned_trainer else "Unknown"
            
            return {
                "valid": True,  # QR code is valid, but there's a warning
                "user_id": str(user.id),
                "user_name": user.full_name,
                "user_role": user.role_name,
                "message": f"Warning: This customer is assigned to trainer {trainer_name}",
                "scanned_at": scan_time.isoformat()
            }
    
    # Successful scan
    success_message = f"Valid QR code for {user.role_name.lower()} {user.full_name}"
    
    # TODO: Record session tracking entry here when session tracking is implemented
    # This would create a new SessionTracking record linking the trainer and customer
    
    return {
        "valid": True,
        "user_id": str(user.id),
        "user_name": user.full_name,
        "user_role": user.role_name,
        "message": success_message,
        "scanned_at": scan_time.isoformat()
    }