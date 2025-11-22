"""
Redis caching utilities
"""
import json
from typing import Optional, Any
import redis.asyncio as redis

from app.config import settings

# Create Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """
    Get Redis client instance
    """
    global redis_client

    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    """
    Get value from cache
    """
    client = await get_redis()
    value = await client.get(key)

    if value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    return None


async def cache_set(key: str, value: Any, ttl: int = None) -> bool:
    """
    Set value in cache with optional TTL
    """
    client = await get_redis()

    if ttl is None:
        ttl = settings.REDIS_CACHE_TTL

    # Serialize value
    if isinstance(value, (dict, list)):
        value = json.dumps(value)

    await client.setex(key, ttl, value)
    return True


async def cache_delete(key: str) -> bool:
    """
    Delete key from cache
    """
    client = await get_redis()
    await client.delete(key)
    return True


async def cache_clear_pattern(pattern: str) -> int:
    """
    Delete all keys matching pattern
    """
    client = await get_redis()
    keys = await client.keys(pattern)

    if keys:
        return await client.delete(*keys)

    return 0
