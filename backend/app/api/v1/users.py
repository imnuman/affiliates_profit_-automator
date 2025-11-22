"""
User endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User
from app.models.content import Content
from app.models.campaign import Campaign
from app.schemas.user import UserResponse, UserUpdate, UserUsage
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile
    """
    # Update fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    if user_update.email is not None:
        # Check if email is already taken
        result = await db.execute(
            select(User).where(User.email == user_update.email, User.id != current_user.id)
        )
        if result.scalar_one_or_none():
            from app.core.exceptions import ConflictException
            raise ConflictException("Email already in use")

        current_user.email = user_update.email
        current_user.is_email_verified = False

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/me/usage", response_model=UserUsage)
async def get_user_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's usage statistics
    """
    # Get tier limits
    tier_limits = settings.tier_limits[current_user.tier]

    # Count content generated this month
    from datetime import datetime
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    content_count = await db.scalar(
        select(func.count(Content.id)).where(
            Content.user_id == current_user.id,
            Content.created_at >= start_of_month
        )
    )

    # Count active campaigns
    active_campaigns = await db.scalar(
        select(func.count(Campaign.id)).where(
            Campaign.user_id == current_user.id,
            Campaign.status == "active"
        )
    )

    return {
        "content_generated": content_count or 0,
        "content_limit": tier_limits["content"],
        "campaigns_active": active_campaigns or 0,
        "campaigns_limit": tier_limits["campaigns"],
        "storage_used_gb": 0.0,  # TODO: Calculate actual storage
        "storage_limit_gb": tier_limits["storage_gb"]
    }
