"""Shared fixtures: in-memory SQLite and mocked Redis side effects."""

from __future__ import annotations

import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from app.db import get_db
from app.main import app
from app.models import Base, Job, JobStatus, utcnow
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide an isolated in-memory SQLite session per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """HTTP client with DB override and Redis helpers mocked."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    mock_enqueue = MagicMock()
    mock_remove = MagicMock(return_value=True)
    mock_publish = MagicMock()
    mock_list_dlq = MagicMock(return_value=[])
    mock_queue_depth = MagicMock(return_value=0)

    with (
        patch("app.main.init_db"),
        patch("app.services.job_service.enqueue", mock_enqueue),
        patch("app.services.job_service.remove_from_queue", mock_remove),
        patch("app.services.job_service.publish_event", mock_publish),
        patch("app.routers.dlq.list_dlq", mock_list_dlq),
        patch("app.routers.metrics_route.queue_depth", mock_queue_depth),
        patch("app.routers.health.ping_redis", return_value=True),
        patch("app.routers.health.ping_db", return_value=True),
        TestClient(app) as test_client,
    ):
        test_client.mock_enqueue = mock_enqueue  # type: ignore[attr-defined]
        test_client.mock_remove = mock_remove  # type: ignore[attr-defined]
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def queued_job(db_session: Session) -> Job:
    """Insert a queued sleep job used by cancel/get tests."""
    job = Job(
        id="11111111-1111-1111-1111-111111111111",
        type="sleep",
        payload=json.dumps({"seconds": 1}),
        status=JobStatus.queued.value,
        attempts=0,
        max_attempts=3,
        priority=0,
        created_at=utcnow(),
        updated_at=utcnow(),
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job
