from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class ResponseMetadata(BaseModel):
    """Shared metadata for all API responses."""
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RegisterRequest(BaseModel):
    """Request schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Request schema for token refresh."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    refresh_expires_in: Optional[int] = None


class AuthResponse(BaseModel):
    """Response schema for auth endpoints with embedded metadata."""
    success: bool
    message: str
    data: Optional[TokenResponse] = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
