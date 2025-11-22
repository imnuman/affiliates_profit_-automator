"""
User schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, UUID4, Field


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """User response schema"""
    id: UUID4
    tier: str
    status: str
    is_email_verified: bool
    created_at: datetime
    trial_ends_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh schema"""
    refresh_token: str


class UserUsage(BaseModel):
    """User usage statistics"""
    content_generated: int
    content_limit: int
    campaigns_active: int
    campaigns_limit: int
    storage_used_gb: float
    storage_limit_gb: int
