"""Pydantic schemas for the food module."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.modules.glucose.schemas import SpikePredictionResponse


class FoodItem(BaseModel):
    name: str
    portion: str = ""
    calories: float = 0
    carbs_g: float = 0
    protein_g: float = 0
    fat_g: float = 0
    fiber_g: float = 0


class NutritionTotal(BaseModel):
    calories: float
    carbs_g: float
    protein_g: float
    fat_g: float
    fiber_g: float


class FoodAnalysisResponse(BaseModel):
    items: list[FoodItem]
    total: NutritionTotal
    glucose_prediction: SpikePredictionResponse
    source: str  # vision-llm | text-only


class FoodTextRequest(BaseModel):
    description: str = Field(..., min_length=2)
    patient_id: str | None = None
    user_id: str | None = None
