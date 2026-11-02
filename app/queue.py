from redis import Redis

from app.config import get_settings

_settings = get_settings()
_client: Redis | None = None


def get_redis() -> Redis:
    global _client
    if _client is None:
        _client = Redis.from_url(_settings.redis_url, decode_responses=True)
    return _client


def enqueue(job_id: str) -> None:
    get_redis().lpush(_settings.queue_key, job_id)


def dequeue(timeout: int = 5) -> str | None:
    """Block until a job id is available. Returns None on timeout."""
    item = get_redis().brpop(_settings.queue_key, timeout=timeout)
    if item is None:
        return None
    _queue_name, job_id = item
    return job_id


def ping_redis() -> bool:
    try:
        return bool(get_redis().ping())
    except Exception:
        return False
