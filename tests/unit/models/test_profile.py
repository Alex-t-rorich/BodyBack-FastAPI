import pytest
from uuid import uuid4
from datetime import datetime, timezone

from tests.conftest import MockUser


class MockProfile:
    """Mock Profile object that behaves like SQLAlchemy model"""
    def __init__(self):
        self.user_id = uuid4()
        self.profile_picture_url = None
        self.bio = None
        self.emergency_contact = None
        self.preferences = {}
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.user = None
    
    def __repr__(self):
        bio_length = len(self.bio) if self.bio else 0
        return f"<Profile(user_id={self.user_id}, bio_length={bio_length})>"
    
    @property
    def is_complete(self) -> bool:
        """Check if profile has essential information"""
        return bool(self.bio and self.profile_picture_url)
    
    def has_emergency_contact(self) -> bool:
        """Check if profile has emergency contact information"""
        return bool(self.emergency_contact)
    
    def get_preference(self, key: str, default=None):
        """Get a specific preference value"""
        if not self.preferences:
            return default
        return self.preferences.get(key, default)
    
    def set_preference(self, key: str, value):
        """Set a specific preference value"""
        if not self.preferences:
            self.preferences = {}
        self.preferences[key] = value


@pytest.fixture
def sample_profile():
    """Create a sample Profile object"""
    profile = MockProfile()
    profile.bio = "I love fitness and helping others achieve their goals!"
    profile.profile_picture_url = "https://example.com/profile.jpg"
    profile.emergency_contact = "John Doe - 555-1234"
    profile.preferences = {"theme": "dark", "notifications": True}
    return profile


@pytest.fixture
def incomplete_profile():
    """Create an incomplete Profile object"""
    profile = MockProfile()
    profile.bio = None
    profile.profile_picture_url = None
    return profile


@pytest.mark.unit
@pytest.mark.model
class TestProfileModel:
    """Test Profile model methods and properties"""
    
    def test_profile_repr(self, sample_profile):
        """Test Profile __repr__ method"""
        result = repr(sample_profile)
        
        assert "Profile(user_id=" in result
        assert "bio_length=54" in result
    
    def test_profile_repr_no_bio(self, incomplete_profile):
        """Test Profile __repr__ with no bio"""
        result = repr(incomplete_profile)
        
        assert "Profile(user_id=" in result
        assert "bio_length=0" in result
    
    def test_is_complete_true(self, sample_profile):
        """Test is_complete property returns True when profile has bio and picture"""
        assert sample_profile.is_complete is True
    
    def test_is_complete_false_no_bio(self, incomplete_profile):
        """Test is_complete property returns False when no bio"""
        incomplete_profile.profile_picture_url = "https://example.com/pic.jpg"
        assert incomplete_profile.is_complete is False
    
    def test_is_complete_false_no_picture(self, incomplete_profile):
        """Test is_complete property returns False when no picture"""
        incomplete_profile.bio = "Some bio"
        assert incomplete_profile.is_complete is False
    
    def test_is_complete_false_both_missing(self, incomplete_profile):
        """Test is_complete property returns False when both missing"""
        assert incomplete_profile.is_complete is False
    
    def test_has_emergency_contact_true(self, sample_profile):
        """Test has_emergency_contact returns True when contact exists"""
        assert sample_profile.has_emergency_contact() is True
    
    def test_has_emergency_contact_false(self, incomplete_profile):
        """Test has_emergency_contact returns False when no contact"""
        assert incomplete_profile.has_emergency_contact() is False
    
    def test_has_emergency_contact_empty_string(self, incomplete_profile):
        """Test has_emergency_contact returns False for empty string"""
        incomplete_profile.emergency_contact = ""
        assert incomplete_profile.has_emergency_contact() is False
    
    def test_get_preference_existing(self, sample_profile):
        """Test get_preference returns existing preference"""
        result = sample_profile.get_preference("theme")
        assert result == "dark"
    
    def test_get_preference_non_existing(self, sample_profile):
        """Test get_preference returns default for non-existing preference"""
        result = sample_profile.get_preference("language", "en")
        assert result == "en"
    
    def test_get_preference_no_preferences(self, incomplete_profile):
        """Test get_preference with no preferences dict"""
        incomplete_profile.preferences = None
        result = incomplete_profile.get_preference("theme", "light")
        assert result == "light"
    
    def test_set_preference_existing_dict(self, sample_profile):
        """Test set_preference on existing preferences dict"""
        sample_profile.set_preference("language", "es")
        assert sample_profile.preferences["language"] == "es"
        assert sample_profile.preferences["theme"] == "dark"  # Existing preference unchanged
    
    def test_set_preference_no_dict(self, incomplete_profile):
        """Test set_preference creates preferences dict if None"""
        incomplete_profile.preferences = None
        incomplete_profile.set_preference("theme", "light")
        
        assert incomplete_profile.preferences is not None
        assert incomplete_profile.preferences["theme"] == "light"
    
    def test_set_preference_empty_dict(self, incomplete_profile):
        """Test set_preference on empty preferences dict"""
        incomplete_profile.preferences = {}
        incomplete_profile.set_preference("notifications", False)
        
        assert incomplete_profile.preferences["notifications"] is False
    
    def test_preferences_types(self, sample_profile):
        """Test preferences can store different data types"""
        sample_profile.set_preference("count", 42)
        sample_profile.set_preference("enabled", True)
        sample_profile.set_preference("tags", ["fitness", "health"])
        sample_profile.set_preference("config", {"max_items": 10})
        
        assert sample_profile.get_preference("count") == 42
        assert sample_profile.get_preference("enabled") is True
        assert sample_profile.get_preference("tags") == ["fitness", "health"]
        assert sample_profile.get_preference("config") == {"max_items": 10}
    
    def test_preferences_overwrite(self, sample_profile):
        """Test that setting an existing preference overwrites it"""
        original_theme = sample_profile.get_preference("theme")
        assert original_theme == "dark"
        
        sample_profile.set_preference("theme", "light")
        new_theme = sample_profile.get_preference("theme")
        assert new_theme == "light"