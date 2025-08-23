# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token data schema"""
    user_id: str
    email: str
    role: str | None = None

class ChangePassword(BaseModel):
    """Change password schema"""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

class ForgotPassword(BaseModel):
    """Forgot password request schema"""
    email: EmailStr

class ResetPassword(BaseModel):
    """Reset password schema"""
    token: str
    new_password: str = Field(..., min_length=8)

class RefreshToken(BaseModel):
    """Refresh token request schema"""
    refresh_token: str

class MessageResponse(BaseModel):
    """Simple message response"""
    message: str