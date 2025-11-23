"""
Seed script to populate database with test data.

Run with: python -m scripts.seed_data
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from datetime import datetime, timedelta
import uuid

from app.database import async_session_maker
from app.models.user import User
from app.models.product import Product
from app.models.campaign import Campaign
from app.models.content import Content
from app.models.workflow import Workflow
from app.models.analytics import AnalyticsEvent
from app.core.security import hash_password


async def clear_data():
    """Clear all existing data from the database."""
    print("Clearing existing data...")

    async with async_session_maker() as session:
        # Delete in reverse order of foreign key dependencies
        await session.execute("DELETE FROM analytics_events")
        await session.execute("DELETE FROM bonuses")
        await session.execute("DELETE FROM team_members")
        await session.execute("DELETE FROM teams")
        await session.execute("DELETE FROM content")
        await session.execute("DELETE FROM workflows")
        await session.execute("DELETE FROM campaigns")
        await session.execute("DELETE FROM products")
        await session.execute("DELETE FROM users")
        await session.commit()

    print("Data cleared successfully")


async def seed_users():
    """Seed test users with different tiers."""
    print("Seeding users...")

    users_data = [
        {
            "email": "starter@test.com",
            "password": "Password123!",
            "full_name": "Starter User",
            "tier": "starter",
            "status": "trial",
        },
        {
            "email": "pro@test.com",
            "password": "Password123!",
            "full_name": "Professional User",
            "tier": "professional",
            "status": "active",
        },
        {
            "email": "agency@test.com",
            "password": "Password123!",
            "full_name": "Agency User",
            "tier": "agency",
            "status": "active",
        },
    ]

    users = []

    async with async_session_maker() as session:
        for user_data in users_data:
            user = User(
                id=uuid.uuid4(),
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                tier=user_data["tier"],
                status=user_data["status"],
                is_email_verified=True,
                trial_ends_at=datetime.utcnow() + timedelta(days=14)
                if user_data["status"] == "trial"
                else None,
            )
            session.add(user)
            users.append(user)

        await session.commit()

    print(f"Created {len(users)} users")
    return users


async def seed_products():
    """Seed ClickBank products."""
    print("Seeding products...")

    products_data = [
        {
            "clickbank_id": "CB_PRODUCT_001",
            "title": "Digital Marketing Mastery Course",
            "vendor": "MarketingPro",
            "category": "Business & Marketing",
            "description": "Complete digital marketing course covering SEO, PPC, social media, and email marketing.",
            "commission_rate": 50.00,
            "commission_amount": 49.50,
            "initial_sale_amount": 99.00,
            "gravity": 87.50,
            "refund_rate": 5.20,
            "rebill": True,
            "popularity_rank": 5,
        },
        {
            "clickbank_id": "CB_PRODUCT_002",
            "title": "Keto Diet Blueprint",
            "vendor": "HealthGuru",
            "category": "Health & Fitness",
            "description": "Complete keto diet guide with meal plans, recipes, and tracking tools.",
            "commission_rate": 75.00,
            "commission_amount": 29.25,
            "initial_sale_amount": 39.00,
            "gravity": 125.30,
            "refund_rate": 8.50,
            "rebill": False,
            "popularity_rank": 2,
        },
        {
            "clickbank_id": "CB_PRODUCT_003",
            "title": "Affiliate Profits Academy",
            "vendor": "AffiliateExperts",
            "category": "Business & Marketing",
            "description": "Learn proven affiliate marketing strategies from industry experts.",
            "commission_rate": 50.00,
            "commission_amount": 74.50,
            "initial_sale_amount": 149.00,
            "gravity": 95.80,
            "refund_rate": 6.30,
            "rebill": True,
            "popularity_rank": 8,
        },
        {
            "clickbank_id": "CB_PRODUCT_004",
            "title": "Meditation & Mindfulness Training",
            "vendor": "MindfulLiving",
            "category": "Self-Help",
            "description": "Comprehensive meditation and mindfulness training program.",
            "commission_rate": 60.00,
            "commission_amount": 17.94,
            "initial_sale_amount": 29.90,
            "gravity": 65.20,
            "refund_rate": 4.80,
            "rebill": True,
            "popularity_rank": 15,
        },
        {
            "clickbank_id": "CB_PRODUCT_005",
            "title": "Forex Trading Signals",
            "vendor": "TradingMaster",
            "category": "Finance & Investment",
            "description": "Daily forex trading signals with high accuracy and support.",
            "commission_rate": 50.00,
            "commission_amount": 49.50,
            "initial_sale_amount": 99.00,
            "gravity": 110.50,
            "refund_rate": 7.20,
            "rebill": True,
            "popularity_rank": 4,
        },
    ]

    products = []

    async with async_session_maker() as session:
        for product_data in products_data:
            product = Product(
                id=uuid.uuid4(),
                clickbank_id=product_data["clickbank_id"],
                title=product_data["title"],
                vendor=product_data["vendor"],
                category=product_data["category"],
                description=product_data["description"],
                commission_rate=product_data["commission_rate"],
                commission_amount=product_data["commission_amount"],
                initial_sale_amount=product_data["initial_sale_amount"],
                gravity=product_data["gravity"],
                refund_rate=product_data["refund_rate"],
                rebill=product_data["rebill"],
                popularity_rank=product_data["popularity_rank"],
                data_snapshot={
                    "last_updated": datetime.utcnow().isoformat(),
                    "trending": product_data["gravity"] > 100,
                },
                last_updated=datetime.utcnow(),
            )
            session.add(product)
            products.append(product)

        await session.commit()

    print(f"Created {len(products)} products")
    return products


async def seed_campaigns(users, products):
    """Seed campaigns for users."""
    print("Seeding campaigns...")

    campaigns = []

    async with async_session_maker() as session:
        # Create 2 campaigns for each user
        for user in users[:2]:  # Just first 2 users
            for i in range(2):
                product = products[i]
                campaign = Campaign(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    product_id=product.id,
                    name=f"{product.title} Campaign {i+1}",
                    status="active" if i == 0 else "draft",
                    funnel_type="email_series" if i == 0 else "blog_content",
                    affiliate_link=f"https://hop.clickbank.net/?affiliate={user.id}&vendor={product.clickbank_id}",
                    tracking_id=f"TRACK_{user.id}_{product.clickbank_id}_{i}",
                    settings={
                        "auto_publish": i == 0,
                        "platforms": ["wordpress", "social"],
                        "schedule": "daily",
                    },
                )
                session.add(campaign)
                campaigns.append(campaign)

        await session.commit()

    print(f"Created {len(campaigns)} campaigns")
    return campaigns


async def seed_content(users, campaigns):
    """Seed content for campaigns."""
    print("Seeding content...")

    content_items = []

    async with async_session_maker() as session:
        for campaign in campaigns:
            # Create blog post
            blog_post = Content(
                id=uuid.uuid4(),
                user_id=campaign.user_id,
                campaign_id=campaign.id,
                type="blog_post",
                title=f"Why {campaign.name} Is Perfect For You",
                body=f"""
