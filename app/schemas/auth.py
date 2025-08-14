# app/schemas/auth.py
from pydantic import BaseModel

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token data schema"""
    user_id: str
    email: str
    role: str | None = None