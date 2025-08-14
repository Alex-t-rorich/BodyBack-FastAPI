import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime, timezone

from app.schemas.user import (
    UserBase, 
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserLogin, 
    UserPasswordUpdate
)


@pytest.mark.unit
@pytest.mark.schema
class TestUserBase:
    """Test UserBase schema"""
    
    def test_valid_user_base(self):
        """Test valid UserBase creation"""
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "123-456-7890",
            "location": "Test City",
            "active": True
        }
        
        user = UserBase(**user_data)
        
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.phone_number == "123-456-7890"
        assert user.location == "Test City"
        assert user.active is True
    
    def test_user_base_minimal_data(self):
        """Test UserBase with minimal required data"""
        user = UserBase(email="test@example.com")
        
        assert user.email == "test@example.com"
        assert user.first_name is None
        assert user.last_name is None
        assert user.phone_number is None
        assert user.location is None
        assert user.active is True  # Default value
    
    def test_invalid_email(self):
        """Test UserBase with invalid email"""
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="invalid-email")
        
        assert "email" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestUserCreate:
    """Test UserCreate schema"""
    
    def test_valid_user_create(self):
        """Test valid UserCreate"""
        user_data = {
            "email": "test@example.com",
            "password": "strongpassword123",
            "role": "Customer",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        user = UserCreate(**user_data)
        
        assert user.email == "test@example.com"
        assert user.password == "strongpassword123"
        assert user.role == "Customer"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
    
    def test_password_too_short(self):
        """Test password validation - too short"""
        user_data = {
            "email": "test@example.com",
            "password": "short",
            "role": "Customer"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "Password must be at least 8 characters long" in str(exc_info.value)
    
    def test_valid_password_length(self):
        """Test valid password length"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",  # Exactly 8 characters
            "role": "Customer"
        }
        
        user = UserCreate(**user_data)
        assert user.password == "password123"
    
    def test_missing_role_validation(self):
        """Test role validation - missing role"""
        user_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "Field required" in str(exc_info.value)
    
    def test_invalid_role_validation(self):
        """Test role validation - invalid role"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "role": "InvalidRole"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "Invalid role: InvalidRole" in str(exc_info.value)
    
    def test_valid_roles(self):
        """Test all valid roles"""
        for role in ["Admin", "Trainer", "Customer"]:
            user_data = {
                "email": "test@example.com",
                "password": "password123",
                "role": role
            }
            
            user = UserCreate(**user_data)
            assert user.role == role
    
    def test_role_assignment(self):
        """Test single role assignment"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "role": "Admin"
        }
        
        user = UserCreate(**user_data)
        assert user.role == "Admin"


@pytest.mark.unit
@pytest.mark.schema
class TestUserUpdate:
    """Test UserUpdate schema"""
    
    def test_valid_user_update(self):
        """Test valid UserUpdate"""
        update_data = {
            "email": "newemail@example.com",
            "first_name": "Updated",
            "active": False,
            "role": "Admin"
        }
        
        user_update = UserUpdate(**update_data)
        
        assert user_update.email == "newemail@example.com"
        assert user_update.first_name == "Updated"
        assert user_update.active is False
        assert user_update.role == "Admin"
    
    def test_empty_user_update(self):
        """Test UserUpdate with no fields"""
        user_update = UserUpdate()
        
        assert user_update.email is None
        assert user_update.first_name is None
        assert user_update.last_name is None
        assert user_update.phone_number is None
        assert user_update.location is None
        assert user_update.active is None
        assert user_update.role is None
    
    def test_partial_user_update(self):
        """Test UserUpdate with some fields"""
        user_update = UserUpdate(first_name="Updated", active=False)
        
        assert user_update.first_name == "Updated"
        assert user_update.active is False
        assert user_update.email is None
    
    def test_role_validation_none(self):
        """Test UserUpdate role validation with None"""
        user_update = UserUpdate(role=None)
        assert user_update.role is None
    
    def test_role_validation_invalid(self):
        """Test UserUpdate role validation with invalid role"""
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(role="InvalidRole")
        
        assert "Invalid role: InvalidRole" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestUserResponse:
    """Test UserResponse schema"""
    
    def test_user_response_creation(self):
        """Test UserResponse creation from dict"""
        user_data = {
            "id": uuid4(),
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "123-456-7890",
            "location": "Test City",
            "active": True,
            "role": "Customer",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        user_response = UserResponse(**user_data)
        
        assert str(user_response.id) == str(user_data["id"])
        assert user_response.email == "test@example.com"
        assert user_response.role == "Customer"
    
    def test_user_response_with_role_object(self, sample_role):
        """Test UserResponse with Role object (simulating ORM)"""
        user_data = {
            "id": uuid4(),
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": None,
            "location": None,
            "active": True,
            "role": sample_role,  # Role object
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        user_response = UserResponse(**user_data)
        
        # Should convert Role object to role name
        assert user_response.role == "Customer"
    
    def test_user_response_no_role(self):
        """Test UserResponse with no role"""
        user_data = {
            "id": uuid4(),
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": None,
            "location": None,
            "active": True,
            "role": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        user_response = UserResponse(**user_data)
        assert user_response.role is None


@pytest.mark.unit
@pytest.mark.schema
class TestUserLogin:
    """Test UserLogin schema"""
    
    def test_valid_user_login(self):
        """Test valid UserLogin"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        user_login = UserLogin(**login_data)
        
        assert user_login.email == "test@example.com"
        assert user_login.password == "password123"
    
    def test_invalid_email_login(self):
        """Test UserLogin with invalid email"""
        with pytest.raises(ValidationError):
            UserLogin(email="invalid-email", password="password123")


@pytest.mark.unit
@pytest.mark.schema
class TestUserPasswordUpdate:
    """Test UserPasswordUpdate schema"""
    
    def test_valid_password_update(self):
        """Test valid UserPasswordUpdate"""
        password_data = {
            "current_password": "oldpassword",
            "new_password": "newpassword123"
        }
        
        password_update = UserPasswordUpdate(**password_data)
        
        assert password_update.current_password == "oldpassword"
        assert password_update.new_password == "newpassword123"
    
    def test_new_password_too_short(self):
        """Test new password validation"""
        password_data = {
            "current_password": "oldpassword",
            "new_password": "short"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserPasswordUpdate(**password_data)
        
        assert "Password must be at least 8 characters long" in str(exc_info.value)