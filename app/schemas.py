from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models import JobStatus, JobType


class JobCreate(BaseModel):
    type: JobType
    payload: dict[str, Any] = Field(default_factory=dict)
    max_attempts: int | None = Field(default=None, ge=1, le=10)
    priority: int = Field(default=0, ge=0, le=10)
    run_at: datetime | None = None


class JobOut(BaseModel):
    id: str
    type: str
    payload: dict[str, Any]
    status: JobStatus
    result: dict[str, Any] | None = None
    error: str | None = None
    attempts: int
    max_attempts: int
    priority: int = 0
    run_at: datetime | None = None
    idempotency_key: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status: str
    redis: str
    database: str


class DlqItem(BaseModel):
    job_id: str
