"""Sleep job handler for timing demos."""

from __future__ import annotations

import time
from typing import Any


def handle_sleep(payload: dict[str, Any]) -> dict[str, Any]:
    """Sleep for payload['seconds'] (0–10) and return how long slept."""
    seconds = float(payload.get("seconds", 1))
    if seconds < 0 or seconds > 10:
        raise ValueError("seconds must be between 0 and 10")
    time.sleep(seconds)
    return {"slept": seconds}
