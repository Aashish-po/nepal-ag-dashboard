"""
Redis caching service for the Nepal Agricultural Intelligence Dashboard.

Provides async helpers for storing and retrieving cached API responses.
Uses Upstash Redis in production, falls back gracefully when Redis is unavailable.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, cast

import redis.asyncio as redis

logger = logging.getLogger(__name__)


def _json_default(obj):
    """Custom JSON encoder for Decimal and date/datetime types."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return str(obj)


logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "")

# --------------------------------------------------------------------------- #
# Redis client (lazily initialised)
# --------------------------------------------------------------------------- #

_redis_client: Optional[redis.Redis] = None


def _get_redis_client() -> Optional[redis.Redis]:
    """Return a Redis client instance, or None if Redis is not configured."""
    global _redis_client
    if REDIS_URL and _redis_client is None:
        try:
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        except Exception as e:
            logger.warning("Could not connect to Redis: %s", e)
            _redis_client = None
    return _redis_client


# --------------------------------------------------------------------------- #
# Cache operations
# --------------------------------------------------------------------------- #


async def get_cached(key: str, db=None) -> Optional[dict]:
    """Retrieve a cached value from Redis.

    Args:
        key: Cache key (e.g., ``cache:summary:1:2024``).
        db: Unused; kept for compatibility with call sites that pass a DB session.

    Returns:
        Cached dict or None if not found / Redis unavailable.
    """
    client = _get_redis_client()
    if client is None:
        return None

    try:
        raw = await client.get(key)
        if raw is None:
            return None
        data = json.loads(raw)
        if isinstance(data, dict):
            return cast(dict[Any, Any], data)
        return None
    except Exception as e:
        logger.warning("Cache GET error for key %s: %s", key, e)
        return None


async def set_cached(
    key: str,
    value: dict,
    ttl_seconds: int = 86400,
    db=None,
) -> bool:
    """Store a value in Redis cache.

    Args:
        key: Cache key.
        value: Dict to cache.
        ttl_seconds: Time-to-live in seconds (default: 1 day).
        db: Unused; kept for compatibility.

    Returns:
        True if stored successfully, False otherwise.
    """
    client = _get_redis_client()
    if client is None:
        return False

    try:
        await client.setex(key, ttl_seconds, json.dumps(value, default=_json_default))
        return True
    except Exception as e:
        logger.warning("Cache SET error for key %s: %s", key, e)
        return False


async def invalidate_cache(pattern: str, db=None) -> int:
    """Delete all cache keys matching a pattern.

    Args:
        pattern: Redis key pattern (e.g., ``cache:summary:*``).
        db: Unused; kept for compatibility.

    Returns:
        Number of keys deleted.
    """
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
    except Exception as e:
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
