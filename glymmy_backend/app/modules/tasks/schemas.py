"""Task queue schemas."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class TaskStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    created_at: str
    completed_at: str | None = None
    result: Any | None = None
    error: str | None = None
