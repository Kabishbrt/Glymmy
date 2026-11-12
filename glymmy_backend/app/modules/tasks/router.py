"""Task queue routes — async food prediction."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.adapters.storage import get_storage_adapter
from app.core.auth import AuthenticatedUser, get_current_user
from app.modules.tasks.schemas import TaskResponse
from app.modules.tasks.service import run_food_prediction
from app.modules.tasks.store import create_task, get_task

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/food-predict")
async def submit_food_prediction(
    image: UploadFile | None = File(None),
    description: str | None = Form(None),
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    """Submit a food prediction task. Returns task_id for polling."""
    if not image and not description:
        raise HTTPException(status_code=422, detail="Provide an image or description")

    image_path = None
    if image:
        storage = get_storage_adapter()
        content = await image.read()
        image_path = storage.save_upload(image.filename or "food.jpg", content)

    task_id = create_task("food-predict")
    asyncio.create_task(
        run_food_prediction(task_id, image_path, description, user.internal_id)
    )
    return {"task_id": task_id}


@router.get("/{task_id}", response_model=TaskResponse)
async def poll_task(task_id: str) -> TaskResponse:
    """Poll a task's status and result."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task)
