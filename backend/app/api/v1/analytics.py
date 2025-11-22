"""
Analytics endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal

from app.db.session import get_db
from app.models.user import User
from app.models.analytics import AnalyticsEvent, EventType
from app.models.campaign import Campaign
from app.schemas.analytics import DashboardMetrics
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard metrics for current user
    """
    # Total clicks
    total_clicks = await db.scalar(
        select(func.count(AnalyticsEvent.id)).where(
            AnalyticsEvent.user_id == current_user.id,
            AnalyticsEvent.event_type == EventType.CLICK
        )
    ) or 0

    # Total conversions
    total_conversions = await db.scalar(
        select(func.count(AnalyticsEvent.id)).where(
            AnalyticsEvent.user_id == current_user.id,
            AnalyticsEvent.event_type == EventType.CONVERSION
        )
    ) or 0

    # Total revenue
    total_revenue = await db.scalar(
        select(func.sum(AnalyticsEvent.revenue)).where(
            AnalyticsEvent.user_id == current_user.id,
            AnalyticsEvent.event_type == EventType.CONVERSION
        )
    ) or Decimal("0.00")

    # Active campaigns
    active_campaigns = await db.scalar(
        select(func.count(Campaign.id)).where(
            Campaign.user_id == current_user.id,
            Campaign.status == "active"
        )
    ) or 0

    # Conversion rate
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0.0

    # Average commission
    average_commission = (total_revenue / total_conversions) if total_conversions > 0 else Decimal("0.00")

    return {
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "total_revenue": total_revenue,
        "conversion_rate": conversion_rate,
        "average_commission": average_commission,
        "active_campaigns": active_campaigns
    }
