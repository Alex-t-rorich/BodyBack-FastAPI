import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime, timezone

from app.schemas.trainer import (
    TrainerBase,
    TrainerCreate,
    TrainerUpdate, 
    TrainerResponse,
    TrainerListResponse,
    TrainerWithCustomersResponse
)
from app.schemas.user import UserResponse


@pytest.mark.unit
@pytest.mark.schema
class TestTrainerBase:
    """Test TrainerBase schema"""
    
    def test_valid_trainer_base(self):
        """Test valid TrainerBase creation"""
        trainer_data = {
            "profile_picture_url": "https://example.com/trainer.jpg"
        }
        
        trainer = TrainerBase(**trainer_data)
        
        assert trainer.profile_picture_url == "https://example.com/trainer.jpg"
    
    def test_trainer_base_minimal(self):
        """Test TrainerBase with minimal data (all optional)"""
        trainer = TrainerBase()
        
        assert trainer.profile_picture_url is None
    
    def test_trainer_base_none_profile_pic(self):
        """Test TrainerBase with None profile picture"""
        trainer = TrainerBase(profile_picture_url=None)
        
        assert trainer.profile_picture_url is None


@pytest.mark.unit
@pytest.mark.schema
class TestTrainerCreate:
    """Test TrainerCreate schema"""
    
    def test_valid_trainer_create(self):
        """Test valid TrainerCreate"""
        user_id = uuid4()
        
        trainer_data = {
            "user_id": user_id,
            "profile_picture_url": "https://example.com/trainer.jpg"
        }
        
        trainer = TrainerCreate(**trainer_data)
        
        assert trainer.user_id == user_id
        assert trainer.profile_picture_url == "https://example.com/trainer.jpg"
    
    def test_trainer_create_minimal(self):
        """Test TrainerCreate with only required field"""
        user_id = uuid4()
        
        trainer = TrainerCreate(user_id=user_id)
        
        assert trainer.user_id == user_id
        assert trainer.profile_picture_url is None
    
    def test_trainer_create_missing_user_id(self):
        """Test TrainerCreate without required user_id"""
        with pytest.raises(ValidationError) as exc_info:
            TrainerCreate()
        
        assert "user_id" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestTrainerUpdate:
    """Test TrainerUpdate schema"""
    
    def test_valid_trainer_update(self):
        """Test valid TrainerUpdate"""
        update_data = {
            "profile_picture_url": "https://example.com/newtrainer.jpg"
        }
        
        trainer_update = TrainerUpdate(**update_data)
        
        assert trainer_update.profile_picture_url == "https://example.com/newtrainer.jpg"
    
    def test_empty_trainer_update(self):
        """Test TrainerUpdate with no fields"""
        trainer_update = TrainerUpdate()
        
        assert trainer_update.profile_picture_url is None
    
    def test_trainer_update_remove_picture(self):
        """Test TrainerUpdate to remove profile picture"""
        trainer_update = TrainerUpdate(profile_picture_url=None)
        
        assert trainer_update.profile_picture_url is None


