"""
Celery tasks for AI content generation and processing.
"""
from typing import Dict, Any, Optional
import asyncio
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.database import async_session_maker
from app.models.content import Content
from app.models.campaign import Campaign
from app.models.user import User
from app.services.claude import ClaudeService
from app.core.logging import logger


def run_async(coro):
    """Helper to run async code in Celery tasks."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, max_retries=3)
def generate_content_task(self, content_id: str, prompt: str, max_tokens: int = 2500):
    """
    Generate AI content using Claude API.

    Args:
        content_id: UUID of content record
        prompt: Generation prompt
        max_tokens: Maximum tokens to generate

    Returns:
        Dict with content_id and status
    """
    try:
        async def _generate():
            async with async_session_maker() as session:
                # Get content record
                result = await session.execute(
                    select(Content).where(Content.id == content_id)
                )
                content = result.scalar_one_or_none()

                if not content:
                    raise ValueError(f"Content {content_id} not found")

                # Update status to generating
                content.status = "generating"
                await session.commit()

                # Generate content
                claude_service = ClaudeService()
                generated_text = ""

                async for chunk in claude_service.generate_content_stream(
                    prompt=prompt, max_tokens=max_tokens
                ):
                    generated_text += chunk

                # Update content with generated text
                content.body = generated_text
                content.status = "draft"
                await session.commit()

                logger.info(f"Content generated successfully: {content_id}")
                return {"content_id": str(content.id), "status": "completed"}

        return run_async(_generate())

    except Exception as exc:
        logger.error(f"Content generation failed: {str(exc)}")

        # Update content status to failed
        async def _mark_failed():
            async with async_session_maker() as session:
                result = await session.execute(
                    select(Content).where(Content.id == content_id)
                )
                content = result.scalar_one_or_none()
                if content:
                    content.status = "failed"
                    content.metadata = {
                        **(content.metadata or {}),
                        "error": str(exc)
                    }
                    await session.commit()

        run_async(_mark_failed())

        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task
def batch_generate_content(campaign_id: str, content_count: int = 5):
    """
    Generate multiple content pieces for a campaign.

    Args:
        campaign_id: UUID of campaign
        content_count: Number of content pieces to generate

    Returns:
        Dict with campaign_id and generated content IDs
    """
    try:
        async def _batch_generate():
            async with async_session_maker() as session:
                # Get campaign
                result = await session.execute(
                    select(Campaign).where(Campaign.id == campaign_id)
                )
                campaign = result.scalar_one_or_none()

                if not campaign:
                    raise ValueError(f"Campaign {campaign_id} not found")

                # Get product info
                product = campaign.product
                if not product:
                    raise ValueError(f"Campaign has no product associated")

                content_ids = []

                # Generate different content types
                content_types = ["blog_post", "email", "social_post", "video_script"]

                for i in range(min(content_count, len(content_types))):
                    content_type = content_types[i]

                    # Create content record
                    content = Content(
                        user_id=campaign.user_id,
                        campaign_id=campaign.id,
                        type=content_type,
                        title=f"{content_type.replace('_', ' ').title()} for {product.title}",
                        body="",
                        status="queued",
                        metadata={"batch_generated": True}
                    )
                    session.add(content)
                    await session.flush()

                    # Build prompt based on type
                    prompt = _build_prompt(content_type, product, campaign)

                    # Queue generation task
                    generate_content_task.delay(str(content.id), prompt)
                    content_ids.append(str(content.id))

                await session.commit()

                logger.info(f"Queued {len(content_ids)} content pieces for campaign {campaign_id}")
                return {
                    "campaign_id": str(campaign_id),
                    "content_ids": content_ids,
                    "status": "queued"
                }

        return run_async(_batch_generate())

    except Exception as exc:
        logger.error(f"Batch content generation failed: {str(exc)}")
        raise


def _build_prompt(content_type: str, product, campaign) -> str:
    """Build AI prompt based on content type and product."""

    base_context = f"""
Product: {product.title}
Vendor: {product.vendor}
Category: {product.category}
Description: {product.description}
Commission: ${product.commission_amount} ({product.commission_rate}%)
"""

    prompts = {
        "blog_post": f"""
{base_context}

