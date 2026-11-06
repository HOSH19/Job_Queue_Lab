"""Queue behavior against fakeredis."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import fakeredis
import pytest
from app import queue as queue_mod
from app.queue import client as queue_client


@pytest.fixture()
def fake_redis(monkeypatch: pytest.MonkeyPatch):
    """Install an in-memory Redis and stable queue key names."""
    server = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(queue_client, "_client", server)
    cfg = queue_client.settings()
    monkeypatch.setattr(cfg, "queue_key", "jobqueue:jobs")
    monkeypatch.setattr(cfg, "delayed_key", "jobqueue:delayed")
    monkeypatch.setattr(cfg, "dlq_key", "jobqueue:dlq")
    return server


def test_enqueue_and_dequeue_priority(fake_redis) -> None:
    """Higher priority ids should pop before lower ones."""
    queue_mod.enqueue("low", priority=1)
    queue_mod.enqueue("high", priority=9)
    assert queue_mod.dequeue(timeout=1) == "high"
    assert queue_mod.dequeue(timeout=1) == "low"


def test_delayed_then_promote(fake_redis) -> None:
    """Future run_at stays delayed until promoted."""
    future = datetime.now(UTC) + timedelta(hours=1)
    queue_mod.enqueue("later", priority=0, run_at=future)
    assert queue_mod.dequeue(timeout=1) is None
    fake_redis.zadd(queue_client.settings().delayed_key, {"later": 0})
    assert queue_mod.promote_delayed() == 1
    assert queue_mod.dequeue(timeout=1) == "later"


def test_remove_from_queue(fake_redis) -> None:
    """Removing a ready id should leave the queue empty."""
    queue_mod.enqueue("x", priority=0)
    assert queue_mod.remove_from_queue("x") is True
    assert queue_mod.dequeue(timeout=1) is None


def test_dlq(fake_redis) -> None:
    """DLQ stores failed ids in list order."""
    queue_mod.push_dlq("dead-1")
    assert queue_mod.list_dlq() == ["dead-1"]
