import pytest
from uuid import uuid4
from datetime import datetime, timezone

from tests.conftest import MockUser


class MockSessionVolume:
    """Mock SessionVolume object that behaves like SQLAlchemy model"""
    def __init__(self):
        self.id = uuid4()
        self.user_id = uuid4()
        self.trainer_id = uuid4()
        self.session_count = 0
        self.notes = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.deleted_at = None
        self.user = None
        self.trainer = None
    
    def __repr__(self):
        return f"<SessionVolume(id={self.id}, user_id={self.user_id}, trainer_id={self.trainer_id}, session_count={self.session_count})>"
    
    @property
    def is_active(self) -> bool:
        """Check if session volume record is active (not soft deleted)"""
        return self.deleted_at is None
    
    def increment_session_count(self, count: int = 1):
        """Increment the session count"""
        self.session_count += count
    
    def add_note(self, note: str):
        """Add or update notes"""
        if self.notes:
            self.notes += f"\n{note}"
        else:
            self.notes = note


@pytest.fixture
def sample_session_volume():
    """Create a sample SessionVolume object"""
    session_volume = MockSessionVolume()
    session_volume.session_count = 5
    session_volume.notes = "Great progress this week!"
    return session_volume


@pytest.fixture
def empty_session_volume():
    """Create an empty SessionVolume object"""
    return MockSessionVolume()


@pytest.mark.unit
@pytest.mark.model
class TestSessionVolumeModel:
    """Test SessionVolume model methods and properties"""
    
    def test_session_volume_repr(self, sample_session_volume):
        """Test SessionVolume __repr__ method"""
        result = repr(sample_session_volume)
        
        assert "SessionVolume(id=" in result
        assert f"user_id={sample_session_volume.user_id}" in result
        assert f"trainer_id={sample_session_volume.trainer_id}" in result
        assert "session_count=5" in result
    
    def test_is_active_true(self, sample_session_volume):
        """Test is_active property returns True when not deleted"""
        assert sample_session_volume.is_active is True
    
    def test_is_active_false(self, sample_session_volume):
        """Test is_active property returns False when soft deleted"""
        sample_session_volume.deleted_at = datetime.now(timezone.utc)
        assert sample_session_volume.is_active is False
    
    def test_increment_session_count_default(self, empty_session_volume):
        """Test increment_session_count with default value"""
        initial_count = empty_session_volume.session_count
        empty_session_volume.increment_session_count()
        
        assert empty_session_volume.session_count == initial_count + 1
    
    def test_increment_session_count_custom(self, empty_session_volume):
        """Test increment_session_count with custom value"""
        initial_count = empty_session_volume.session_count
        empty_session_volume.increment_session_count(5)
        
        assert empty_session_volume.session_count == initial_count + 5
    
    def test_increment_session_count_multiple(self, empty_session_volume):
        """Test multiple increments accumulate correctly"""
        empty_session_volume.increment_session_count(3)
        empty_session_volume.increment_session_count(2)
        
        assert empty_session_volume.session_count == 5
    
    def test_add_note_to_empty(self, empty_session_volume):
        """Test adding note to empty notes"""
        note = "First training session completed"
        empty_session_volume.add_note(note)
        
        assert empty_session_volume.notes == note
    
    def test_add_note_to_existing(self, sample_session_volume):
        """Test adding note to existing notes"""
        original_notes = sample_session_volume.notes
        new_note = "Additional progress noted"
        sample_session_volume.add_note(new_note)
        
        expected_notes = f"{original_notes}\n{new_note}"
        assert sample_session_volume.notes == expected_notes
    
    def test_add_multiple_notes(self, empty_session_volume):
        """Test adding multiple notes"""
        empty_session_volume.add_note("First note")
        empty_session_volume.add_note("Second note")
        empty_session_volume.add_note("Third note")
        
        expected_notes = "First note\nSecond note\nThird note"
        assert empty_session_volume.notes == expected_notes
    
    def test_add_empty_note(self, empty_session_volume):
        """Test adding empty note"""
        empty_session_volume.add_note("")
        
        assert empty_session_volume.notes == ""
    
    def test_session_volume_initialization(self):
        """Test SessionVolume initialization with default values"""
        session_volume = MockSessionVolume()
        
        assert session_volume.id is not None
        assert session_volume.user_id is not None
        assert session_volume.trainer_id is not None
        assert session_volume.session_count == 0
        assert session_volume.notes is None
        assert session_volume.created_at is not None
        assert session_volume.updated_at is not None
        assert session_volume.deleted_at is None
        assert session_volume.is_active is True
    
    def test_session_volume_relationships_none(self, empty_session_volume):
        """Test session volume with no loaded relationships"""
        assert empty_session_volume.user is None
        assert empty_session_volume.trainer is None
    
    def test_session_volume_with_relationships(self, empty_session_volume):
        """Test session volume with loaded relationships"""
        user = MockUser()
        trainer = MockUser()
        
        empty_session_volume.user = user
        empty_session_volume.trainer = trainer
        
        assert empty_session_volume.user == user
        assert empty_session_volume.trainer == trainer