"""
Celery tasks for ClickBank product synchronization and data updates.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import select, func

from app.tasks.celery_app import celery_app
from app.database import async_session_maker
from app.models.product import Product
from app.services.clickbank import ClickBankService
from app.core.logging import logger


def run_async(coro):
    """Helper to run async code in Celery tasks."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@celery_app.task(bind=True)
def sync_clickbank_products(self, category: str = None, limit: int = 100):
    """
    Sync ClickBank products from API to database.

    Args:
        category: Optional category filter
        limit: Maximum number of products to sync

    Returns:
        Dict with sync statistics
    """
    try:
        async def _sync():
            clickbank_service = ClickBankService()

            # Fetch products from ClickBank API
            products_data = await clickbank_service.search_products(
                category=category,
                min_gravity=10.0,  # Only products with some traction
                limit=limit
            )

            created_count = 0
            updated_count = 0

            async with async_session_maker() as session:
                for product_data in products_data:
                    clickbank_id = product_data.get("site")

                    # Check if product exists
                    result = await session.execute(
                        select(Product).where(Product.clickbank_id == clickbank_id)
                    )
                    existing_product = result.scalar_one_or_none()

                    if existing_product:
                        # Update existing product
                        existing_product.title = product_data.get("title", existing_product.title)
                        existing_product.vendor = product_data.get("vendor", existing_product.vendor)
                        existing_product.category = product_data.get("category", existing_product.category)
                        existing_product.description = product_data.get("description", existing_product.description)
                        existing_product.commission_rate = product_data.get("percent_per_sale")
                        existing_product.commission_amount = product_data.get("initial_sale_amount")
                        existing_product.initial_sale_amount = product_data.get("initial_sale_amount")
                        existing_product.gravity = product_data.get("gravity")
                        existing_product.refund_rate = product_data.get("refund_rate")
                        existing_product.rebill = product_data.get("has_recurring", False)
                        existing_product.popularity_rank = product_data.get("rank")
                        existing_product.data_snapshot = product_data
                        existing_product.last_updated = datetime.utcnow()
                        updated_count += 1
                    else:
                        # Create new product
                        new_product = Product(
                            clickbank_id=clickbank_id,
                            title=product_data.get("title", ""),
                            vendor=product_data.get("vendor", ""),
                            category=product_data.get("category"),
                            description=product_data.get("description"),
                            commission_rate=product_data.get("percent_per_sale"),
                            commission_amount=product_data.get("initial_sale_amount"),
                            initial_sale_amount=product_data.get("initial_sale_amount"),
                            gravity=product_data.get("gravity"),
                            refund_rate=product_data.get("refund_rate"),
                            rebill=product_data.get("has_recurring", False),
                            popularity_rank=product_data.get("rank"),
                            data_snapshot=product_data,
                            last_updated=datetime.utcnow()
                        )
                        session.add(new_product)
                        created_count += 1

                await session.commit()

            logger.info(f"ClickBank sync completed: {created_count} created, {updated_count} updated")

            return {
                "status": "completed",
                "created": created_count,
                "updated": updated_count,
                "total": created_count + updated_count,
                "category": category
            }

        return run_async(_sync())

    except Exception as exc:
        logger.error(f"ClickBank sync failed: {str(exc)}")
        raise


@celery_app.task
def update_product_metrics(product_id: str = None):
    """
    Update product performance metrics and rankings.

    Args:
        product_id: Optional specific product ID, otherwise updates all

    Returns:
        Dict with update statistics
    """
    try:
        async def _update_metrics():
            async with async_session_maker() as session:
                if product_id:
                    # Update specific product
                    result = await session.execute(
                        select(Product).where(Product.id == product_id)
                    )
                    products = [result.scalar_one_or_none()]
                else:
                    # Update products that haven't been updated in 24 hours
                    cutoff_time = datetime.utcnow() - timedelta(hours=24)
                    result = await session.execute(
                        select(Product)
                        .where(Product.last_updated < cutoff_time)
                        .limit(50)  # Batch update
                    )
                    products = result.scalars().all()

                clickbank_service = ClickBankService()
                updated_count = 0

                for product in products:
                    if not product:
                        continue

                    try:
                        # Fetch fresh data from ClickBank
                        product_data = await clickbank_service.get_product_details(
                            product.clickbank_id
                        )

                        if product_data:
                            # Update metrics
                            product.gravity = product_data.get("gravity", product.gravity)
                            product.refund_rate = product_data.get("refund_rate", product.refund_rate)
                            product.popularity_rank = product_data.get("rank", product.popularity_rank)
                            product.data_snapshot = product_data
                            product.last_updated = datetime.utcnow()
                            updated_count += 1

                    except Exception as e:
                        logger.warning(f"Failed to update product {product.clickbank_id}: {str(e)}")
                        continue

                await session.commit()

                logger.info(f"Updated metrics for {updated_count} products")
                return {"status": "completed", "updated": updated_count}

        return run_async(_update_metrics())

    except Exception as exc:
        logger.error(f"Product metrics update failed: {str(exc)}")
        raise


