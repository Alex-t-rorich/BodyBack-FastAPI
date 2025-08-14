import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime, timezone

from app.schemas.session_volume import (
    SessionVolumeBase,
    SessionVolumeCreate,
    SessionVolumeUpdate,
    SessionVolumeResponse,
    SessionVolumeSummary,
    SessionVolumeIncrement
)


@pytest.mark.unit
@pytest.mark.schema
class TestSessionVolumeBase:
    """Test SessionVolumeBase schema"""
    
    def test_valid_session_volume_base(self):
        """Test valid SessionVolumeBase creation"""
        session_data = {
            "session_count": 10,
            "notes": "Great training session progress"
        }
        
        session = SessionVolumeBase(**session_data)
        
        assert session.session_count == 10
        assert session.notes == "Great training session progress"
    
    def test_session_volume_base_minimal_data(self):
        """Test SessionVolumeBase with minimal data"""
        session = SessionVolumeBase()
        
        assert session.session_count == 0
        assert session.notes is None
    
    def test_session_count_validation_valid(self):
        """Test session count validation passes for valid count"""
        session = SessionVolumeBase(session_count=50)
        assert session.session_count == 50
    
    def test_session_count_validation_zero(self):
        """Test session count validation passes for zero"""
        session = SessionVolumeBase(session_count=0)
        assert session.session_count == 0
    
    def test_session_count_validation_negative(self):
        """Test session count validation fails for negative count"""
        with pytest.raises(ValidationError) as exc_info:
            SessionVolumeBase(session_count=-1)
        
        assert "Session count cannot be negative" in str(exc_info.value)
    
    def test_notes_length_validation_valid(self):
        """Test notes length validation passes for valid length"""
        notes = "A" * 2000  # Exactly 2000 characters
        session = SessionVolumeBase(notes=notes)
        assert len(session.notes) == 2000
    
    def test_notes_length_validation_too_long(self):
        """Test notes length validation fails for too long notes"""
        notes = "A" * 2001  # 2001 characters
        
        with pytest.raises(ValidationError) as exc_info:
            SessionVolumeBase(notes=notes)
        
        assert "Notes must be 2000 characters or less" in str(exc_info.value)
    
    def test_notes_none_allowed(self):
        """Test notes can be None"""
        session = SessionVolumeBase(notes=None)
        assert session.notes is None


