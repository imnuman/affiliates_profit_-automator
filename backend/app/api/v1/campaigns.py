"""
Campaign endpoints
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.dependencies import get_current_user
from app.core.exceptions import NotFoundException
import uuid

router = APIRouter()


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's campaigns
    """
    result = await db.execute(
        select(Campaign).where(Campaign.user_id == current_user.id)
        .order_by(Campaign.created_at.desc())
    )
    campaigns = result.scalars().all()

    return campaigns


@router.post("", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new campaign
    """
    # Create campaign
    campaign = Campaign(
        user_id=current_user.id,
        product_id=campaign_data.product_id,
        name=campaign_data.name,
        funnel_type=campaign_data.funnel_type,
        affiliate_link=campaign_data.affiliate_link,
        tracking_id=str(uuid.uuid4())[:8],
        settings=campaign_data.settings
    )

    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get campaign details
    """
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise NotFoundException("Campaign not found")

    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update campaign
    """
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise NotFoundException("Campaign not found")

    # Update fields
    if campaign_update.name is not None:
        campaign.name = campaign_update.name
    if campaign_update.status is not None:
        campaign.status = campaign_update.status
    if campaign_update.funnel_type is not None:
        campaign.funnel_type = campaign_update.funnel_type
    if campaign_update.affiliate_link is not None:
        campaign.affiliate_link = campaign_update.affiliate_link
    if campaign_update.settings is not None:
        campaign.settings = campaign_update.settings

    await db.commit()
    await db.refresh(campaign)

    return campaign


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete campaign
    """
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise NotFoundException("Campaign not found")

    await db.delete(campaign)
    await db.commit()

    return {"message": "Campaign deleted successfully"}
