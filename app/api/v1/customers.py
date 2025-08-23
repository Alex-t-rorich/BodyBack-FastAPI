# app/api/v1/customers.py
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.auth import get_current_active_user, require_trainer_or_admin
from app.core.database import get_db
from app.crud.customer import customer_crud
from app.crud.trainer import trainer_crud
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.customer import CustomerResponse, CustomerListResponse, CustomerUpdate
from app.schemas.trainer import TrainerResponse

router = APIRouter()

class RequestTrainerRequest(BaseModel):
    """Schema for requesting a trainer assignment"""
    trainer_id: Optional[UUID] = None  # None means any available trainer
    message: Optional[str] = None  # Optional message to admin/trainer

class CustomerProgressResponse(BaseModel):
    """Schema for customer progress/statistics"""
    customer_id: UUID
    has_trainer: bool
    trainer_id: Optional[UUID] = None
    total_sessions: int
    sessions_this_month: int
    profile_completion: int  # Percentage 0-100
    joined_date: str

@router.get("/", response_model=List[CustomerListResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_trainer_or_admin),
    db: Session = Depends(get_db)
):
    """
    List all active customers.
    Only trainers and admins can view customer list.
    """
    customers = customer_crud.get_active(db, skip=skip, limit=limit)
    return customers

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer_details(
    customer_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific customer.
    Customers can view their own details.
    Trainers can view their assigned customers.
    Admins can view any customer.
    """
    customer = customer_crud.get_by_user_id(db, user_id=customer_id)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Permission check
    if current_user.id == customer_id:
        # Users can always view their own data
        pass
    elif current_user.has_role("Admin"):
        # Admins can view any customer
        pass
    elif current_user.has_role("Trainer"):
        # Trainers can only view their assigned customers
        if customer.trainer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Trainers can only view their assigned customers"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this customer"
        )
    
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer_info(
    customer_id: UUID,
    customer_update: CustomerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update customer information.
    Customers can update their own profile data and picture.
    Only admins can change trainer assignments.
    Trainers can update profile data for their assigned customers.
    """
    customer = customer_crud.get_by_user_id(db, user_id=customer_id)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Permission checks
    can_update_profile = False
    can_update_trainer = False
    
    if current_user.id == customer_id:
        # Customers can update their own profile data
        can_update_profile = True
    elif current_user.has_role("Admin"):
        # Admins can update everything
        can_update_profile = True
        can_update_trainer = True
    elif current_user.has_role("Trainer") and customer.trainer_id == current_user.id:
        # Trainers can update profile data for their assigned customers
        can_update_profile = True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this customer"
        )
    
    # Validate trainer assignment changes
    if customer_update.trainer_id is not None and not can_update_trainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change trainer assignments"
        )
    
    # If trainer assignment is being changed, validate the trainer
    if customer_update.trainer_id is not None and can_update_trainer:
        if customer_update.trainer_id != customer.trainer_id:  # Only check if actually changing
            trainer_user = user_crud.get(db, id=customer_update.trainer_id)
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
    
    # Filter update data based on permissions
    update_data = {}
    if can_update_profile:
        if customer_update.profile_picture_url is not None:
            update_data["profile_picture_url"] = customer_update.profile_picture_url
        if customer_update.profile_data is not None:
            update_data["profile_data"] = customer_update.profile_data
    
    if can_update_trainer and customer_update.trainer_id is not None:
        update_data["trainer_id"] = customer_update.trainer_id
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid update data provided"
        )
    
    # Create update object
    filtered_update = CustomerUpdate(**update_data)
    customer = customer_crud.update(db, db_obj=customer, obj_in=filtered_update)
    
    return customer

@router.get("/{customer_id}/trainer", response_model=Optional[TrainerResponse])
async def get_customer_trainer(
    customer_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the trainer assigned to a specific customer.
    Customers can view their own trainer.
    Trainers and admins can view any customer's trainer.
    """
    customer = customer_crud.get_by_user_id(db, user_id=customer_id)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Permission check
    if (current_user.id != customer_id and 
        not current_user.has_role("Admin") and 
        not current_user.has_role("Trainer")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not customer.trainer_id:
        return None
    
    trainer = trainer_crud.get_by_user_id(db, user_id=customer.trainer_id)
    return trainer

@router.post("/{customer_id}/request-trainer")
async def request_trainer_assignment(
    customer_id: UUID,
    request_data: RequestTrainerRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Request a trainer assignment.
    Only customers can request trainers for themselves.
    This creates a request that admins can review and approve.
    """
    # Only customers can request trainers, and only for themselves
    if current_user.id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only request trainers for yourself"
        )
    
    if not current_user.has_role("Customer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can request trainer assignments"
        )
    
    customer = customer_crud.get_by_user_id(db, user_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer record not found"
        )
    
    # Check if customer already has a trainer
    if customer.trainer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer already has a trainer assigned"
        )
    
    # If specific trainer is requested, validate they exist and are active
    if request_data.trainer_id:
        trainer_user = user_crud.get(db, id=request_data.trainer_id)
        if not trainer_user or not user_crud.is_active(trainer_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested trainer not found or inactive"
            )
        if not trainer_user.has_role("Trainer"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested user is not a trainer"
            )
    
    # TODO: In a production system, this would create a trainer request record
    # that admins can review and approve/deny. For now, we'll return a success message.
    
    trainer_info = ""
    if request_data.trainer_id:
        trainer_user = user_crud.get(db, id=request_data.trainer_id)
        trainer_info = f" for trainer {trainer_user.first_name} {trainer_user.last_name}"
    
    return {
        "message": f"Trainer assignment request submitted{trainer_info}. An administrator will review your request.",
        "request_id": None  # Would be actual request ID in production
    }

@router.get("/me/progress", response_model=CustomerProgressResponse)
async def get_my_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get progress and statistics for the current customer.
    Only customers can access this endpoint for their own data.
    """
    if not current_user.has_role("Customer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can access progress statistics"
        )
    
    customer = customer_crud.get_by_user_id(db, user_id=current_user.id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer record not found"
        )
    
    # Calculate profile completion percentage
    profile_fields = [
        current_user.first_name,
        current_user.last_name,
        current_user.phone_number,
        current_user.location,
        customer.profile_picture_url,
        customer.profile_data.get("bio") if customer.profile_data else None,
    ]
    
    completed_fields = sum(1 for field in profile_fields if field)
    profile_completion = int((completed_fields / len(profile_fields)) * 100)
    
    # TODO: Implement session counting when session tracking is fully implemented
    total_sessions = 0
    sessions_this_month = 0
    
    return {
        "customer_id": current_user.id,
        "has_trainer": customer.trainer_id is not None,
        "trainer_id": customer.trainer_id,
        "total_sessions": total_sessions,
        "sessions_this_month": sessions_this_month,
        "profile_completion": profile_completion,
        "joined_date": customer.created_at.isoformat()
    }