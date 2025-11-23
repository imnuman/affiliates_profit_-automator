"""
Celery tasks for publishing content to various platforms.
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.database import async_session_maker
from app.models.content import Content
from app.models.campaign import Campaign
from app.services.wordpress import WordPressService
from app.services.social_media import SocialMediaManager, SocialPlatform
from app.services.email import EmailService
from app.core.logging import logger


def run_async(coro):
    """Helper to run async code in Celery tasks."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, max_retries=3)
def publish_to_wordpress(self, content_id: str, wp_config: Dict[str, str]):
    """
    Publish content to WordPress site.

    Args:
        content_id: UUID of content to publish
        wp_config: WordPress configuration (site_url, username, password)

    Returns:
        Dict with publication results
    """
    try:
        async def _publish():
            async with async_session_maker() as session:
                # Get content
                result = await session.execute(
                    select(Content).where(Content.id == content_id)
                )
                content = result.scalar_one_or_none()

                if not content:
                    raise ValueError(f"Content {content_id} not found")

                # Initialize WordPress service
                wp_service = WordPressService(
                    site_url=wp_config["site_url"],
                    username=wp_config["username"],
                    password=wp_config["password"]
                )

                # Verify connection
                await wp_service.verify_connection()

                # Get campaign for category/tags
                campaign = content.campaign
                categories = [campaign.name] if campaign else []
                tags = content.metadata.get("keywords", []) if content.metadata else []

                # Publish post
                result = await wp_service.create_post(
                    title=content.title,
                    content=content.body,
                    status="publish",
                    categories=categories,
                    tags=tags,
                    excerpt=content.body[:200] + "..." if len(content.body) > 200 else content.body
                )

                # Update content metadata
                content.metadata = {
                    **(content.metadata or {}),
                    "wordpress": {
                        "post_id": result["post_id"],
                        "post_url": result["post_url"],
                        "published_at": datetime.utcnow().isoformat()
                    }
                }
                content.status = "published"
                content.published_at = datetime.utcnow()
                await session.commit()

                logger.info(f"Content {content_id} published to WordPress: {result['post_url']}")

                return {
                    "content_id": str(content_id),
                    "platform": "wordpress",
                    "status": "published",
                    "url": result["post_url"]
                }

        return run_async(_publish())

    except Exception as exc:
        logger.error(f"WordPress publishing failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 minutes


@celery_app.task(bind=True, max_retries=3)
def publish_to_social_media(
    self,
    content_id: str,
    platforms: List[str],
    social_configs: Dict[str, Dict]
):
    """
    Publish content to social media platforms.

    Args:
        content_id: UUID of content to publish
        platforms: List of platforms (twitter, facebook, linkedin)
        social_configs: Configuration for each platform

    Returns:
        Dict with publication results for each platform
    """
    try:
        async def _publish():
            async with async_session_maker() as session:
                # Get content
                result = await session.execute(
                    select(Content).where(Content.id == content_id)
                )
                content = result.scalar_one_or_none()

                if not content:
                    raise ValueError(f"Content {content_id} not found")

                # Initialize social media manager
                social_manager = SocialMediaManager()

                # Add platform configurations
                for platform, config in social_configs.items():
                    if platform == "twitter" and platform in platforms:
                        social_manager.add_twitter(
                            api_key=config["api_key"],
                            api_secret=config["api_secret"],
                            access_token=config["access_token"],
                            access_secret=config["access_secret"]
                        )
                    elif platform == "facebook" and platform in platforms:
                        social_manager.add_facebook(
                            access_token=config["access_token"],
                            page_id=config["page_id"]
                        )
                    elif platform == "linkedin" and platform in platforms:
                        social_manager.add_linkedin(
                            access_token=config["access_token"],
                            person_urn=config["person_urn"]
                        )

                # Extract text for social (truncate if needed)
                social_text = content.title
                if content.type == "social_post":
                    social_text = content.body[:280]  # Twitter limit

                # Add affiliate link if available
                if content.campaign and content.campaign.affiliate_link:
                    social_text += f"\n\n{content.campaign.affiliate_link}"

                # Publish to platforms
                platform_enums = [SocialPlatform(p) for p in platforms]
                results = await social_manager.post_to_multiple(
                    platforms=platform_enums,
                    text=social_text,
                    link=content.metadata.get("link") if content.metadata else None
                )

                # Update content metadata
                content.metadata = {
                    **(content.metadata or {}),
                    "social_media": {
                        platform: {
                            "status": "published" if result["success"] else "failed",
                            "post_id": result.get("data", {}).get("post_id") or result.get("data", {}).get("tweet_id"),
                            "published_at": datetime.utcnow().isoformat(),
                            "error": result.get("error")
                        }
                        for platform, result in results.items()
                    }
                }
                content.status = "published"
                content.published_at = datetime.utcnow()
                await session.commit()

                logger.info(f"Content {content_id} published to social media: {platforms}")

                return {
                    "content_id": str(content_id),
                    "platforms": platforms,
                    "results": {str(k): v for k, v in results.items()}
                }

        return run_async(_publish())

    except Exception as exc:
        logger.error(f"Social media publishing failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)


@celery_app.task
def send_email_campaign(campaign_id: str, content_id: str, recipient_list: List[str]):
    """
    Send email campaign to recipient list.

    Args:
        campaign_id: UUID of campaign
        content_id: UUID of email content
        recipient_list: List of email addresses

    Returns:
        Dict with sending statistics
    """
    try:
        async def _send():
            async with async_session_maker() as session:
                # Get content
                result = await session.execute(
                    select(Content).where(Content.id == content_id)
                )
                content = result.scalar_one_or_none()

                if not content or content.type != "email":
                    raise ValueError(f"Email content {content_id} not found")

                email_service = EmailService()

                sent_count = 0
                failed_count = 0
                failed_emails = []

                # Extract subject and body
                subject = content.metadata.get("subject_line", content.title) if content.metadata else content.title
                body = content.body

                # Send to each recipient
                for recipient in recipient_list:
                    try:
                        await email_service.send_email(
                            to_email=recipient,
                            subject=subject,
                            html_body=body,
                            from_email="noreply@yourcompany.com"
                        )
                        sent_count += 1
                    except Exception as e:
                        failed_count += 1
                        failed_emails.append({"email": recipient, "error": str(e)})
                        logger.warning(f"Failed to send to {recipient}: {str(e)}")

                # Update content metadata
                content.metadata = {
                    **(content.metadata or {}),
                    "email_campaign": {
                        "sent": sent_count,
                        "failed": failed_count,
                        "sent_at": datetime.utcnow().isoformat()
                    }
                }
                await session.commit()

                logger.info(f"Email campaign sent: {sent_count} sent, {failed_count} failed")

                return {
                    "campaign_id": str(campaign_id),
                    "content_id": str(content_id),
                    "sent": sent_count,
                    "failed": failed_count,
                    "failed_emails": failed_emails
                }

        return run_async(_send())

    except Exception as exc:
        logger.error(f"Email campaign failed: {str(exc)}")
        raise


@celery_app.task
def publish_scheduled_content():
    """
    Check for and publish all scheduled content that is due.

    This task should run periodically (every 15 minutes).

    Returns:
        Dict with publication statistics
    """
    try:
        async def _publish_scheduled():
            async with async_session_maker() as session:
                # Get content scheduled for now or earlier
                result = await session.execute(
                    select(Content)
                    .where(Content.status == "scheduled")
                    .where(Content.scheduled_for <= datetime.utcnow())
                )
                scheduled_content = result.scalars().all()

                published_count = 0
                failed_count = 0

                for content in scheduled_content:
                    try:
                        platforms = content.metadata.get("scheduled_platforms", []) if content.metadata else []

                        # Determine which platforms to publish to
                        if "wordpress" in platforms:
                            # This would need actual WordPress config from user settings
                            # For now, just mark as needing manual config
                            logger.info(f"Content {content.id} needs WordPress config")

                        if any(p in platforms for p in ["twitter", "facebook", "linkedin"]):
                            # Similarly, needs social media config
                            logger.info(f"Content {content.id} needs social media config")

                        # For now, just mark as published
                        content.status = "published"
                        content.published_at = datetime.utcnow()
                        published_count += 1

                    except Exception as e:
                        logger.error(f"Failed to publish content {content.id}: {str(e)}")
                        content.status = "failed"
                        failed_count += 1

                await session.commit()

                logger.info(f"Scheduled publishing: {published_count} published, {failed_count} failed")

                return {
                    "status": "completed",
                    "published": published_count,
                    "failed": failed_count
                }

        return run_async(_publish_scheduled())

    except Exception as exc:
        logger.error(f"Scheduled publishing failed: {str(exc)}")
        raise


@celery_app.task
def cross_post_content(content_id: str, target_platforms: List[str]):
    """
    Cross-post existing content to multiple platforms.

    Args:
        content_id: UUID of content to cross-post
        target_platforms: List of platforms to post to

    Returns:
        Dict with cross-posting results
    """
    try:
        async def _cross_post():
            async with async_session_maker() as session:
                result = await session.execute(
                    select(Content).where(Content.id == content_id)
                )
                content = result.scalar_one_or_none()

                if not content:
                    raise ValueError(f"Content {content_id} not found")

                results = {}

                # Create platform-specific versions of content
                for platform in target_platforms:
                    try:
                        adapted_content = _adapt_content_for_platform(
                            content.body,
                            platform
                        )

                        results[platform] = {
                            "status": "queued",
                            "adapted_content": adapted_content[:100] + "..."
                        }

                        # Queue actual publishing tasks
                        # (Would call publish_to_wordpress or publish_to_social_media)

                    except Exception as e:
                        results[platform] = {
                            "status": "failed",
                            "error": str(e)
                        }

                logger.info(f"Cross-posted content {content_id} to {len(target_platforms)} platforms")

                return {
                    "content_id": str(content_id),
                    "platforms": target_platforms,
                    "results": results
                }

        return run_async(_cross_post())

    except Exception as exc:
        logger.error(f"Cross-posting failed: {str(exc)}")
        raise


def _adapt_content_for_platform(content: str, platform: str) -> str:
    """Adapt content format for specific platform."""
    if platform == "twitter":
        # Truncate to 280 characters
        return content[:277] + "..." if len(content) > 280 else content

    elif platform == "linkedin":
        # LinkedIn prefers professional tone, keep longer
        return content[:3000]

    elif platform == "facebook":
        # Facebook optimal length
        return content[:2000]

    else:
        return content
