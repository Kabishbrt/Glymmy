"""Glucose module business logic.

Contains:
- CGM series retrieval + summary stats (time-in-range, mean, last reading)
- Meal → spike prediction using a physiological model
- Nocturnal hypoglycemia detection
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

from loguru import logger

from app.adapters.cgm import get_cgm_adapter
from app.modules.glucose.schemas import (
    GlucoseReading,
    GlucoseSeriesResponse,
    GlucoseSummary,
    HypoCheckResponse,
    MealInput,
    SpikePredictionResponse,
)

# Clinical thresholds
HYPO_THRESHOLD = 70.0
HYPO_CRITICAL = 55.0
HYPER_THRESHOLD = 180.0
TIR_LOW = 70.0
TIR_HIGH = 180.0


def _summarize(readings: list[dict[str, Any]]) -> GlucoseSummary:
    if not readings:
        return GlucoseSummary(
            count=0, mean=0.0, min=0.0, max=0.0, time_in_range_pct=0.0
        )
    values = [r["glucose_mg_dl"] for r in readings]
    in_range = sum(1 for v in values if TIR_LOW <= v <= TIR_HIGH)
    last = readings[-1]
    return GlucoseSummary(
        count=len(values),
        mean=round(sum(values) / len(values), 1),
        min=round(min(values), 1),
        max=round(max(values), 1),
        time_in_range_pct=round(100 * in_range / len(values), 1),
        last_reading=last["glucose_mg_dl"],
        last_reading_at=last["timestamp"],
    )


def get_glucose_series(
    patient_id: str,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int | None = 500,
) -> GlucoseSeriesResponse:
    """Return glucose readings + summary for a patient."""
    adapter = get_cgm_adapter()
    raw = adapter.get_readings(patient_id, start=start, end=end, limit=limit)
    readings = [GlucoseReading.model_validate(r) for r in raw]
    return GlucoseSeriesResponse(
        patient_id=patient_id,
        summary=_summarize(raw),
        readings=readings,
    )


def predict_meal_spike(
    patient_id: str,
    meal: MealInput,
    pre_meal_glucose: float | None = None,
    carb_sensitivity: float = 0.55,
) -> SpikePredictionResponse:
    """Predict the glucose spike from a meal using a physiological model.

    Formula: net_carbs × carb_sensitivity × fat_damping × protein_damping
    - Fiber reduces net carbs.
    - Fat and protein slow absorption, reducing peak magnitude.
    - Higher pre-meal glucose slightly amplifies the spike.
    """
    net_carbs = max(0.0, meal.carbs_g - meal.fiber_g)
    fat_factor = max(0.70, 1 - meal.fat_g * 0.005)
    protein_factor = max(0.80, 1 - meal.protein_g * 0.003)
    base = net_carbs * carb_sensitivity * fat_factor * protein_factor

    # Slight modulation by pre-meal glucose (higher start → slightly higher spike)
    if pre_meal_glucose is None:
        try:
            adapter = get_cgm_adapter()
            recent = adapter.get_readings(patient_id, limit=1)
            if recent:
                pre_meal_glucose = recent[-1]["glucose_mg_dl"]
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"Could not fetch pre-meal glucose: {exc}")

    if pre_meal_glucose is not None and pre_meal_glucose > 130:
        base *= 1.10

    spike = round(base, 1)
    risk = "high" if spike > 40 else "moderate" if spike > 25 else "low"
    with_walk = round(spike * 0.75, 1)

    explanation = (
        f"{net_carbs:.0f}g net carbs × {carb_sensitivity:.2f} sensitivity, "
        f"damped by fat/protein absorption (×{fat_factor * protein_factor:.2f}). "
        f"A 15-min post-meal walk can cut the peak by ~25%."
    )

    return SpikePredictionResponse(
        predicted_spike_mg_dl=spike,
        net_carbs_g=round(net_carbs, 1),
        time_to_peak_min=75,
        with_walk_spike_mg_dl=with_walk,
        risk=risk,
        explanation=explanation,
    )


def check_hypoglycemia(patient_id: str, limit: int = 1000) -> HypoCheckResponse:
    """Scan recent readings for hypo events (esp. nocturnal 22:00–06:00)."""
    adapter = get_cgm_adapter()
    readings = adapter.get_readings(patient_id, limit=limit)

    hypo_events = 0
    critical_events = 0
    last_event: datetime | None = None

    for r in readings:
        glucose = r["glucose_mg_dl"]
        ts = datetime.fromisoformat(r["timestamp"])
        if glucose < HYPO_THRESHOLD:
            hypo_events += 1
            last_event = ts
            if glucose < HYPO_CRITICAL:
                # Nocturnal critical is worse
                is_night = ts.time() >= time(22, 0) or ts.time() <= time(6, 0)
                critical_events += 2 if is_night else 1

    if critical_events >= 3:
        alert = "critical"
    elif critical_events >= 1:
        alert = "high"
    elif hypo_events >= 1:
        alert = "low"
    else:
        alert = "none"

    return HypoCheckResponse(
        patient_id=patient_id,
        hypo_events=hypo_events,
        critical_events=critical_events,
        last_event=last_event,
        alert_level=alert,
    )
