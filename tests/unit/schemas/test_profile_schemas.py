import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime, timezone

from app.schemas.profile import (
    ProfileBase,
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    ProfileSummary,
    PreferenceUpdate
)


@pytest.mark.unit
@pytest.mark.schema
class TestProfileBase:
    """Test ProfileBase schema"""
    
    def test_valid_profile_base(self):
        """Test valid ProfileBase creation"""
        profile_data = {
            "profile_picture_url": "https://example.com/profile.jpg",
            "bio": "I love fitness and helping others!",
            "emergency_contact": "Jane Doe - 555-1234",
            "preferences": {"theme": "dark", "notifications": True}
        }
        
        profile = ProfileBase(**profile_data)
        
        assert profile.profile_picture_url == "https://example.com/profile.jpg"
        assert profile.bio == "I love fitness and helping others!"
        assert profile.emergency_contact == "Jane Doe - 555-1234"
        assert profile.preferences == {"theme": "dark", "notifications": True}
    
    def test_profile_base_minimal_data(self):
        """Test ProfileBase with minimal data (all optional)"""
        profile = ProfileBase()
        
        assert profile.profile_picture_url is None
        assert profile.bio is None
        assert profile.emergency_contact is None
        assert profile.preferences == {}  # Default empty dict
    
    def test_bio_length_validation_valid(self):
        """Test bio length validation passes for valid length"""
        bio = "A" * 1000  # Exactly 1000 characters
        profile = ProfileBase(bio=bio)
        assert len(profile.bio) == 1000
    
    def test_bio_length_validation_too_long(self):
        """Test bio length validation fails for too long bio"""
        bio = "A" * 1001  # 1001 characters
        
        with pytest.raises(ValidationError) as exc_info:
            ProfileBase(bio=bio)
        
        assert "Bio must be 1000 characters or less" in str(exc_info.value)
    
    def test_profile_picture_url_validation_http(self):
        """Test profile picture URL validation with http"""
        profile = ProfileBase(profile_picture_url="http://example.com/pic.jpg")
        assert profile.profile_picture_url == "http://example.com/pic.jpg"
    
    def test_profile_picture_url_validation_https(self):
        """Test profile picture URL validation with https"""
        profile = ProfileBase(profile_picture_url="https://example.com/pic.jpg")
        assert profile.profile_picture_url == "https://example.com/pic.jpg"
    
    def test_profile_picture_url_validation_invalid(self):
        """Test profile picture URL validation fails for invalid URL"""
        with pytest.raises(ValidationError) as exc_info:
            ProfileBase(profile_picture_url="ftp://example.com/pic.jpg")
        
        assert "Profile picture URL must start with http:// or https://" in str(exc_info.value)
    
    def test_preferences_validation_valid_dict(self):
        """Test preferences validation with valid dictionary"""
        prefs = {"theme": "dark", "notifications": True, "count": 42}
        profile = ProfileBase(preferences=prefs)
        assert profile.preferences == prefs
    
    def test_preferences_validation_none(self):
        """Test preferences validation with None"""
        profile = ProfileBase(preferences=None)
        assert profile.preferences == {}
    
    def test_preferences_validation_invalid_type(self):
        """Test preferences validation fails for non-dict"""
        with pytest.raises(ValidationError) as exc_info:
            ProfileBase(preferences="not a dict")
        
        assert "Preferences must be a dictionary" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestProfileCreate:
    """Test ProfileCreate schema"""
    
    def test_valid_profile_create(self):
        """Test valid ProfileCreate"""
        user_id = uuid4()
        profile_data = {
            "user_id": user_id,
            "profile_picture_url": "https://example.com/pic.jpg",
            "bio": "Fitness enthusiast",
            "emergency_contact": "John Doe - 555-9876",
            "preferences": {"language": "en"}
        }
        
        profile = ProfileCreate(**profile_data)
        
        assert profile.user_id == user_id
        assert profile.profile_picture_url == "https://example.com/pic.jpg"
        assert profile.bio == "Fitness enthusiast"
        assert profile.emergency_contact == "John Doe - 555-9876"
        assert profile.preferences == {"language": "en"}
    
    def test_profile_create_minimal(self):
        """Test ProfileCreate with only required field"""
        user_id = uuid4()
        
        profile = ProfileCreate(user_id=user_id)
        
        assert profile.user_id == user_id
        assert profile.profile_picture_url is None
        assert profile.bio is None
        assert profile.emergency_contact is None
        assert profile.preferences == {}
    
    def test_profile_create_missing_user_id(self):
        """Test ProfileCreate without required user_id"""
        with pytest.raises(ValidationError) as exc_info:
            ProfileCreate()
        
        assert "user_id" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestProfileUpdate:
    """Test ProfileUpdate schema"""
    
    def test_valid_profile_update(self):
        """Test valid ProfileUpdate"""
        update_data = {
            "profile_picture_url": "https://example.com/newpic.jpg",
            "bio": "Updated bio",
            "emergency_contact": "Jane Smith - 555-4321",
            "preferences": {"theme": "light"}
        }
        
        profile_update = ProfileUpdate(**update_data)
        
        assert profile_update.profile_picture_url == "https://example.com/newpic.jpg"
        assert profile_update.bio == "Updated bio"
        assert profile_update.emergency_contact == "Jane Smith - 555-4321"
        assert profile_update.preferences == {"theme": "light"}
    
    def test_empty_profile_update(self):
        """Test ProfileUpdate with no fields"""
        profile_update = ProfileUpdate()
        
        assert profile_update.profile_picture_url is None
        assert profile_update.bio is None
        assert profile_update.emergency_contact is None
        assert profile_update.preferences == {}  # Validator converts None to {}
    
    def test_partial_profile_update(self):
        """Test ProfileUpdate with some fields"""
        profile_update = ProfileUpdate(bio="New bio", preferences={"notifications": False})
        
        assert profile_update.bio == "New bio"
        assert profile_update.preferences == {"notifications": False}
        assert profile_update.profile_picture_url is None
        assert profile_update.emergency_contact is None
    
    def test_profile_update_bio_validation(self):
        """Test ProfileUpdate bio length validation"""
        bio_too_long = "A" * 1001
        
        with pytest.raises(ValidationError) as exc_info:
            ProfileUpdate(bio=bio_too_long)
        
        assert "Bio must be 1000 characters or less" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestProfileResponse:
    """Test ProfileResponse schema"""
    
    def test_profile_response_creation(self):
        """Test ProfileResponse creation"""
        user_id = uuid4()
        
        user_data = {
            "id": user_id,
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "User",
            "phone_number": "555-1234",
            "location": "City",
            "active": True,
            "roles": ["Customer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        profile_data = {
            "user_id": user_id,
            "profile_picture_url": "https://example.com/pic.jpg",
            "bio": "Fitness lover",
            "emergency_contact": "Emergency - 555-9999",
            "preferences": {"theme": "dark"},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "user": user_data
        }
        
        profile_response = ProfileResponse(**profile_data)
        
        assert profile_response.user_id == user_id
        assert profile_response.bio == "Fitness lover"
        assert profile_response.user.email == "user@example.com"
        assert profile_response.preferences == {"theme": "dark"}


@pytest.mark.unit
@pytest.mark.schema
class TestProfileSummary:
    """Test ProfileSummary schema"""
    
    def test_profile_summary_creation(self):
        """Test ProfileSummary creation"""
        user_id = uuid4()
        
        summary_data = {
            "user_id": user_id,
            "profile_picture_url": "https://example.com/pic.jpg",
            "bio": "Short bio",
            "has_emergency_contact": True,
            "is_complete": True
        }
        
        summary = ProfileSummary(**summary_data)
        
        assert summary.user_id == user_id
        assert summary.profile_picture_url == "https://example.com/pic.jpg"
        assert summary.bio == "Short bio"
        assert summary.has_emergency_contact is True
        assert summary.is_complete is True
    
    def test_profile_summary_minimal(self):
        """Test ProfileSummary with minimal data"""
        user_id = uuid4()
        
        summary = ProfileSummary(user_id=user_id)
        
        assert summary.user_id == user_id
        assert summary.profile_picture_url is None
        assert summary.bio is None
        assert summary.has_emergency_contact is False
        assert summary.is_complete is False


@pytest.mark.unit
@pytest.mark.schema
class TestPreferenceUpdate:
    """Test PreferenceUpdate schema"""
    
    def test_valid_preference_update(self):
        """Test valid PreferenceUpdate"""
        pref_update = PreferenceUpdate(key="theme", value="dark")
        
        assert pref_update.key == "theme"
        assert pref_update.value == "dark"
    
    def test_preference_update_different_types(self):
        """Test PreferenceUpdate with different value types"""
        # String value
        pref1 = PreferenceUpdate(key="theme", value="dark")
        assert pref1.value == "dark"
        
        # Boolean value
        pref2 = PreferenceUpdate(key="notifications", value=True)
        assert pref2.value is True
        
        # Integer value
        pref3 = PreferenceUpdate(key="count", value=42)
        assert pref3.value == 42
        
        # Dict value
        pref4 = PreferenceUpdate(key="config", value={"max": 10})
        assert pref4.value == {"max": 10}
    
    def test_preference_update_empty_key(self):
        """Test PreferenceUpdate with empty key"""
        with pytest.raises(ValidationError) as exc_info:
            PreferenceUpdate(key="", value="some_value")
        
        assert "Preference key cannot be empty" in str(exc_info.value)
    
    def test_preference_update_whitespace_key(self):
        """Test PreferenceUpdate with whitespace-only key"""
        with pytest.raises(ValidationError) as exc_info:
            PreferenceUpdate(key="   ", value="some_value")
        
        assert "Preference key cannot be empty" in str(exc_info.value)
    
    def test_preference_update_key_too_long(self):
        """Test PreferenceUpdate with key too long"""
        long_key = "a" * 101  # 101 characters
        
        with pytest.raises(ValidationError) as exc_info:
            PreferenceUpdate(key=long_key, value="value")
        
        assert "Preference key must be 100 characters or less" in str(exc_info.value)
    
    def test_preference_update_key_trimmed(self):
        """Test PreferenceUpdate trims whitespace from key"""
        pref_update = PreferenceUpdate(key="  theme  ", value="dark")
        
        assert pref_update.key == "theme"  # Whitespace trimmed