# Introduction

Discover how {campaign.name} can transform your life. This comprehensive guide
covers everything you need to know about getting started.

## Key Benefits

- Proven results from thousands of satisfied customers
- Step-by-step implementation guide
- Ongoing support and updates
- Money-back guarantee

## Getting Started

Ready to begin your journey? Click the link below to learn more!

[Get Started Now]({campaign.affiliate_link})
                """.strip(),
                status="published" if campaign.status == "active" else "draft",
                metadata={
                    "word_count": 150,
                    "keywords": ["affiliate", "marketing", "guide"],
                },
                published_at=datetime.utcnow()
                if campaign.status == "active"
                else None,
            )
            session.add(blog_post)
            content_items.append(blog_post)

            # Create email
            email = Content(
                id=uuid.uuid4(),
                user_id=campaign.user_id,
                campaign_id=campaign.id,
                type="email",
                title=f"Exclusive Offer: {campaign.name}",
                body=f"""
Subject: Don't Miss This Limited Time Offer!

Hi there,

I wanted to share something special with you today. I've been using this product
and the results have been incredible.

{campaign.name} has helped me achieve:
- Better results in less time
- More efficient workflow
- Increased productivity

Click here to learn more: {campaign.affiliate_link}

To your success,
[Your Name]
                """.strip(),
                status="draft",
                metadata={
                    "subject_line": f"Exclusive Offer: {campaign.name}",
                    "preview_text": "Don't miss this limited time offer!",
                },
            )
            session.add(email)
            content_items.append(email)

        await session.commit()

    print(f"Created {len(content_items)} content items")
    return content_items


async def seed_workflows(users, campaigns):
    """Seed automation workflows."""
    print("Seeding workflows...")

    workflows = []

    async with async_session_maker() as session:
        for user in users[:2]:
            workflow = Workflow(
                id=uuid.uuid4(),
                user_id=user.id,
                name="Daily Content Automation",
                trigger_type="schedule",
                trigger_config={"cron": "0 9 * * *", "timezone": "UTC"},
                actions=[
                    {
                        "type": "generate_content",
                        "params": {"content_type": "blog_post", "ai_model": "claude-3"},
                    },
                    {"type": "publish_wordpress", "params": {"status": "draft"}},
                    {
                        "type": "post_social",
                        "params": {"platforms": ["twitter", "linkedin"]},
                    },
                ],
                conditions={"user_tier": ["professional", "agency"]},
                status="active",
                next_run_at=datetime.utcnow() + timedelta(hours=24),
            )
            session.add(workflow)
            workflows.append(workflow)

        await session.commit()

    print(f"Created {len(workflows)} workflows")
    return workflows


async def seed_analytics(users, campaigns):
    """Seed analytics events."""
    print("Seeding analytics events...")

    events = []

    async with async_session_maker() as session:
        for campaign in campaigns:
            # Create various events over the past 30 days
            for day in range(30):
                event_date = datetime.utcnow() - timedelta(days=day)

                # Clicks
                for _ in range(10):
                    click_event = AnalyticsEvent(
                        user_id=campaign.user_id,
                        campaign_id=campaign.id,
                        event_type="click",
                        source="blog",
                        metadata={"ip": "192.168.1.1", "user_agent": "Mozilla/5.0"},
                        created_at=event_date,
                    )
                    session.add(click_event)
                    events.append(click_event)

                # Conversions (10% conversion rate)
                if day % 10 == 0:
                    conversion_event = AnalyticsEvent(
                        user_id=campaign.user_id,
                        campaign_id=campaign.id,
                        event_type="conversion",
                        source="blog",
                        revenue=49.50,
                        metadata={"order_id": f"ORDER_{uuid.uuid4()}"},
                        created_at=event_date,
                    )
                    session.add(conversion_event)
                    events.append(conversion_event)

        await session.commit()

    print(f"Created {len(events)} analytics events")
    return events


async def main():
    """Main seed function."""
    print("=" * 50)
    print("Starting database seeding...")
    print("=" * 50)

    try:
        # Clear existing data
        await clear_data()

        # Seed data in order
        users = await seed_users()
        products = await seed_products()
        campaigns = await seed_campaigns(users, products)
        content = await seed_content(users, campaigns)
        workflows = await seed_workflows(users, campaigns)
        analytics = await seed_analytics(users, campaigns)

        print("=" * 50)
        print("Database seeding completed successfully!")
        print("=" * 50)
        print("\nTest Accounts:")
        print("-" * 50)
        print("Email: starter@test.com | Password: Password123! | Tier: Starter")
        print("Email: pro@test.com | Password: Password123! | Tier: Professional")
        print("Email: agency@test.com | Password: Password123! | Tier: Agency")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