@pytest.mark.unit
@pytest.mark.schema
class TestTrainerResponse:
    """Test TrainerResponse schema"""
    
    def test_trainer_response_creation(self):
        """Test TrainerResponse creation"""
        user_id = uuid4()
        
        user_data = {
            "id": user_id,
            "email": "trainer@example.com",
            "first_name": "Jane",
            "last_name": "Trainer",
            "phone_number": "987-654-3210",
            "location": "Trainer City", 
            "active": True,
            "roles": ["Trainer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        trainer_data = {
            "user_id": user_id,
            "profile_picture_url": "https://example.com/trainer.jpg",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None,
            "user": user_data
        }
        
        trainer_response = TrainerResponse(**trainer_data)
        
        assert trainer_response.user_id == user_id
        assert trainer_response.profile_picture_url == "https://example.com/trainer.jpg"
        assert trainer_response.user.email == "trainer@example.com"
        assert trainer_response.user.first_name == "Jane"
    
    def test_trainer_response_no_profile_pic(self):
        """Test TrainerResponse without profile picture"""
        user_id = uuid4()
        
        user_data = {
            "id": user_id,
            "email": "trainer@example.com",
            "first_name": "Jane",
            "last_name": "Trainer",
            "phone_number": None,
            "location": None,
            "active": True,
            "roles": ["Trainer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        trainer_data = {
            "user_id": user_id,
            "profile_picture_url": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None,
            "user": user_data
        }
        
        trainer_response = TrainerResponse(**trainer_data)
        
        assert trainer_response.profile_picture_url is None
        assert trainer_response.user.email == "trainer@example.com"


@pytest.mark.unit
@pytest.mark.schema
class TestTrainerListResponse:
    """Test TrainerListResponse schema"""
    
    def test_trainer_list_response(self):
        """Test TrainerListResponse creation"""
        user_id = uuid4()
        
        user_data = {
            "id": user_id,
            "email": "trainer@example.com",
            "first_name": "Jane",
            "last_name": "Trainer",
            "phone_number": "987-654-3210",
            "location": "Trainer City",
            "active": True,
            "roles": ["Trainer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        trainer_data = {
            "user_id": user_id,
            "profile_picture_url": "https://example.com/trainer.jpg",
            "created_at": datetime.now(timezone.utc),
            "user": user_data
        }
        
        trainer_list = TrainerListResponse(**trainer_data)
        
        assert trainer_list.user_id == user_id
        assert trainer_list.profile_picture_url == "https://example.com/trainer.jpg"
        assert trainer_list.user.email == "trainer@example.com"


@pytest.mark.unit
@pytest.mark.schema
class TestTrainerWithCustomersResponse:
    """Test TrainerWithCustomersResponse schema"""
    
    def test_trainer_with_customers(self):
        """Test TrainerWithCustomersResponse with customers"""
        user_id = uuid4()
        customer_user_id = uuid4()
        
        user_data = {
            "id": user_id,
            "email": "trainer@example.com",
            "first_name": "Jane",
            "last_name": "Trainer",
            "phone_number": "987-654-3210",
            "location": "Trainer City",
            "active": True,
            "roles": ["Trainer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        customer_user_data = {
            "id": customer_user_id,
            "email": "customer@example.com",
            "first_name": "John",
            "last_name": "Customer",
            "phone_number": "123-456-7890",
            "location": "Customer City",
            "active": True,
            "roles": ["Customer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        customer_data = {
            "user_id": customer_user_id,
            "trainer_id": user_id,
            "profile_picture_url": "https://example.com/customer.jpg",
            "created_at": datetime.now(timezone.utc),
            "user": customer_user_data
        }
        
        trainer_data = {
            "user_id": user_id,
            "profile_picture_url": "https://example.com/trainer.jpg",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None,
            "user": user_data,
            "customers": [customer_data]
        }
        
        trainer_with_customers = TrainerWithCustomersResponse(**trainer_data)
        
        assert trainer_with_customers.user_id == user_id
        assert trainer_with_customers.user.email == "trainer@example.com"
        assert len(trainer_with_customers.customers) == 1
        assert trainer_with_customers.customers[0].user.email == "customer@example.com"
        assert trainer_with_customers.customers[0].trainer_id == user_id
    
    def test_trainer_with_no_customers(self):
        """Test TrainerWithCustomersResponse with no customers"""
        user_id = uuid4()
        
        user_data = {
            "id": user_id,
            "email": "trainer@example.com",
            "first_name": "Jane",
            "last_name": "Trainer",
            "phone_number": None,
            "location": None,
            "active": True,
            "roles": ["Trainer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        trainer_data = {
            "user_id": user_id,
            "profile_picture_url": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None,
            "user": user_data,
            "customers": []
        }
        
        trainer_with_customers = TrainerWithCustomersResponse(**trainer_data)
        
        assert trainer_with_customers.user_id == user_id
        assert len(trainer_with_customers.customers) == 0
    
    def test_trainer_default_empty_customers(self):
        """Test TrainerWithCustomersResponse with default empty customers"""
        user_id = uuid4()
        
        user_data = {
            "id": user_id,
            "email": "trainer@example.com",
            "first_name": "Jane",
            "last_name": "Trainer",
            "phone_number": None,
            "location": None,
            "active": True,
            "roles": ["Trainer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        trainer_data = {
            "user_id": user_id,
            "profile_picture_url": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None,
            "user": user_data
            # customers not provided - should default to []
        }
        
        trainer_with_customers = TrainerWithCustomersResponse(**trainer_data)
        
        assert len(trainer_with_customers.customers) == 0