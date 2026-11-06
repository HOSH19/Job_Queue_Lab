from __future__ import annotations

from unittest.mock import patch

from app.config import get_settings
from app.models import Job, JobStatus


def test_health(client) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["redis"] == "up"
    assert body["database"] == "up"


def test_create_and_list_job(client) -> None:
    res = client.post("/jobs", json={"type": "sleep", "payload": {"seconds": 1}, "priority": 5})
    assert res.status_code == 201
    job = res.json()
    assert job["status"] == "queued"
    assert job["priority"] == 5
    client.mock_enqueue.assert_called_once()

    listed = client.get("/jobs")
    assert listed.status_code == 200
    assert any(j["id"] == job["id"] for j in listed.json())


def test_get_job(client, queued_job: Job) -> None:
    res = client.get(f"/jobs/{queued_job.id}")
    assert res.status_code == 200
    assert res.json()["id"] == queued_job.id


def test_get_missing_job(client) -> None:
    res = client.get("/jobs/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404


def test_cancel_queued_job(client, queued_job: Job) -> None:
    res = client.post(f"/jobs/{queued_job.id}/cancel")
    assert res.status_code == 200
    assert res.json()["status"] == "cancelled"
    client.mock_remove.assert_called_once_with(queued_job.id)


def test_cancel_non_queued_rejected(client, db_session, queued_job: Job) -> None:
    queued_job.status = JobStatus.running.value
    db_session.commit()
    res = client.post(f"/jobs/{queued_job.id}/cancel")
    assert res.status_code == 409


def test_idempotency_key_returns_same_job(client) -> None:
    headers = {"Idempotency-Key": "demo-key-1"}
    first = client.post(
        "/jobs",
        json={"type": "sleep", "payload": {"seconds": 1}},
        headers=headers,
    )
    second = client.post(
        "/jobs",
        json={"type": "sleep", "payload": {"seconds": 1}},
        headers=headers,
    )
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert client.mock_enqueue.call_count == 1


def test_metrics_endpoint(client) -> None:
    res = client.get("/metrics")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/plain")
    assert len(res.content) > 0


def test_dlq_list(client) -> None:
    res = client.get("/dlq")
    assert res.status_code == 200
    assert res.json() == []


def test_api_key_required_when_configured(client) -> None:
    locked = get_settings().model_copy(update={"api_key": "secret"})
    with patch("app.auth.get_settings", return_value=locked):
        denied = client.post("/jobs", json={"type": "fail", "payload": {}})
        assert denied.status_code == 401
        ok = client.post(
            "/jobs",
            json={"type": "fail", "payload": {}},
            headers={"X-API-Key": "secret"},
        )
        assert ok.status_code == 201
