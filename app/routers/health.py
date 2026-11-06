"""Liveness of Redis and Postgres."""

from fastapi import APIRouter

from app.db import ping_db
from app.queue import ping_redis
from app.schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    """Report dependency health for dashboards and probes."""
    redis_ok = ping_redis()
    db_ok = ping_db()
    return HealthOut(
        status="ok" if redis_ok and db_ok else "degraded",
        redis="up" if redis_ok else "down",
        database="up" if db_ok else "down",
    )
