"""In-memory task store. Resets on server restart."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

_tasks: dict[str, dict[str, Any]] = {}


def create_task(task_type: str) -> str:
    task_id = uuid4().hex[:12]
    _tasks[task_id] = {
        "task_id": task_id,
        "type": task_type,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "result": None,
        "error": None,
    }
    return task_id


def update_task(
    task_id: str,
    status: str,
    result: Any = None,
    error: str | None = None,
) -> None:
    task = _tasks.get(task_id)
    if not task:
        return
    task["status"] = status
    if result is not None:
        task["result"] = result
    if error is not None:
        task["error"] = error
    if status in ("completed", "failed"):
        task["completed_at"] = datetime.now().isoformat()


def get_task(task_id: str) -> dict[str, Any] | None:
    return _tasks.get(task_id)
