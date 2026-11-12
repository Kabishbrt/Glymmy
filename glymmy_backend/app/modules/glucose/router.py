"""Glucose FastAPI routes."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query

from app.modules.glucose.schemas import (
    GlucoseSeriesResponse,
    HypoCheckResponse,
    SpikePredictionRequest,
    SpikePredictionResponse,
)
from app.modules.glucose.service import (
    check_hypoglycemia,
    get_glucose_series,
    predict_meal_spike,
)

router = APIRouter(prefix="/api/v1/glucose", tags=["glucose"])


@router.get("/{patient_id}", response_model=GlucoseSeriesResponse)
def read_series(
    patient_id: str,
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int | None = Query(500),
) -> GlucoseSeriesResponse:
    """Return CGM time series + summary for a patient."""
    return get_glucose_series(patient_id, start=start, end=end, limit=limit)


@router.post("/predict", response_model=SpikePredictionResponse)
def predict(req: SpikePredictionRequest) -> SpikePredictionResponse:
    """Predict the glucose spike from a proposed meal."""
    return predict_meal_spike(
        patient_id=req.patient_id,
        meal=req.meal,
        pre_meal_glucose=req.pre_meal_glucose,
    )


@router.get("/{patient_id}/hypo-check", response_model=HypoCheckResponse)
def hypo_check(patient_id: str) -> HypoCheckResponse:
    """Nocturnal hypoglycemia check."""
    return check_hypoglycemia(patient_id)