@celery_app.task
def identify_trending_products(min_gravity: float = 50.0, limit: int = 20):
    """
    Identify trending products based on gravity and recent performance.

    Args:
        min_gravity: Minimum gravity score
        limit: Number of trending products to identify

    Returns:
        List of trending product IDs and details
    """
    try:
        async def _identify_trending():
            async with async_session_maker() as session:
                # Get high-gravity products
                result = await session.execute(
                    select(Product)
                    .where(Product.gravity >= min_gravity)
                    .order_by(Product.gravity.desc())
                    .limit(limit)
                )
                trending_products = result.scalars().all()

                trending_list = []
                for product in trending_products:
                    trending_list.append({
                        "id": str(product.id),
                        "clickbank_id": product.clickbank_id,
                        "title": product.title,
                        "category": product.category,
                        "gravity": float(product.gravity) if product.gravity else 0,
                        "commission": float(product.commission_amount) if product.commission_amount else 0,
                        "vendor": product.vendor
                    })

                    # Mark as trending in metadata
                    product.data_snapshot = {
                        **(product.data_snapshot or {}),
                        "trending": True,
                        "trending_since": datetime.utcnow().isoformat()
                    }

                await session.commit()

                logger.info(f"Identified {len(trending_list)} trending products")
                return {"status": "completed", "trending_products": trending_list}

        return run_async(_identify_trending())

    except Exception as exc:
        logger.error(f"Trending products identification failed: {str(exc)}")
        raise


@celery_app.task
def calculate_product_roi(product_id: str = None):
    """
    Calculate ROI estimates for products based on campaigns and analytics.

    Args:
        product_id: Optional specific product, otherwise calculates for all

    Returns:
        Dict with ROI calculations
    """
    try:
        async def _calculate_roi():
            async with async_session_maker() as session:
                if product_id:
                    result = await session.execute(
                        select(Product).where(Product.id == product_id)
                    )
                    products = [result.scalar_one_or_none()]
                else:
                    result = await session.execute(select(Product).limit(100))
                    products = result.scalars().all()

                roi_data = []

                for product in products:
                    if not product:
                        continue

                    # Get campaign count
                    from app.models.campaign import Campaign
                    campaign_result = await session.execute(
                        select(func.count(Campaign.id))
                        .where(Campaign.product_id == product.id)
                    )
                    campaign_count = campaign_result.scalar()

                    # Get analytics data
                    from app.models.analytics import AnalyticsEvent
                    analytics_result = await session.execute(
                        select(
                            func.count(AnalyticsEvent.id).label('total_events'),
                            func.sum(AnalyticsEvent.revenue).label('total_revenue')
                        )
                        .join(Campaign, Campaign.id == AnalyticsEvent.campaign_id)
                        .where(Campaign.product_id == product.id)
                    )
                    analytics = analytics_result.one()

                    # Calculate estimated ROI
                    avg_revenue_per_campaign = (
                        float(analytics.total_revenue or 0) / campaign_count
                        if campaign_count > 0 else 0
                    )

                    roi_info = {
                        "product_id": str(product.id),
                        "product_title": product.title,
                        "campaign_count": campaign_count,
                        "total_revenue": float(analytics.total_revenue or 0),
                        "avg_revenue_per_campaign": avg_revenue_per_campaign,
                        "commission_amount": float(product.commission_amount or 0),
                        "roi_rating": _calculate_roi_rating(
                            avg_revenue_per_campaign,
                            float(product.gravity or 0)
                        )
                    }

                    roi_data.append(roi_info)

                logger.info(f"Calculated ROI for {len(roi_data)} products")
                return {"status": "completed", "roi_data": roi_data}

        return run_async(_calculate_roi())

    except Exception as exc:
        logger.error(f"ROI calculation failed: {str(exc)}")
        raise


def _calculate_roi_rating(avg_revenue: float, gravity: float) -> str:
    """Calculate ROI rating based on revenue and gravity."""
    score = (avg_revenue * 0.6) + (gravity * 0.4)

    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "fair"
    else:
        return "poor"


@celery_app.task
def cleanup_stale_products(days_old: int = 90):
    """
    Clean up products that haven't been updated in specified days.

    Args:
        days_old: Number of days to consider a product stale

    Returns:
        Dict with cleanup statistics
    """
    try:
        async def _cleanup():
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            async with async_session_maker() as session:
                # Find stale products with no campaigns
                from app.models.campaign import Campaign

                result = await session.execute(
                    select(Product)
                    .outerjoin(Campaign)
                    .where(Product.last_updated < cutoff_date)
                    .where(Campaign.id.is_(None))  # No campaigns
                )
                stale_products = result.scalars().all()

                deleted_count = 0
                for product in stale_products:
                    await session.delete(product)
                    deleted_count += 1

                await session.commit()

                logger.info(f"Cleaned up {deleted_count} stale products")
                return {
                    "status": "completed",
                    "deleted": deleted_count,
                    "cutoff_date": cutoff_date.isoformat()
                }

        return run_async(_cleanup())

    except Exception as exc:
        logger.error(f"Product cleanup failed: {str(exc)}")
        raise
