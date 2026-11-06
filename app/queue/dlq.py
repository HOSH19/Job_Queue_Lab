"""Dead-letter list for permanently failed jobs."""

from __future__ import annotations

from app.queue.client import get_redis, settings


def push_dlq(job_id: str) -> None:
    """Push a job id onto the dead-letter list."""
    get_redis().lpush(settings().dlq_key, job_id)


def list_dlq(limit: int = 50) -> list[str]:
    """Return the newest dead-letter job ids."""
    return get_redis().lrange(settings().dlq_key, 0, limit - 1)
