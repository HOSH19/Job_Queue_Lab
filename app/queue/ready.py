"""Ready-work ZSET: enqueue, dequeue, remove, depth."""

from __future__ import annotations

from datetime import UTC, datetime

from app.queue.client import get_redis, settings
from app.queue.scoring import priority_score


def enqueue(job_id: str, priority: int = 0, run_at: datetime | None = None) -> None:
    """
    Place a job on the ready set, or on the delayed set when run_at is future.
    """
    from app.queue.delayed import schedule_delayed

    cfg = settings()
    client = get_redis()
    now = datetime.now(UTC)
    if run_at is not None:
        when = run_at if run_at.tzinfo else run_at.replace(tzinfo=UTC)
        if when > now:
            schedule_delayed(job_id, when)
            return
    client.zadd(cfg.queue_key, {job_id: priority_score(priority, run_at)})


def dequeue(timeout: int = 5) -> str | None:
    """Block until a ready job id appears, else return None on timeout."""
    from app.queue.delayed import promote_delayed

    promote_delayed()
    item = get_redis().bzpopmin(settings().queue_key, timeout=timeout)
    if item is None:
        return None
    _name, job_id, _score = item
    return job_id


def remove_from_queue(job_id: str) -> bool:
    """Remove a job id from ready and delayed sets."""
    from app.queue.delayed import remove_delayed

    cfg = settings()
    client = get_redis()
    removed = client.zrem(cfg.queue_key, job_id)
    removed += 1 if remove_delayed(job_id) else 0
    return removed > 0


def ready_depth() -> int:
    """Count members on the ready ZSET."""
    return int(get_redis().zcard(settings().queue_key))
