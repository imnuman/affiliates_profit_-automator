"""
Content endpoints
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.content import Content
from app.models.user import User
from app.schemas.content import ContentCreate, ContentUpdate, ContentResponse, ContentGenerateRequest
from app.dependencies import get_current_user
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("", response_model=List[ContentResponse])
async def list_content(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's content
    """
    result = await db.execute(
        select(Content).where(Content.user_id == current_user.id)
        .order_by(Content.created_at.desc())
    )
    content_items = result.scalars().all()

    return content_items


@router.post("", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new content
    """
    content = Content(
        user_id=current_user.id,
        campaign_id=content_data.campaign_id,
        type=content_data.type,
        title=content_data.title,
        body=content_data.body,
        metadata=content_data.metadata
    )

    db.add(content)
    await db.commit()
    await db.refresh(content)

    return content


@router.post("/generate")
async def generate_content(
    request: ContentGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI content (placeholder for WebSocket implementation)
    """
    # TODO: Implement WebSocket streaming with Claude API
    return {
        "message": "Content generation started",
        "job_id": "placeholder",
        "note": "Use WebSocket endpoint for streaming"
    }


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get content details
    """
    result = await db.execute(
        select(Content).where(
            Content.id == content_id,
            Content.user_id == current_user.id
        )
    )
    content = result.scalar_one_or_none()

    if not content:
        raise NotFoundException("Content not found")

    return content


@router.patch("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    content_update: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update content
    """
    result = await db.execute(
        select(Content).where(
            Content.id == content_id,
            Content.user_id == current_user.id
        )
    )
    content = result.scalar_one_or_none()

    if not content:
        raise NotFoundException("Content not found")

    # Update fields
    if content_update.title is not None:
        content.title = content_update.title
    if content_update.body is not None:
        content.body = content_update.body
    if content_update.status is not None:
        content.status = content_update.status
    if content_update.metadata is not None:
        content.metadata = content_update.metadata

    await db.commit()
    await db.refresh(content)

    return content


@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete content
    """
    result = await db.execute(
        select(Content).where(
            Content.id == content_id,
            Content.user_id == current_user.id
        )
    )
    content = result.scalar_one_or_none()

    if not content:
        raise NotFoundException("Content not found")

    await db.delete(content)
    await db.commit()

    return {"message": "Content deleted successfully"}
