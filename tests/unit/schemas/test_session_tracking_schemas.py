import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime, timezone

from app.schemas.session_tracking import (
    SessionTrackingBase,
    SessionTrackingCreate,
    SessionTrackingUpdate,
    SessionTrackingResponse,
    SessionTrackingSummary,
    SessionStatusUpdate,
    SessionTrackingStats
)


@pytest.mark.unit
@pytest.mark.schema
class TestSessionTrackingBase:
    """Test SessionTrackingBase schema"""
    
    def test_valid_session_tracking_base(self):
        """Test valid SessionTrackingBase creation"""
        session_data = {
            "status": "active"
        }
        
        session = SessionTrackingBase(**session_data)
        
        assert session.status == "active"
    
    def test_session_tracking_base_default_status(self):
        """Test SessionTrackingBase with default status"""
        session = SessionTrackingBase()
        
        assert session.status == "active"
    
    def test_status_validation_active(self):
        """Test status validation passes for active"""
        session = SessionTrackingBase(status="active")
        assert session.status == "active"
    
    def test_status_validation_completed(self):
        """Test status validation passes for completed"""
        session = SessionTrackingBase(status="completed")
        assert session.status == "completed"
    
    def test_status_validation_cancelled(self):
        """Test status validation passes for cancelled"""
        session = SessionTrackingBase(status="cancelled")
        assert session.status == "cancelled"
    
    def test_status_validation_invalid(self):
        """Test status validation fails for invalid status"""
        with pytest.raises(ValidationError) as exc_info:
            SessionTrackingBase(status="invalid_status")
        
        assert "Status must be one of: active, completed, cancelled" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestSessionTrackingCreate:
    """Test SessionTrackingCreate schema"""
    
    def test_valid_session_tracking_create(self):
        """Test valid SessionTrackingCreate"""
        user_id = uuid4()
        qr_code_id = uuid4()
        scanned_at = datetime.now(timezone.utc)
        
        session_data = {
            "user_id": user_id,
            "qr_code_id": qr_code_id,
            "status": "active",
            "scanned_at": scanned_at
        }
        
        session = SessionTrackingCreate(**session_data)
        
        assert session.user_id == user_id
        assert session.qr_code_id == qr_code_id
        assert session.status == "active"
        assert session.scanned_at == scanned_at
    
    def test_session_tracking_create_minimal(self):
        """Test SessionTrackingCreate with minimal required data"""
        user_id = uuid4()
        qr_code_id = uuid4()
        
        session = SessionTrackingCreate(user_id=user_id, qr_code_id=qr_code_id)
        
        assert session.user_id == user_id
        assert session.qr_code_id == qr_code_id
        assert session.status == "active"  # Default
        assert session.scanned_at is None  # Optional
    
    def test_session_tracking_create_missing_user_id(self):
        """Test SessionTrackingCreate without required user_id"""
        qr_code_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            SessionTrackingCreate(qr_code_id=qr_code_id)
        
        assert "user_id" in str(exc_info.value)
    
    def test_session_tracking_create_missing_qr_code_id(self):
        """Test SessionTrackingCreate without required qr_code_id"""
        user_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            SessionTrackingCreate(user_id=user_id)
        
        assert "qr_code_id" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestSessionTrackingUpdate:
    """Test SessionTrackingUpdate schema"""
    
    def test_valid_session_tracking_update(self):
        """Test valid SessionTrackingUpdate"""
        update_data = {
            "status": "completed"
        }
        
        session_update = SessionTrackingUpdate(**update_data)
        
        assert session_update.status == "completed"
    
    def test_empty_session_tracking_update(self):
        """Test SessionTrackingUpdate with no fields"""
        session_update = SessionTrackingUpdate()
        
        assert session_update.status is None
    
    def test_session_tracking_update_all_statuses(self):
        """Test SessionTrackingUpdate with all valid statuses"""
        for status in ["active", "completed", "cancelled"]:
            session_update = SessionTrackingUpdate(status=status)
            assert session_update.status == status