Write a comprehensive, SEO-optimized blog post (800-1200 words) reviewing this product.

Include:
- Engaging introduction with hook
- What the product offers
- Key benefits and features
- Who it's perfect for
- Pros and cons (be balanced)
- Personal recommendation
- Strong call-to-action

Tone: Helpful, authentic, persuasive but not pushy.
Format: Use headers, bullet points, short paragraphs.
""",

        "email": f"""
{base_context}

Write a compelling email (300-400 words) promoting this product.

Include:
- Attention-grabbing subject line
- Personal greeting
- Problem/pain point
- How product solves it
- Social proof or results
- Clear call-to-action
- P.S. with urgency

Tone: Conversational, friendly, benefit-focused.
""",

        "social_post": f"""
{base_context}

Write 3 engaging social media posts (each 100-150 words) for Twitter/LinkedIn.

Each should:
- Hook in first line
- Highlight one key benefit
- Include call-to-action
- Use relevant hashtags (2-3)

Tone: Casual, engaging, value-driven.
""",

        "video_script": f"""
{base_context}

Write a video script (2-3 minutes, ~300 words) for a product review.

Structure:
- Hook (first 5 seconds)
- Introduction
- Product overview
- Demonstration/walkthrough
- Results/benefits
- Who should buy
- Call-to-action
- Outro

Tone: Energetic, authentic, helpful.
Include visual cues in [brackets].
"""
    }

    return prompts.get(content_type, prompts["blog_post"])


@celery_app.task
def optimize_content_seo(content_id: str):
    """
    Optimize content for SEO using AI.

    Args:
        content_id: UUID of content to optimize

    Returns:
        Dict with optimization results
    """
    try:
        async def _optimize():
            async with async_session_maker() as session:
                result = await session.execute(
                    select(Content).where(Content.id == content_id)
                )
                content = result.scalar_one_or_none()

                if not content:
                    raise ValueError(f"Content {content_id} not found")

                claude_service = ClaudeService()

                # Generate SEO improvements
                prompt = f"""
Analyze this content and provide SEO optimization suggestions:

Title: {content.title}
Content: {content.body[:1000]}...

Provide:
1. Improved title (with keyword)
2. Meta description (155 characters)
3. 5-10 relevant keywords
4. H2/H3 heading suggestions
5. Internal linking opportunities

Format as JSON.
"""

                generated_text = ""
                async for chunk in claude_service.generate_content_stream(prompt, max_tokens=800):
                    generated_text += chunk

                # Update metadata
                content.metadata = {
                    **(content.metadata or {}),
                    "seo_optimized": True,
                    "seo_suggestions": generated_text
                }
                await session.commit()

                logger.info(f"SEO optimization completed for content {content_id}")
                return {"content_id": str(content_id), "status": "optimized"}

        return run_async(_optimize())

    except Exception as exc:
        logger.error(f"SEO optimization failed: {str(exc)}")
        raise


@celery_app.task
def schedule_content_publishing(content_id: str, publish_at: str, platforms: list):
    """
    Schedule content for future publishing.

    Args:
        content_id: UUID of content
        publish_at: ISO timestamp for publishing
        platforms: List of platforms (wordpress, twitter, facebook, etc.)

    Returns:
        Dict with scheduling confirmation
    """
    try:
        async def _schedule():
            async with async_session_maker() as session:
                result = await session.execute(
                    select(Content).where(Content.id == content_id)
                )
                content = result.scalar_one_or_none()

                if not content:
                    raise ValueError(f"Content {content_id} not found")

                from datetime import datetime
                scheduled_time = datetime.fromisoformat(publish_at)

                content.scheduled_for = scheduled_time
                content.status = "scheduled"
                content.metadata = {
                    **(content.metadata or {}),
                    "scheduled_platforms": platforms
                }
                await session.commit()

                logger.info(f"Content {content_id} scheduled for {publish_at}")
                return {
                    "content_id": str(content_id),
                    "scheduled_for": publish_at,
                    "platforms": platforms
                }

        return run_async(_schedule())

    except Exception as exc:
        logger.error(f"Content scheduling failed: {str(exc)}")
        raise
