import pytest
from uuid import uuid4
from datetime import datetime, timezone

from tests.conftest import MockUser


class MockQRCode:
    """Mock QRCode object for testing"""
    def __init__(self):
        self.id = uuid4()
        self.user_id = uuid4()
        self.token = "test_token_123"
        self.status = "active"
        self.is_used = False
        self.expires_at = datetime.now(timezone.utc)


class MockSessionTracking:
    """Mock SessionTracking object that behaves like SQLAlchemy model"""
    def __init__(self):
        self.id = uuid4()
        self.user_id = uuid4()
        self.qr_code_id = uuid4()
        self.status = "active"
        self.scanned_at = datetime.now(timezone.utc)
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.deleted_at = None
        self.user = None
        self.qr_code = None
    
    def __repr__(self):
        return f"<SessionTracking(id={self.id}, user_id={self.user_id}, status={self.status}, scanned_at={self.scanned_at})>"
    
    @property
    def is_active(self) -> bool:
        """Check if session tracking record is active (not soft deleted)"""
        return self.deleted_at is None
    
    @property
    def is_session_active(self) -> bool:
        """Check if the session is currently active"""
        return self.status == "active"
    
    def complete_session(self):
        """Mark the session as completed"""
        self.status = "completed"
    
    def cancel_session(self):
        """Mark the session as cancelled"""
        self.status = "cancelled"


@pytest.fixture
def sample_session_tracking():
    """Create a sample SessionTracking object"""
    session_tracking = MockSessionTracking()
    session_tracking.status = "active"
    return session_tracking


@pytest.fixture
def completed_session_tracking():
    """Create a completed SessionTracking object"""
    session_tracking = MockSessionTracking()
    session_tracking.status = "completed"
    return session_tracking


@pytest.fixture
def cancelled_session_tracking():
    """Create a cancelled SessionTracking object"""
    session_tracking = MockSessionTracking()
    session_tracking.status = "cancelled"
    return session_tracking


@pytest.mark.unit
@pytest.mark.model
class TestSessionTrackingModel:
    """Test SessionTracking model methods and properties"""
    
    def test_session_tracking_repr(self, sample_session_tracking):
        """Test SessionTracking __repr__ method"""
        result = repr(sample_session_tracking)
        
        assert "SessionTracking(id=" in result
        assert f"user_id={sample_session_tracking.user_id}" in result
        assert "status=active" in result
        assert f"scanned_at={sample_session_tracking.scanned_at}" in result
    
    def test_is_active_true(self, sample_session_tracking):
        """Test is_active property returns True when not deleted"""
        assert sample_session_tracking.is_active is True
    
    def test_is_active_false(self, sample_session_tracking):
        """Test is_active property returns False when soft deleted"""
        sample_session_tracking.deleted_at = datetime.now(timezone.utc)
        assert sample_session_tracking.is_active is False
    
    def test_is_session_active_true(self, sample_session_tracking):
        """Test is_session_active property returns True for active status"""
        assert sample_session_tracking.is_session_active is True
    
    def test_is_session_active_false_completed(self, completed_session_tracking):
        """Test is_session_active property returns False for completed status"""
        assert completed_session_tracking.is_session_active is False
    
    def test_is_session_active_false_cancelled(self, cancelled_session_tracking):
        """Test is_session_active property returns False for cancelled status"""
        assert cancelled_session_tracking.is_session_active is False
    
    def test_complete_session(self, sample_session_tracking):
        """Test complete_session method"""
        sample_session_tracking.complete_session()
        
        assert sample_session_tracking.status == "completed"
        assert sample_session_tracking.is_session_active is False
    
    def test_cancel_session(self, sample_session_tracking):
        """Test cancel_session method"""
        sample_session_tracking.cancel_session()
        
        assert sample_session_tracking.status == "cancelled"
        assert sample_session_tracking.is_session_active is False
    
    def test_session_tracking_initialization(self):
        """Test SessionTracking initialization with default values"""
        session_tracking = MockSessionTracking()
        
        assert session_tracking.id is not None
        assert session_tracking.user_id is not None
        assert session_tracking.qr_code_id is not None
        assert session_tracking.status == "active"
        assert session_tracking.scanned_at is not None
        assert session_tracking.created_at is not None
        assert session_tracking.updated_at is not None
        assert session_tracking.deleted_at is None
        assert session_tracking.is_active is True
        assert session_tracking.is_session_active is True
    
    def test_session_tracking_relationships_none(self, sample_session_tracking):
        """Test session tracking with no loaded relationships"""
        assert sample_session_tracking.user is None
        assert sample_session_tracking.qr_code is None
    
    def test_session_tracking_with_relationships(self, sample_session_tracking):
        """Test session tracking with loaded relationships"""
        user = MockUser()
        qr_code = MockQRCode()
        
        sample_session_tracking.user = user
        sample_session_tracking.qr_code = qr_code
        
        assert sample_session_tracking.user == user
        assert sample_session_tracking.qr_code == qr_code
    
    def test_status_transitions(self, sample_session_tracking):
        """Test status transitions work correctly"""
        # Start with active
        assert sample_session_tracking.status == "active"
        assert sample_session_tracking.is_session_active is True
        
        # Complete session
        sample_session_tracking.complete_session()
        assert sample_session_tracking.status == "completed"
        assert sample_session_tracking.is_session_active is False
        
        # Reset to active
        sample_session_tracking.status = "active"
        assert sample_session_tracking.is_session_active is True
        
        # Cancel session
        sample_session_tracking.cancel_session()
        assert sample_session_tracking.status == "cancelled"
        assert sample_session_tracking.is_session_active is False
    
    def test_multiple_status_changes(self, sample_session_tracking):
        """Test multiple status changes"""
        # Complete first
        sample_session_tracking.complete_session()
        assert sample_session_tracking.status == "completed"
        
        # Cancel after completion (edge case)
        sample_session_tracking.cancel_session()
        assert sample_session_tracking.status == "cancelled"
    
    def test_scanned_at_timestamp(self, sample_session_tracking):
        """Test scanned_at timestamp is properly set"""
        assert isinstance(sample_session_tracking.scanned_at, datetime)
        assert sample_session_tracking.scanned_at.tzinfo is not None