@pytest.mark.unit
@pytest.mark.schema
class TestSessionTrackingResponse:
    """Test SessionTrackingResponse schema"""
    
    def test_session_tracking_response_creation(self):
        """Test SessionTrackingResponse creation"""
        user_id = uuid4()
        qr_code_id = uuid4()
        session_id = uuid4()
        scanned_at = datetime.now(timezone.utc)
        
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
        
        session_data = {
            "id": session_id,
            "user_id": user_id,
            "qr_code_id": qr_code_id,
            "status": "active",
            "scanned_at": scanned_at,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None,
            "user": user_data
        }
        
        session_response = SessionTrackingResponse(**session_data)
        
        assert session_response.id == session_id
        assert session_response.user_id == user_id
        assert session_response.qr_code_id == qr_code_id
        assert session_response.status == "active"
        assert session_response.scanned_at == scanned_at
        assert session_response.user.email == "user@example.com"


@pytest.mark.unit
@pytest.mark.schema
class TestSessionTrackingSummary:
    """Test SessionTrackingSummary schema"""
    
    def test_session_tracking_summary_creation(self):
        """Test SessionTrackingSummary creation"""
        user_id = uuid4()
        qr_code_id = uuid4()
        session_id = uuid4()
        scanned_at = datetime.now(timezone.utc)
        
        summary_data = {
            "id": session_id,
            "user_id": user_id,
            "qr_code_id": qr_code_id,
            "status": "completed",
            "scanned_at": scanned_at,
            "is_active": True,
            "is_session_active": False
        }
        
        summary = SessionTrackingSummary(**summary_data)
        
        assert summary.id == session_id
        assert summary.user_id == user_id
        assert summary.qr_code_id == qr_code_id
        assert summary.status == "completed"
        assert summary.scanned_at == scanned_at
        assert summary.is_active is True
        assert summary.is_session_active is False
    
    def test_session_tracking_summary_defaults(self):
        """Test SessionTrackingSummary with default values"""
        user_id = uuid4()
        qr_code_id = uuid4()
        session_id = uuid4()
        scanned_at = datetime.now(timezone.utc)
        
        summary = SessionTrackingSummary(
            id=session_id,
            user_id=user_id,
            qr_code_id=qr_code_id,
            status="active",
            scanned_at=scanned_at
        )
        
        assert summary.is_active is True  # Default
        assert summary.is_session_active is True  # Default


@pytest.mark.unit
@pytest.mark.schema
class TestSessionStatusUpdate:
    """Test SessionStatusUpdate schema"""
    
    def test_valid_session_status_update(self):
        """Test valid SessionStatusUpdate"""
        status_update = SessionStatusUpdate(status="completed")
        
        assert status_update.status == "completed"
    
    def test_session_status_update_all_statuses(self):
        """Test SessionStatusUpdate with all valid statuses"""
        for status in ["active", "completed", "cancelled"]:
            status_update = SessionStatusUpdate(status=status)
            assert status_update.status == status


@pytest.mark.unit
@pytest.mark.schema
class TestSessionTrackingStats:
    """Test SessionTrackingStats schema"""
    
    def test_session_tracking_stats_creation(self):
        """Test SessionTrackingStats creation"""
        stats_data = {
            "total_sessions": 100,
            "active_sessions": 15,
            "completed_sessions": 80,
            "cancelled_sessions": 5
        }
        
        stats = SessionTrackingStats(**stats_data)
        
        assert stats.total_sessions == 100
        assert stats.active_sessions == 15
        assert stats.completed_sessions == 80
        assert stats.cancelled_sessions == 5
    
    def test_session_tracking_stats_defaults(self):
        """Test SessionTrackingStats with default values"""
        stats = SessionTrackingStats()
        
        assert stats.total_sessions == 0
        assert stats.active_sessions == 0
        assert stats.completed_sessions == 0
        assert stats.cancelled_sessions == 0
    
    def test_session_tracking_stats_partial(self):
        """Test SessionTrackingStats with partial data"""
        stats = SessionTrackingStats(total_sessions=50, active_sessions=10)
        
        assert stats.total_sessions == 50
        assert stats.active_sessions == 10
        assert stats.completed_sessions == 0  # Default
        assert stats.cancelled_sessions == 0  # Default