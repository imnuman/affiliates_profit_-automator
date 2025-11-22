"""
Analytics schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, UUID4
from decimal import Decimal


class AnalyticsEventCreate(BaseModel):
    """Analytics event creation"""
    campaign_id: Optional[UUID4] = None
    event_type: str
    source: Optional[str] = None
    metadata: Optional[dict] = None
    revenue: Optional[Decimal] = None


class DashboardMetrics(BaseModel):
    """Dashboard metrics response"""
    total_clicks: int
    total_conversions: int
    total_revenue: Decimal
    conversion_rate: float
    average_commission: Decimal
    active_campaigns: int


class CampaignAnalytics(BaseModel):
    """Campaign analytics response"""
    campaign_id: UUID4
    campaign_name: str
    clicks: int
    conversions: int
    revenue: Decimal
    conversion_rate: float
    epc: Decimal  # Earnings per click


class RevenueDataPoint(BaseModel):
    """Revenue time series data point"""
    date: datetime
    revenue: Decimal
    conversions: int


class TrafficSource(BaseModel):
    """Traffic source breakdown"""
    source: str
    clicks: int
    conversions: int
    revenue: Decimal
