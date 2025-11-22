"""
Campaign schemas
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, UUID4


class CampaignBase(BaseModel):
    """Base campaign schema"""
    name: str
    funnel_type: Optional[str] = None
    affiliate_link: Optional[str] = None


class CampaignCreate(CampaignBase):
    """Campaign creation schema"""
    product_id: Optional[UUID4] = None
    settings: Optional[Dict[str, Any]] = None


class CampaignUpdate(BaseModel):
    """Campaign update schema"""
    name: Optional[str] = None
    status: Optional[str] = None
    funnel_type: Optional[str] = None
    affiliate_link: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class CampaignResponse(CampaignBase):
    """Campaign response schema"""
    id: UUID4
    user_id: UUID4
    product_id: Optional[UUID4] = None
    status: str
    tracking_id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
