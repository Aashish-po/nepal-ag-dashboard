"""
Redis cache invalidation for the Nepal Agricultural Intelligence Dashboard.

Uses Upstash Redis in production, falls back gracefully when Redis is unavailable.
"""

from __future__ import annotations

import logging
import os

import redis.asyncio as redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "")

_redis_client: redis.Redis | None = None


def _get_redis_client() -> redis.Redis | None:
    """Return a Redis client instance, or None if Redis is not configured."""
    global _redis_client
    if REDIS_URL and _redis_client is None:
        try:
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        except RedisError as e:
            logger.warning("Could not connect to Redis: %s", e)
            _redis_client = None
    return _redis_client


async def invalidate_cache(pattern: str) -> int:
    """Delete all cache keys matching a pattern. Returns the number deleted."""
    client = _get_redis_client()
    if client is None:
        return 0

    try:
        deleted = 0
        batch: list[str] = []
        async for key in client.scan_iter(match=pattern, count=500):
            batch.append(key)
            if len(batch) >= 500:
                deleted += await client.delete(*batch)
                batch.clear()
        if batch:
            deleted += await client.delete(*batch)
        if deleted:
            logger.info("Invalidated %d cache keys matching %s", deleted, pattern)
        return deleted
    except RedisError as e:
        logger.warning("Cache invalidate error for pattern %s: %s", pattern, e)
        return 0


async def invalidate_all_cache() -> None:
    """Invalidate all cache keys (district summaries, forecasts, heatmaps)."""
    patterns = [
        "cache:summary:*",
        "cache:forecast:*",
        "cache:heatmap:*",
        "cache:correlation:*",
    ]
    for pattern in patterns:
        await invalidate_cache(pattern)
