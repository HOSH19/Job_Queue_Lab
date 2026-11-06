"""Delayed / scheduled jobs held in a Redis ZSET."""

from __future__ import annotations

import time
from datetime import datetime

from app.queue.client import get_redis, settings
from app.queue.scoring import priority_score


def schedule_delayed(job_id: str, when: datetime) -> None:
    """Store a job to become ready at the given time."""
    get_redis().zadd(settings().delayed_key, {job_id: when.timestamp()})


def remove_delayed(job_id: str) -> bool:
    """Remove a delayed job id. Returns True if it was present."""
    return bool(get_redis().zrem(settings().delayed_key, job_id))


def promote_delayed(limit: int = 50) -> int:
    """Move due delayed jobs onto the ready ZSET. Returns how many moved."""
    cfg = settings()
    client = get_redis()
    now = time.time()
    due = client.zrangebyscore(cfg.delayed_key, min="-inf", max=now, start=0, num=limit)
    promoted = 0
    for job_id in due:
        if client.zrem(cfg.delayed_key, job_id):
            client.zadd(cfg.queue_key, {job_id: priority_score(0)})
            promoted += 1
    return promoted


def delayed_depth() -> int:
    """Count members still waiting on the delayed ZSET."""
    return int(get_redis().zcard(settings().delayed_key))
