"""
FastAPI dependencies
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.config import settings

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials

    # Decode and validate token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Get user from database
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended"
        )

    return user


async def get_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (not on trial or canceled)
    """
    if current_user.status not in ["active", "trial"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not active"
        )
    return current_user


async def check_tier_access(
    required_tier: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Check if user has required tier access
    """
    tier_hierarchy = {"starter": 1, "professional": 2, "agency": 3}

    user_tier_level = tier_hierarchy.get(current_user.tier, 0)
    required_tier_level = tier_hierarchy.get(required_tier, 0)

    if user_tier_level < required_tier_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This feature requires {required_tier} tier or higher"
        )

    return current_user
