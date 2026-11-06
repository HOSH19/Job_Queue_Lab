"""Unit tests for job handlers."""

import pytest
from app.jobs.fail_handler import handle_fail
from app.jobs.handlers import run_handler
from app.jobs.http_handler import handle_http_fetch
from app.jobs.sleep_handler import handle_sleep


def test_handle_sleep() -> None:
    """Zero-second sleep returns slept=0."""
    assert handle_sleep({"seconds": 0}) == {"slept": 0.0}


def test_handle_sleep_rejects_out_of_range() -> None:
    """Seconds outside 0–10 raise ValueError."""
    with pytest.raises(ValueError, match="between 0 and 10"):
        handle_sleep({"seconds": 99})


def test_handle_fail() -> None:
    """Fail handler always raises."""
    with pytest.raises(RuntimeError, match="boom"):
        handle_fail({"message": "boom"})


def test_http_fetch_blocks_localhost() -> None:
    """Localhost targets are rejected as SSRF."""
    with pytest.raises(ValueError, match="not allowed|blocked"):
        handle_http_fetch({"url": "http://localhost/secret"})


def test_http_fetch_requires_url() -> None:
    """Missing url raises ValueError."""
    with pytest.raises(ValueError, match="url is required"):
        handle_http_fetch({})


def test_run_handler_unknown() -> None:
    """Unknown types raise ValueError."""
    with pytest.raises(ValueError, match="unknown job type"):
        run_handler("nope", {})
