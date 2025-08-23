# app/api/v1/trainers.py
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.auth import get_current_active_user, require_trainer_or_admin
from app.core.database import get_db
from app.crud.trainer import trainer_crud
from app.crud.customer import customer_crud
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.trainer import TrainerResponse, TrainerListResponse
from app.schemas.customer import CustomerResponse

router = APIRouter()

class AssignCustomerRequest(BaseModel):
    """Schema for assigning a customer to trainer"""
    customer_id: UUID

class RemoveCustomerRequest(BaseModel):
    """Schema for removing a customer from trainer"""
    customer_id: UUID

class TrainerStatsResponse(BaseModel):
    """Schema for trainer statistics"""
    trainer_id: UUID
    total_customers: int
    active_customers: int
    total_sessions: int
    sessions_this_month: int
    
@router.get("/", response_model=List[TrainerListResponse])
async def list_trainers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all active trainers.
    Anyone can view the trainer list.
    """
    trainers = trainer_crud.get_active(db, skip=skip, limit=limit)
    return trainers

@router.get("/{trainer_id}", response_model=TrainerResponse)
async def get_trainer_details(
    trainer_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific trainer.
    Anyone can view trainer details.
    """
    trainer = trainer_crud.get_by_user_id(db, user_id=trainer_id)
    
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )
    
    return trainer

@router.get("/{trainer_id}/customers", response_model=List[CustomerResponse])
async def get_trainer_customers(
    trainer_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_trainer_or_admin),
    db: Session = Depends(get_db)
):
    """
    Get customers assigned to a specific trainer.
    Only trainers and admins can access this.
    Trainers can only view their own customers.
    """
    # Check if trainer exists
    trainer = trainer_crud.get_by_user_id(db, user_id=trainer_id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )
    
    # Trainers can only view their own customers
    if current_user.has_role("Trainer") and current_user.id != trainer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trainers can only view their own customers"
        )
    
    customers = trainer_crud.get_customers(db, trainer_id=trainer_id, skip=skip, limit=limit)
    return customers

@router.post("/{trainer_id}/assign-customer")
async def assign_customer_to_trainer(
    trainer_id: UUID,
    assignment_request: AssignCustomerRequest,
    current_user: User = Depends(require_trainer_or_admin),
    db: Session = Depends(get_db)
):
    """
    Assign a customer to a trainer.
    Only admins can assign customers to any trainer.
    Trainers cannot assign customers to themselves.
    """
    # Only admins can assign customers
    if not current_user.has_role("Admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can assign customers to trainers"
        )
    
    # Check if trainer exists
    trainer = trainer_crud.get_by_user_id(db, user_id=trainer_id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )
    
    # Check if trainer user is active
    trainer_user = user_crud.get(db, id=trainer_id)
    if not trainer_user or not user_crud.is_active(trainer_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trainer is not active"
        )
    
    # Check if customer exists and is active
    customer_user = user_crud.get(db, id=assignment_request.customer_id)
    if not customer_user or not user_crud.is_active(customer_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found or inactive"
        )
    
    # Check if customer has Customer role
    if not customer_user.has_role("Customer"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a customer"
        )
    
    # Assign customer to trainer
    try:
        customer = customer_crud.assign_trainer(
            db, 
            customer_id=assignment_request.customer_id, 
            trainer_id=trainer_id
        )
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer record not found"
            )
            
        return {"message": f"Customer successfully assigned to trainer"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign customer: {str(e)}"
        )

@router.delete("/{trainer_id}/remove-customer")
async def remove_customer_from_trainer(
    trainer_id: UUID,
    removal_request: RemoveCustomerRequest,
    current_user: User = Depends(require_trainer_or_admin),
    db: Session = Depends(get_db)
):
    """
    Remove a customer from a trainer.
    Only admins can remove customer assignments.
    """
    # Only admins can remove customer assignments
    if not current_user.has_role("Admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can remove customer assignments"
        )
    
    # Check if trainer exists
    trainer = trainer_crud.get_by_user_id(db, user_id=trainer_id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )
    
    # Check if customer exists
    customer_user = user_crud.get(db, id=removal_request.customer_id)
    if not customer_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Remove customer from trainer
    try:
        customer = customer_crud.unassign_trainer(
            db, 
            customer_id=removal_request.customer_id
        )
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer record not found"
            )
            
        return {"message": "Customer successfully removed from trainer"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove customer: {str(e)}"
        )

@router.get("/me/stats", response_model=TrainerStatsResponse)
async def get_my_trainer_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for the current trainer.
    Only trainers can access this endpoint.
    """
    # Check if current user is a trainer
    if not current_user.has_role("Trainer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers can access trainer statistics"
        )
    
    # Check if trainer record exists
    trainer = trainer_crud.get_by_user_id(db, user_id=current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer record not found"
        )
    
    # Get customer counts
    total_customers = customer_crud.count_by_trainer(db, trainer_id=current_user.id)
    active_customers = total_customers  # For now, assume all assigned customers are active
    
    # TODO: Implement session counting when session tracking is fully implemented
    # For now, return placeholder values
    total_sessions = 0
    sessions_this_month = 0
    
    return {
        "trainer_id": current_user.id,
        "total_customers": total_customers,
        "active_customers": active_customers,
        "total_sessions": total_sessions,
        "sessions_this_month": sessions_this_month
    }