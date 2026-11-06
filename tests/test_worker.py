"""Worker job finalization paths."""

from __future__ import annotations

import json
from unittest.mock import patch

from app.models import Job, JobStatus, utcnow
from app.worker_job import process_job


def _job(**kwargs) -> Job:
    """Build a Job ORM instance with sensible defaults."""
    defaults = dict(
        id="22222222-2222-2222-2222-222222222222",
        type="sleep",
        payload=json.dumps({"seconds": 0}),
        status=JobStatus.queued.value,
        attempts=0,
        max_attempts=3,
        priority=0,
        created_at=utcnow(),
        updated_at=utcnow(),
    )
    defaults.update(kwargs)
    return Job(**defaults)


def test_process_job_success(db_session) -> None:
    """A successful handler should leave status succeeded."""
    job = _job()
    db_session.add(job)
    db_session.commit()
    job_id = job.id

    with (
        patch("app.worker_job.SessionLocal", return_value=db_session),
        patch("app.worker_job.publish_event"),
        patch("app.worker_job.run_handler", return_value={"slept": 0}),
        patch.object(db_session, "close"),
    ):
        process_job(job_id)

    updated = db_session.get(Job, job_id)
    assert updated is not None
    assert updated.status == JobStatus.succeeded.value
    assert json.loads(updated.result or "{}") == {"slept": 0}


def test_process_job_retries_then_dlq(db_session) -> None:
    """Exhausted attempts should mark dead and push DLQ."""
    job = _job(type="fail", payload=json.dumps({"message": "nope"}), max_attempts=1)
    db_session.add(job)
    db_session.commit()
    job_id = job.id

    with (
        patch("app.worker_job.SessionLocal", return_value=db_session),
        patch("app.worker_job.publish_event"),
        patch("app.worker_job.push_dlq") as mock_dlq,
        patch("app.worker_job.enqueue") as mock_enqueue,
        patch.object(db_session, "close"),
    ):
        process_job(job_id)

    updated = db_session.get(Job, job_id)
    assert updated is not None
    assert updated.status == JobStatus.dead.value
    mock_dlq.assert_called_once_with(job_id)
    mock_enqueue.assert_not_called()


def test_process_job_skips_cancelled(db_session) -> None:
    """Cancelled jobs must not invoke the handler."""
    job = _job(status=JobStatus.cancelled.value)
    db_session.add(job)
    db_session.commit()
    job_id = job.id

    with (
        patch("app.worker_job.SessionLocal", return_value=db_session),
        patch("app.worker_job.publish_event"),
        patch("app.worker_job.run_handler") as mock_run,
        patch.object(db_session, "close"),
    ):
        process_job(job_id)

    mock_run.assert_not_called()
