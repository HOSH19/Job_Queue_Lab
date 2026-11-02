import time
from typing import Any, Callable

import httpx

Handler = Callable[[dict[str, Any]], dict[str, Any]]


def handle_sleep(payload: dict[str, Any]) -> dict[str, Any]:
    seconds = float(payload.get("seconds", 1))
    if seconds < 0 or seconds > 10:
        raise ValueError("seconds must be between 0 and 10")
    time.sleep(seconds)
    return {"slept": seconds}


def handle_http_fetch(payload: dict[str, Any]) -> dict[str, Any]:
    url = payload.get("url")
    if not url or not isinstance(url, str):
        raise ValueError("url is required")
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        response = client.get(url)
    return {
        "url": url,
        "status_code": response.status_code,
        "body_length": len(response.content),
    }


def handle_fail(payload: dict[str, Any]) -> dict[str, Any]:
    message = str(payload.get("message", "intentional failure"))
    raise RuntimeError(message)


HANDLERS: dict[str, Handler] = {
    "sleep": handle_sleep,
    "http_fetch": handle_http_fetch,
    "fail": handle_fail,
}


def run_handler(job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    handler = HANDLERS.get(job_type)
    if handler is None:
        raise ValueError(f"unknown job type: {job_type}")
    return handler(payload)
