import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime, timezone

from app.schemas.customer import (
    CustomerBase,
    CustomerCreate, 
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    CustomerAssignTrainer
)
from app.schemas.user import UserResponse


@pytest.mark.unit
@pytest.mark.schema
class TestCustomerBase:
    """Test CustomerBase schema"""
    
    def test_valid_customer_base(self):
        """Test valid CustomerBase creation"""
        customer_data = {
            "trainer_id": uuid4(),
            "profile_picture_url": "https://example.com/pic.jpg",
            "profile_data": {"height": "180cm", "weight": "75kg"}
        }
        
        customer = CustomerBase(**customer_data)
        
        assert customer.trainer_id == customer_data["trainer_id"]
        assert customer.profile_picture_url == "https://example.com/pic.jpg"
        assert customer.profile_data == {"height": "180cm", "weight": "75kg"}
    
    def test_customer_base_minimal_data(self):
        """Test CustomerBase with minimal data (all optional)"""
        customer = CustomerBase()
        
        assert customer.trainer_id is None
        assert customer.profile_picture_url is None
        assert customer.profile_data == {}  # Default empty dict
    
    def test_customer_base_none_trainer(self):
        """Test CustomerBase with None trainer_id"""
        customer = CustomerBase(trainer_id=None)
        assert customer.trainer_id is None


@pytest.mark.unit
@pytest.mark.schema
class TestCustomerCreate:
    """Test CustomerCreate schema"""
    
    def test_valid_customer_create(self):
        """Test valid CustomerCreate"""
        user_id = uuid4()
        trainer_id = uuid4()
        
        customer_data = {
            "user_id": user_id,
            "trainer_id": trainer_id,
            "profile_picture_url": "https://example.com/pic.jpg",
            "profile_data": {"age": 25, "goals": "weight loss"}
        }
        
        customer = CustomerCreate(**customer_data)
        
        assert customer.user_id == user_id
        assert customer.trainer_id == trainer_id
        assert customer.profile_picture_url == "https://example.com/pic.jpg"
        assert customer.profile_data == {"age": 25, "goals": "weight loss"}
    
    def test_customer_create_minimal(self):
        """Test CustomerCreate with only required field"""
        user_id = uuid4()
        
        customer = CustomerCreate(user_id=user_id)
        
        assert customer.user_id == user_id
        assert customer.trainer_id is None
        assert customer.profile_picture_url is None
        assert customer.profile_data == {}
    
    def test_profile_data_validator_none(self):
        """Test profile_data validator with None"""
        user_id = uuid4()
        
        customer = CustomerCreate(user_id=user_id, profile_data=None)
        
        assert customer.profile_data == {}
    
    def test_profile_data_validator_empty_dict(self):
        """Test profile_data validator with empty dict"""
        user_id = uuid4()
        
        customer = CustomerCreate(user_id=user_id, profile_data={})
        
        assert customer.profile_data == {}


@pytest.mark.unit  
@pytest.mark.schema
class TestCustomerUpdate:
    """Test CustomerUpdate schema"""
    
    def test_valid_customer_update(self):
        """Test valid CustomerUpdate"""
        trainer_id = uuid4()
        
        update_data = {
            "trainer_id": trainer_id,
            "profile_picture_url": "https://example.com/newpic.jpg",
            "profile_data": {"updated": True}
        }
        
        customer_update = CustomerUpdate(**update_data)
        
        assert customer_update.trainer_id == trainer_id
        assert customer_update.profile_picture_url == "https://example.com/newpic.jpg"
        assert customer_update.profile_data == {"updated": True}
    
    def test_empty_customer_update(self):
        """Test CustomerUpdate with no fields"""
        customer_update = CustomerUpdate()
        
        assert customer_update.trainer_id is None
        assert customer_update.profile_picture_url is None
        assert customer_update.profile_data is None
    
    def test_customer_update_unassign_trainer(self):
        """Test CustomerUpdate to unassign trainer"""
        customer_update = CustomerUpdate(trainer_id=None)
        
        assert customer_update.trainer_id is None
    
    def test_profile_data_validator_none_update(self):
        """Test CustomerUpdate profile_data validator with None"""
        customer_update = CustomerUpdate(profile_data=None)
        
        assert customer_update.profile_data == {}


@pytest.mark.unit
@pytest.mark.schema  
class TestCustomerResponse:
    """Test CustomerResponse schema"""
    
    def test_customer_response_creation(self):
        """Test CustomerResponse creation"""
        user_id = uuid4()
        trainer_id = uuid4()
        
        # Create mock user data
        user_data = {
            "id": user_id,
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
        
        trainer_data = {
            "id": trainer_id,
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
        
        customer_data = {
            "user_id": user_id,
            "trainer_id": trainer_id,
            "profile_picture_url": "https://example.com/pic.jpg",
            "profile_data": {"height": "180cm"},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None,
            "user": user_data,
            "trainer": trainer_data
        }
        
        customer_response = CustomerResponse(**customer_data)
        
        assert customer_response.user_id == user_id
        assert customer_response.trainer_id == trainer_id
        assert customer_response.profile_picture_url == "https://example.com/pic.jpg"
        assert customer_response.user.email == "customer@example.com"
        assert customer_response.trainer.email == "trainer@example.com"
    
    def test_customer_response_no_trainer(self):
        """Test CustomerResponse without trainer"""
        user_id = uuid4()
        
        user_data = {
            "id": user_id,
            "email": "customer@example.com",
            "first_name": "John",
            "last_name": "Customer",
            "phone_number": None,
            "location": None,
            "active": True,
            "roles": ["Customer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        customer_data = {
            "user_id": user_id,
            "trainer_id": None,
            "profile_picture_url": None,
            "profile_data": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None,
            "user": user_data,
            "trainer": None
        }
        
        customer_response = CustomerResponse(**customer_data)
        
        assert customer_response.trainer_id is None
        assert customer_response.trainer is None
        assert customer_response.user.email == "customer@example.com"


@pytest.mark.unit
@pytest.mark.schema
class TestCustomerListResponse:
    """Test CustomerListResponse schema"""
    
    def test_customer_list_response(self):
        """Test CustomerListResponse creation"""
        user_id = uuid4()
        trainer_id = uuid4()
        
        user_data = {
            "id": user_id,
            "email": "customer@example.com",
            "first_name": "John",
            "last_name": "Customer",
            "phone_number": None,
            "location": None,
            "active": True,
            "roles": ["Customer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        customer_data = {
            "user_id": user_id,
            "trainer_id": trainer_id,
            "profile_picture_url": "https://example.com/pic.jpg",
            "created_at": datetime.now(timezone.utc),
            "user": user_data
        }
        
        customer_list = CustomerListResponse(**customer_data)
        
        assert customer_list.user_id == user_id
        assert customer_list.trainer_id == trainer_id
        assert customer_list.user.email == "customer@example.com"


@pytest.mark.unit
@pytest.mark.schema
class TestCustomerAssignTrainer:
    """Test CustomerAssignTrainer schema"""
    
    def test_assign_trainer(self):
        """Test assigning a trainer"""
        trainer_id = uuid4()
        
        assign_data = CustomerAssignTrainer(trainer_id=trainer_id)
        
        assert assign_data.trainer_id == trainer_id
    
    def test_unassign_trainer(self):
        """Test unassigning a trainer (None)"""
        assign_data = CustomerAssignTrainer(trainer_id=None)
        
        assert assign_data.trainer_id is None
    
    def test_default_none(self):
        """Test default None value"""
        assign_data = CustomerAssignTrainer()
        
        assert assign_data.trainer_id is None