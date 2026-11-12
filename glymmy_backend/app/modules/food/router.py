"""Food FastAPI routes."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from app.adapters.storage import get_storage_adapter
from app.modules.food.schemas import FoodAnalysisResponse, FoodTextRequest
from app.modules.food.service import analyze_food_image, analyze_food_text

router = APIRouter(prefix="/api/v1/food", tags=["food"])


@router.post("/scan", response_model=FoodAnalysisResponse)
async def scan_food(
    image: UploadFile = File(...),
    patient_id: str | None = Form(None),
    user_id: str | None = Form(None),
) -> FoodAnalysisResponse:
    """Upload a photo of a meal → identify + estimate nutrition + predict spike.

    Pass `user_id` to use the user's latest CGM reading for personalized prediction.
    """
    storage = get_storage_adapter()
    content = await image.read()
    path = storage.save_upload(image.filename or "upload.jpg", content)
    return await analyze_food_image(path, patient_id=patient_id, user_id=user_id)


@router.post("/analyze-text", response_model=FoodAnalysisResponse)
async def analyze_text(req: FoodTextRequest) -> FoodAnalysisResponse:
    """Describe a meal in text → estimate nutrition + predict spike."""
    return await analyze_food_text(req.description, patient_id=req.patient_id, user_id=req.user_id)
