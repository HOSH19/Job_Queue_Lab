"""Cached Redis connection shared by queue helpers."""

from __future__ import annotations

from redis import Redis

from app.config import get_settings

_settings = get_settings()
_client: Redis | None = None


def get_redis() -> Redis:
    """Return a process-wide Redis client."""
    global _client
    if _client is None:
        _client = Redis.from_url(_settings.redis_url, decode_responses=True)
    return _client


def reset_redis_client() -> None:
    """Drop the cached client so the next call reconnects (tests)."""
    global _client
    _client = None


def settings():
    """Expose queue-related settings for helpers in this package."""
    return _settings


def ping_redis() -> bool:
    """Return True when Redis answers PING."""
    try:
        return bool(get_redis().ping())
    except Exception:
        return False
