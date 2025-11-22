"""
Initialize database with default data
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.db.base import Base
from app.models.user import User
from app.core.security import get_password_hash


async def init_db() -> None:
    """
    Initialize database with tables and default data
    """
    async with async_session_maker() as session:
        # Create test user if in development
        from app.config import settings

        if settings.APP_ENV == "development":
            # Check if test user exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == "admin@test.com")
            )
            user = result.scalar_one_or_none()

            if not user:
                test_user = User(
                    email="admin@test.com",
                    password_hash=get_password_hash("admin123"),
                    full_name="Test Admin",
                    tier="agency",
                    status="active"
                )
                session.add(test_user)
                await session.commit()
                print("Test user created: admin@test.com / admin123")


if __name__ == "__main__":
    asyncio.run(init_db())
