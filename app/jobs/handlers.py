"""Registry that maps job type names to handler callables."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.jobs.fail_handler import handle_fail
from app.jobs.http_handler import handle_http_fetch
from app.jobs.sleep_handler import handle_sleep

Handler = Callable[[dict[str, Any]], dict[str, Any]]

HANDLERS: dict[str, Handler] = {
    "sleep": handle_sleep,
    "http_fetch": handle_http_fetch,
    "fail": handle_fail,
}


def run_handler(job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Dispatch to the registered handler or raise for unknown types."""
    handler = HANDLERS.get(job_type)
    if handler is None:
        raise ValueError(f"unknown job type: {job_type}")
    return handler(payload)