@pytest.mark.unit
@pytest.mark.schema
class TestSessionVolumeCreate:
    """Test SessionVolumeCreate schema"""
    
    def test_valid_session_volume_create(self):
        """Test valid SessionVolumeCreate"""
        user_id = uuid4()
        trainer_id = uuid4()
        
        session_data = {
            "user_id": user_id,
            "trainer_id": trainer_id,
            "session_count": 5,
            "notes": "Initial session setup"
        }
        
        session = SessionVolumeCreate(**session_data)
        
        assert session.user_id == user_id
        assert session.trainer_id == trainer_id
        assert session.session_count == 5
        assert session.notes == "Initial session setup"
    
    def test_session_volume_create_minimal(self):
        """Test SessionVolumeCreate with minimal required data"""
        user_id = uuid4()
        trainer_id = uuid4()
        
        session = SessionVolumeCreate(user_id=user_id, trainer_id=trainer_id)
        
        assert session.user_id == user_id
        assert session.trainer_id == trainer_id
        assert session.session_count == 0
        assert session.notes is None
    
    def test_session_volume_create_missing_user_id(self):
        """Test SessionVolumeCreate without required user_id"""
        trainer_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            SessionVolumeCreate(trainer_id=trainer_id)
        
        assert "user_id" in str(exc_info.value)
    
    def test_session_volume_create_missing_trainer_id(self):
        """Test SessionVolumeCreate without required trainer_id"""
        user_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            SessionVolumeCreate(user_id=user_id)
        
        assert "trainer_id" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestSessionVolumeUpdate:
    """Test SessionVolumeUpdate schema"""
    
    def test_valid_session_volume_update(self):
        """Test valid SessionVolumeUpdate"""
        update_data = {
            "session_count": 15,
            "notes": "Updated progress notes"
        }
        
        session_update = SessionVolumeUpdate(**update_data)
        
        assert session_update.session_count == 15
        assert session_update.notes == "Updated progress notes"
    
    def test_empty_session_volume_update(self):
        """Test SessionVolumeUpdate with no fields"""
        session_update = SessionVolumeUpdate()
        
        assert session_update.session_count is None
        assert session_update.notes is None
    
    def test_partial_session_volume_update(self):
        """Test SessionVolumeUpdate with some fields"""
        session_update = SessionVolumeUpdate(session_count=8)
        
        assert session_update.session_count == 8
        assert session_update.notes is None
    
    def test_session_count_update_validation_negative(self):
        """Test SessionVolumeUpdate session count validation fails for negative"""
        with pytest.raises(ValidationError) as exc_info:
            SessionVolumeUpdate(session_count=-5)
        
        assert "Session count cannot be negative" in str(exc_info.value)
    
    def test_notes_update_validation_too_long(self):
        """Test SessionVolumeUpdate notes length validation"""
        notes_too_long = "A" * 2001
        
        with pytest.raises(ValidationError) as exc_info:
            SessionVolumeUpdate(notes=notes_too_long)
        
        assert "Notes must be 2000 characters or less" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestSessionVolumeResponse:
    """Test SessionVolumeResponse schema"""
    
    def test_session_volume_response_creation(self):
        """Test SessionVolumeResponse creation"""
        user_id = uuid4()
        trainer_id = uuid4()
        session_id = uuid4()
        
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
        
        trainer_data = {
            "id": trainer_id,
            "email": "trainer@example.com",
            "first_name": "Jane",
            "last_name": "Trainer",
            "phone_number": "555-5678",
            "location": "City",
            "active": True,
            "roles": ["Trainer"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None
        }
        
        session_data = {
            "id": session_id,
            "user_id": user_id,
            "trainer_id": trainer_id,
            "session_count": 12,
            "notes": "Excellent progress",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "deleted_at": None,
            "user": user_data,
            "trainer": trainer_data
        }
        
        session_response = SessionVolumeResponse(**session_data)
        
        assert session_response.id == session_id
        assert session_response.user_id == user_id
        assert session_response.trainer_id == trainer_id
        assert session_response.session_count == 12
        assert session_response.notes == "Excellent progress"
        assert session_response.user.email == "user@example.com"
        assert session_response.trainer.email == "trainer@example.com"


@pytest.mark.unit
@pytest.mark.schema
class TestSessionVolumeSummary:
    """Test SessionVolumeSummary schema"""
    
    def test_session_volume_summary_creation(self):
        """Test SessionVolumeSummary creation"""
        user_id = uuid4()
        trainer_id = uuid4()
        session_id = uuid4()
        
        summary_data = {
            "id": session_id,
            "user_id": user_id,
            "trainer_id": trainer_id,
            "session_count": 20,
            "has_notes": True,
            "is_active": True
        }
        
        summary = SessionVolumeSummary(**summary_data)
        
        assert summary.id == session_id
        assert summary.user_id == user_id
        assert summary.trainer_id == trainer_id
        assert summary.session_count == 20
        assert summary.has_notes is True
        assert summary.is_active is True
    
    def test_session_volume_summary_minimal(self):
        """Test SessionVolumeSummary with minimal data"""
        user_id = uuid4()
        trainer_id = uuid4()
        session_id = uuid4()
        
        summary = SessionVolumeSummary(
            id=session_id,
            user_id=user_id,
            trainer_id=trainer_id,
            session_count=0
        )
        
        assert summary.id == session_id
        assert summary.user_id == user_id
        assert summary.trainer_id == trainer_id
        assert summary.session_count == 0
        assert summary.has_notes is False
        assert summary.is_active is True


@pytest.mark.unit
@pytest.mark.schema
class TestSessionVolumeIncrement:
    """Test SessionVolumeIncrement schema"""
    
    def test_valid_session_volume_increment(self):
        """Test valid SessionVolumeIncrement"""
        increment = SessionVolumeIncrement(count=5, note="Session completed successfully")
        
        assert increment.count == 5
        assert increment.note == "Session completed successfully"
    
    def test_session_volume_increment_default(self):
        """Test SessionVolumeIncrement with default values"""
        increment = SessionVolumeIncrement()
        
        assert increment.count == 1
        assert increment.note is None
    
    def test_count_validation_positive(self):
        """Test count validation passes for positive values"""
        increment = SessionVolumeIncrement(count=10)
        assert increment.count == 10
    
    def test_count_validation_zero(self):
        """Test count validation fails for zero"""
        with pytest.raises(ValidationError) as exc_info:
            SessionVolumeIncrement(count=0)
        
        assert "Count must be positive" in str(exc_info.value)
    
    def test_count_validation_negative(self):
        """Test count validation fails for negative values"""
        with pytest.raises(ValidationError) as exc_info:
            SessionVolumeIncrement(count=-1)
        
        assert "Count must be positive" in str(exc_info.value)
    
    def test_count_validation_too_large(self):
        """Test count validation fails for values too large"""
        with pytest.raises(ValidationError) as exc_info:
            SessionVolumeIncrement(count=101)
        
        assert "Count increment cannot exceed 100" in str(exc_info.value)
    
    def test_note_length_validation_valid(self):
        """Test note length validation passes for valid length"""
        note = "A" * 500  # Exactly 500 characters
        increment = SessionVolumeIncrement(note=note)
        assert len(increment.note) == 500
    
    def test_note_length_validation_too_long(self):
        """Test note length validation fails for too long note"""
        note = "A" * 501  # 501 characters
        
        with pytest.raises(ValidationError) as exc_info:
            SessionVolumeIncrement(note=note)
        
        assert "Note must be 500 characters or less" in str(exc_info.value)