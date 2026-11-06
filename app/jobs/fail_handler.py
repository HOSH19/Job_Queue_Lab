"""Intentional-failure handler for retry and DLQ demos."""

from __future__ import annotations

from typing import Any


def handle_fail(payload: dict[str, Any]) -> dict[str, Any]:
    """Always raise RuntimeError using payload['message']."""
    message = str(payload.get("message", "intentional failure"))
    raise RuntimeError(message)
