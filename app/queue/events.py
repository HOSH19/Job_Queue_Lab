"""Redis pub/sub fan-out for UI live updates."""

from __future__ import annotations

import json

from app.queue.client import get_redis, settings


def publish_event(event: dict) -> None:
    """Publish a JSON job lifecycle event on the events channel."""
    get_redis().publish(settings().events_channel, json.dumps(event, default=str))
