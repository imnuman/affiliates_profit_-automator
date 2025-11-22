"""
Product schemas
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, UUID4
from decimal import Decimal


class ProductBase(BaseModel):
    """Base product schema"""
    clickbank_id: str
    title: str
    vendor: str
    category: Optional[str] = None
    description: Optional[str] = None


class ProductResponse(ProductBase):
    """Product response schema"""
    id: UUID4
    commission_rate: Optional[Decimal] = None
    commission_amount: Optional[Decimal] = None
    initial_sale_amount: Optional[Decimal] = None
    gravity: Optional[Decimal] = None
    refund_rate: Optional[Decimal] = None
    rebill: bool = False
    popularity_rank: Optional[int] = None
    last_updated: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductSearch(BaseModel):
    """Product search filters"""
    query: Optional[str] = None
    category: Optional[str] = None
    min_gravity: Optional[float] = None
    max_refund_rate: Optional[float] = None
    min_commission: Optional[float] = None
    has_rebill: Optional[bool] = None
    limit: int = 20
    offset: int = 0
