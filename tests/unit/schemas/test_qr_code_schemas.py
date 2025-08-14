import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime, timezone

from app.schemas.qr_code import (
    QRCodeBase,
    QRCodeCreate,
    QRCodeUpdate,
    QRCodeResponse,
    QRCodeSummary
)


@pytest.mark.unit
@pytest.mark.schema
class TestQRCodeBase:
    """Test QRCodeBase schema"""
    
    def test_valid_qr_code_base(self):
        """Test valid QRCodeBase creation"""
        qr_data = {
            "token": "abc123def456"
        }
        
        qr_code = QRCodeBase(**qr_data)
        
        assert qr_code.token == "abc123def456"
    
    def test_token_validation_valid(self):
        """Test token validation with valid token"""
        qr_code = QRCodeBase(token="validToken123")
        assert qr_code.token == "validToken123"
    
    def test_token_validation_empty(self):
        """Test token validation with empty token"""
        with pytest.raises(ValidationError) as exc_info:
            QRCodeBase(token="")
        
        assert "Token cannot be empty" in str(exc_info.value)
    
    def test_token_validation_whitespace_only(self):
        """Test token validation with whitespace only"""
        with pytest.raises(ValidationError) as exc_info:
            QRCodeBase(token="   ")
        
        assert "Token cannot be empty" in str(exc_info.value)
    
    def test_token_validation_too_long(self):
        """Test token validation with token too long"""
        long_token = "a" * 256  # 256 characters, over the 255 limit
        with pytest.raises(ValidationError) as exc_info:
            QRCodeBase(token=long_token)
        
        assert "Token must be 255 characters or less" in str(exc_info.value)
    
    def test_token_trimming(self):
        """Test that token is trimmed of whitespace"""
        qr_code = QRCodeBase(token="  token123  ")
        assert qr_code.token == "token123"


@pytest.mark.unit
@pytest.mark.schema
class TestQRCodeCreate:
    """Test QRCodeCreate schema"""
    
    def test_valid_qr_code_create(self):
        """Test valid QRCodeCreate"""
        user_id = uuid4()
        qr_data = {
            "token": "create_token_123",
            "user_id": user_id
        }
        
        qr_code = QRCodeCreate(**qr_data)
        
        assert qr_code.token == "create_token_123"
        assert qr_code.user_id == user_id
    
    def test_qr_code_create_missing_user_id(self):
        """Test QRCodeCreate with missing user_id"""
        with pytest.raises(ValidationError) as exc_info:
            QRCodeCreate(token="test_token")
        
        assert "Field required" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestQRCodeUpdate:
    """Test QRCodeUpdate schema"""
    
    def test_valid_qr_code_update(self):
        """Test valid QRCodeUpdate"""
        update_data = {
            "token": "updated_token_456"
        }
        
        qr_update = QRCodeUpdate(**update_data)
        
        assert qr_update.token == "updated_token_456"
    
    def test_empty_qr_code_update(self):
        """Test QRCodeUpdate with no fields"""
        qr_update = QRCodeUpdate()
        
        assert qr_update.token is None
    
    def test_partial_qr_code_update(self):
        """Test QRCodeUpdate with some fields"""
        qr_update = QRCodeUpdate(token="partial_update")
        
        assert qr_update.token == "partial_update"
    
    def test_qr_code_update_token_validation(self):
        """Test QRCodeUpdate token validation"""
        with pytest.raises(ValidationError) as exc_info:
            QRCodeUpdate(token="")
        
        assert "Token cannot be empty" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.schema
class TestQRCodeResponse:
    """Test QRCodeResponse schema"""
    
    def test_qr_code_response_creation(self):
        """Test QRCodeResponse creation from dict"""
        qr_data = {
            "id": uuid4(),
            "user_id": uuid4(),
            "token": "response_token_789",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "user": None
        }
        
        qr_response = QRCodeResponse(**qr_data)
        
        assert str(qr_response.id) == str(qr_data["id"])
        assert str(qr_response.user_id) == str(qr_data["user_id"])
        assert qr_response.token == "response_token_789"
        assert qr_response.user is None


@pytest.mark.unit
@pytest.mark.schema
class TestQRCodeSummary:
    """Test QRCodeSummary schema"""
    
    def test_qr_code_summary_creation(self):
        """Test QRCodeSummary creation"""
        qr_data = {
            "id": uuid4(),
            "user_id": uuid4(),
            "token": "summary_token_abc",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        qr_summary = QRCodeSummary(**qr_data)
        
        assert str(qr_summary.id) == str(qr_data["id"])
        assert str(qr_summary.user_id) == str(qr_data["user_id"])
        assert qr_summary.token == "summary_token_abc"
        assert qr_summary.created_at == qr_data["created_at"]
        assert qr_summary.updated_at == qr_data["updated_at"]