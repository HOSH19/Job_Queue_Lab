"""Priority scores for the ready ZSET."""

from __future__ import annotations

from datetime import UTC, datetime


def priority_score(priority: int, run_at: datetime | None = None) -> float:
    """
    Build a BZPOPMIN score: higher priority pops first, then earlier time.

    Score = (-priority * large_constant) + unix_timestamp.
    """
    when = run_at or datetime.now(UTC)
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    return (-priority * 1_000_000_000_000) + when.timestamp()
