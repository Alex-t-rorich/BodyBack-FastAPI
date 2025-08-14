import pytest
from uuid import uuid4
from datetime import datetime

from app.models.user import User
from app.models.role import Role


@pytest.mark.unit
@pytest.mark.model
class TestUserModel:
    """Test User model methods and properties"""
    
    def test_user_repr(self, sample_user, sample_role):
        """Test User __repr__ method"""
        sample_user.role = sample_role
        result = repr(sample_user)
        
        assert "User(id=" in result
        assert "test@example.com" in result
        assert "Customer" in result
    
    def test_user_repr_no_roles(self, sample_user):
        """Test User __repr__ with no role"""
        result = repr(sample_user)
        
        assert "User(id=" in result
        assert "test@example.com" in result
        assert "No Role" in result
    
    def test_full_name_with_both_names(self, sample_user):
        """Test full_name property when both first and last name exist"""
        assert sample_user.full_name == "Test User"
    
    def test_full_name_with_first_name_only(self, sample_user):
        """Test full_name property with only first name"""
        sample_user.last_name = None
        assert sample_user.full_name == "test@example.com"
    
    def test_full_name_with_last_name_only(self, sample_user):
        """Test full_name property with only last name"""
        sample_user.first_name = None
        assert sample_user.full_name == "test@example.com"
    
    def test_full_name_with_no_names(self, sample_user):
        """Test full_name property with no names"""
        sample_user.first_name = None
        sample_user.last_name = None
        assert sample_user.full_name == "test@example.com"
    
    def test_role_name_property_with_role(self, user_with_customer_role):
        """Test role_name property with role"""
        role_name = user_with_customer_role.role_name
        
        assert isinstance(role_name, str)
        assert role_name == "Customer"
    
    def test_role_name_property_no_role(self, sample_user):
        """Test role_name property with no role"""
        role_name = sample_user.role_name
        
        assert role_name is None
    
    def test_has_role_true(self, user_with_customer_role):
        """Test has_role method returns True for existing role"""
        assert user_with_customer_role.has_role("Customer") is True
    
    def test_has_role_false(self, user_with_customer_role):
        """Test has_role method returns False for non-existing role"""
        assert user_with_customer_role.has_role("Admin") is False
    
    def test_has_role_no_role(self, sample_user):
        """Test has_role method with no role"""
        assert sample_user.has_role("Customer") is False
    
    def test_has_role_case_sensitive(self, user_with_customer_role):
        """Test has_role method is case sensitive"""
        assert user_with_customer_role.has_role("customer") is False
        assert user_with_customer_role.has_role("Customer") is True
    
    def test_is_trainer_true(self, sample_user, trainer_role):
        """Test is_trainer method returns True"""
        sample_user.role = trainer_role
        assert sample_user.is_trainer() is True
    
    def test_is_trainer_false(self, user_with_customer_role):
        """Test is_trainer method returns False"""
        assert user_with_customer_role.is_trainer() is False
    
    def test_is_customer_true(self, user_with_customer_role):
        """Test is_customer method returns True"""
        assert user_with_customer_role.is_customer() is True
    
    def test_is_customer_false(self, user_with_admin_role):
        """Test is_customer method returns False"""
        assert user_with_admin_role.is_customer() is False
    
    def test_is_admin_true(self, user_with_admin_role):
        """Test is_admin method returns True"""
        assert user_with_admin_role.is_admin() is True
    
    def test_is_admin_false(self, user_with_customer_role):
        """Test is_admin method returns False"""
        assert user_with_customer_role.is_admin() is False
    
    def test_single_role_behavior(self, user_with_customer_role):
        """Test behavior with single role"""
        assert user_with_customer_role.is_customer() is True
        assert user_with_customer_role.is_trainer() is False
        assert user_with_customer_role.is_admin() is False
        assert user_with_customer_role.has_role("Customer") is True
        assert user_with_customer_role.has_role("Trainer") is False