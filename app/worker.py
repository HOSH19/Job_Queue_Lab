"""Worker process: poll Redis and hand jobs to worker_job."""

from __future__ import annotations

import logging
import signal
import sys
import time

from app.config import get_settings
from app.db import init_db
from app.logging_config import configure_logging
from app.metrics import QUEUE_DEPTH
from app.queue import dequeue, promote_delayed, queue_depth
from app.worker_job import process_job

configure_logging("worker")
log = logging.getLogger("worker")
_running = True


def _handle_signal(signum: int, _frame: object) -> None:
    """Request a graceful stop after the current job."""
    global _running
    log.info("received signal %s, shutting down after current job", signum)
    _running = False


def main() -> None:
    """Run the blocking worker loop until SIGINT/SIGTERM."""
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)
    settings = get_settings()
    init_db()
    log.info(
        "worker started queue=%s delayed=%s dlq=%s max_attempts_default=%s",
        settings.queue_key,
        settings.delayed_key,
        settings.dlq_key,
        settings.max_attempts,
    )
    while _running:
        _tick()
    log.info("worker stopped")


def _tick() -> None:
    """Promote delayed work, dequeue one job, and process it."""
    try:
        promote_delayed()
        try:
            QUEUE_DEPTH.set(queue_depth())
        except Exception:
            pass
        job_id = dequeue(timeout=2)
    except Exception:
        log.exception("dequeue failed; sleeping briefly")
        time.sleep(1)
        return
    if job_id is None:
        return
    try:
        process_job(job_id)
    except Exception:
        log.exception("unexpected error processing %s", job_id)


if __name__ == "__main__":
    main()
    sys.exit(0)
