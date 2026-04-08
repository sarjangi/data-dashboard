"""Redis cache configuration and utilities."""

import json
from typing import Any, Optional
import redis.asyncio as redis

from app.core.config import settings

# Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_cached(key: str) -> Optional[Any]:
    """Get cached value by key."""
    client = await get_redis()
    value = await client.get(key)
    if value:
        return json.loads(value)
    return None


async def set_cached(key: str, value: Any, ttl: int = 3600):
    """Set cached value with TTL (Time To Live)."""
    client = await get_redis()
    await client.setex(key, ttl, json.dumps(value, default=str))


async def delete_cached(key: str):
    """Delete cached value."""
    client = await get_redis()
    await client.delete(key)


async def clear_cache_pattern(pattern: str):
    """Clear all cache keys matching pattern."""
    client = await get_redis()
    keys = await client.keys(pattern)
    if keys:
        await client.delete(*keys)
