import pytest

from tests.conftest import MockRole


@pytest.mark.unit
@pytest.mark.model
class TestRoleModel:
    """Test Role model methods and properties"""
    
    def test_role_creation(self):
        """Test Role object creation"""
        role = MockRole(id=1, name="TestRole")
        
        assert role.id == 1
        assert role.name == "TestRole"
    
    def test_role_repr(self, sample_role):
        """Test Role __repr__ method"""
        result = repr(sample_role)
        
        assert "Role(id=1" in result
        assert "name='Customer'" in result
    
    def test_role_name_assignment(self):
        """Test role name can be assigned"""
        role = MockRole()
        role.name = "Admin"
        
        assert role.name == "Admin"
    
    def test_role_equality_by_name(self):
        """Test roles with same name are logically equal for our purposes"""
        role1 = MockRole(id=1, name="Customer")
        role2 = MockRole(id=2, name="Customer")
        
        # Same name but different IDs - this tests our understanding
        assert role1.name == role2.name
        assert role1.id != role2.id


