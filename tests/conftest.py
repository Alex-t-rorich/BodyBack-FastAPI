import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

# Create mock classes that don't require SQLAlchemy session
class MockRole:
    """Mock Role object that behaves like SQLAlchemy model"""
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"



class MockUser:
    """Mock User object that behaves like SQLAlchemy model"""
    def __init__(self):
        self.id = uuid4()
        self.email = "test@example.com"
        self.password_hash = "hashed_password"
        self.first_name = "Test"
        self.last_name = "User"
        self.phone_number = "123-456-7890"
        self.location = "Test City"
        self.active = True
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.deleted_at = None
        self.role = None  # Single role instead of list
        self.role_id = None
    
    def __repr__(self):
        role_name = self.role.name if self.role else 'No Role'
        return f"<User(id={self.id}, email='{self.email}', role={role_name})>"
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    @property
    def role_name(self):
        """Get role name"""
        return self.role.name if self.role else None
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        return bool(self.role and self.role.name == role_name)
    
    def is_trainer(self) -> bool:
        """Check if user is a trainer"""
        return self.has_role("Trainer")
    
    def is_customer(self) -> bool:
        """Check if user is a customer"""
        return self.has_role("Customer")
    
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.has_role("Admin")


@pytest.fixture
def sample_role():
    """Create a sample Role object"""
    return MockRole(id=1, name="Customer")


@pytest.fixture
def admin_role():
    """Create an Admin Role object"""
    return MockRole(id=2, name="Admin")


@pytest.fixture
def trainer_role():
    """Create a Trainer Role object"""
    return MockRole(id=3, name="Trainer")


@pytest.fixture
def sample_user():
    """Create a sample User object without roles"""
    return MockUser()


@pytest.fixture
def user_with_customer_role(sample_user, sample_role):
    """Create a User with Customer role"""
    sample_user.role = sample_role
    sample_user.role_id = sample_role.id
    return sample_user


@pytest.fixture
def user_with_admin_role(sample_user, admin_role):
    """Create a User with Admin role"""
    sample_user.role = admin_role
    sample_user.role_id = admin_role.id
    return sample_user


@pytest.fixture
def user_with_trainer_role(sample_user, trainer_role):
    """Create a User with Trainer role"""
    sample_user.role = trainer_role
    sample_user.role_id = trainer_role.id
    return sample_user


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    return Mock()