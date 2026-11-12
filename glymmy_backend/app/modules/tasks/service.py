"""Task execution — runs food prediction asynchronously."""

from __future__ import annotations

from loguru import logger

from app.modules.tasks.store import update_task


async def run_food_prediction(
    task_id: str,
    image_path: str | None,
    description: str | None,
    user_id: str | None,
) -> None:
    """Execute a food prediction task in the background."""
    update_task(task_id, "processing")
    try:
        from app.modules.food.service import analyze_food_image, analyze_food_text

        if image_path:
            result = await analyze_food_image(image_path, patient_id=None, user_id=user_id)
        elif description:
            result = await analyze_food_text(description, patient_id=None, user_id=user_id)
        else:
            update_task(task_id, "failed", error="No image or description provided")
            return

        update_task(task_id, "completed", result=result.model_dump())
        logger.info(f"Task {task_id} completed successfully")

    except Exception as exc:
        logger.error(f"Task {task_id} failed: {exc}")
        update_task(task_id, "failed", error=str(exc))
