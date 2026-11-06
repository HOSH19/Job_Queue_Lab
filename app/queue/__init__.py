"""Redis queue facade used by the API and worker."""

from app.queue.client import get_redis, ping_redis, reset_redis_client
from app.queue.delayed import delayed_depth, promote_delayed
from app.queue.dlq import list_dlq, push_dlq
from app.queue.events import publish_event
from app.queue.ready import dequeue, enqueue, ready_depth, remove_from_queue


def queue_depth() -> int:
    """Ready plus delayed backlog size."""
    return ready_depth() + delayed_depth()


__all__ = [
    "dequeue",
    "enqueue",
    "get_redis",
    "list_dlq",
    "ping_redis",
    "promote_delayed",
    "publish_event",
    "push_dlq",
    "queue_depth",
    "remove_from_queue",
    "reset_redis_client",
]
