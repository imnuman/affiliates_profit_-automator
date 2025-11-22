"""
Content schemas
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, UUID4


class ContentBase(BaseModel):
    """Base content schema"""
    type: str
    title: Optional[str] = None
    body: str


class ContentCreate(ContentBase):
    """Content creation schema"""
    campaign_id: Optional[UUID4] = None
    metadata: Optional[Dict[str, Any]] = None


class ContentUpdate(BaseModel):
    """Content update schema"""
    title: Optional[str] = None
    body: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ContentResponse(ContentBase):
    """Content response schema"""
    id: UUID4
    user_id: UUID4
    campaign_id: Optional[UUID4] = None
    status: str
    metadata: Optional[Dict[str, Any]] = None
    published_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentGenerateRequest(BaseModel):
    """AI content generation request"""
    product_id: UUID4
    content_type: str  # review, comparison, email, social
    tone: Optional[str] = "professional"
    length: Optional[str] = "medium"
    additional_context: Optional[str] = None
