"""Food module business logic.

Uses the multimodal LLM (Gemma 4) to turn a photo or text description
into structured nutrition data, then feeds the macros into the glucose
spike prediction model.
"""

from __future__ import annotations

import json
import re
from typing import Any

from loguru import logger

from app.adapters.llm import get_llm_adapter
from app.modules.food.schemas import (
    FoodAnalysisResponse,
    FoodItem,
    NutritionTotal,
)
from app.modules.glucose.schemas import MealInput
from app.modules.glucose.service import predict_meal_spike

FOOD_PROMPT = """You are Glymmy, a nutrition analysis AI.

Analyze the food described and return a JSON object with this exact structure
(no prose outside the JSON):

{
  "items": [
    {"name": str, "portion": str, "calories": number, "carbs_g": number,
     "protein_g": number, "fat_g": number, "fiber_g": number}
  ],
  "total": {"calories": number, "carbs_g": number, "protein_g": number,
            "fat_g": number, "fiber_g": number}
}

Use USDA FoodData Central values. For South Asian dishes (dal, rice, roti,
biryani, momo, samosa), use regionally-appropriate values. Be realistic
about portion sizes.
"""


def _parse_json(text: str) -> dict[str, Any]:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No JSON found in LLM response")


async def analyze_food_image(
    image_path: str,
    patient_id: str | None,
    user_id: str | None = None,
) -> FoodAnalysisResponse:
    """Identify + estimate nutrition from an image, then predict spike."""
    llm = get_llm_adapter()
    if not llm.supports_vision:
        raise RuntimeError(f"LLM provider {llm.provider_name} does not support vision")

    messages = [
        {"role": "system", "content": FOOD_PROMPT},
        {
            "role": "user",
            "content": "Identify every food item in this photo and provide nutrition data.",
        },
    ]
    raw = await llm.chat_with_image(messages, image_path=image_path, temperature=0.1)
    logger.debug(f"Vision LLM raw response: {raw[:300]}")
    data = _parse_json(raw)

    return _build_response(data, patient_id, source="vision-llm", user_id=user_id)


async def analyze_food_text(
    description: str,
    patient_id: str | None,
    user_id: str | None = None,
) -> FoodAnalysisResponse:
    """Analyze a text description of a meal."""
    llm = get_llm_adapter()
    messages = [
        {"role": "system", "content": FOOD_PROMPT},
        {"role": "user", "content": f"Meal description: {description}"},
    ]
    raw = await llm.chat(messages, temperature=0.1)
    data = _parse_json(raw)
    return _build_response(data, patient_id, source="text-only", user_id=user_id)


def _get_pre_meal_glucose_for_user(user_id: str) -> float | None:
    """Try to fetch the latest CGM reading from a user's paired devices."""
    try:
        from app.adapters.storage import get_storage_adapter

        storage = get_storage_adapter()
        devices = storage.list_devices(user_id)
        cgm_devices = [d for d in devices if d["type"] == "cgm"]
        for cgm in cgm_devices:
            readings = storage.load_readings(cgm["id"], limit=1)
            if readings:
                return readings[-1].get("glucose_mg_dl")
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"Could not fetch user CGM for spike prediction: {exc}")
    return None


def _build_response(
    data: dict[str, Any],
    patient_id: str | None,
    source: str,
    user_id: str | None = None,
) -> FoodAnalysisResponse:
    items = [FoodItem.model_validate(it) for it in data.get("items", [])]
    total_dict = data.get("total") or {}
    total = NutritionTotal(
        calories=float(total_dict.get("calories", 0)),
        carbs_g=float(total_dict.get("carbs_g", 0)),
        protein_g=float(total_dict.get("protein_g", 0)),
        fat_g=float(total_dict.get("fat_g", 0)),
        fiber_g=float(total_dict.get("fiber_g", 0)),
    )

    meal = MealInput(
        carbs_g=total.carbs_g,
        protein_g=total.protein_g,
        fat_g=total.fat_g,
        fiber_g=total.fiber_g,
    )

    # If a user_id is provided, pull their latest CGM for personalized prediction
    pre_meal_glucose: float | None = None
    if user_id:
        pre_meal_glucose = _get_pre_meal_glucose_for_user(user_id)

    prediction = predict_meal_spike(
        patient_id=patient_id or "dubosson_1.0",
        meal=meal,
        pre_meal_glucose=pre_meal_glucose,
    )

    return FoodAnalysisResponse(
        items=items,
        total=total,
        glucose_prediction=prediction,
        source=source,
    )
