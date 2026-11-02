from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models import JobStatus, JobType


class JobCreate(BaseModel):
    type: JobType
    payload: dict[str, Any] = Field(default_factory=dict)
    max_attempts: int | None = Field(default=None, ge=1, le=10)


class JobOut(BaseModel):
    id: str
    type: str
    payload: dict[str, Any]
    status: JobStatus
    result: dict[str, Any] | None = None
    error: str | None = None
    attempts: int
    max_attempts: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status: str
    redis: str
