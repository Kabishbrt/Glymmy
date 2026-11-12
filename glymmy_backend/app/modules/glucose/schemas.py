"""Pydantic schemas for the glucose module."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class GlucoseReading(BaseModel):
    timestamp: datetime
    glucose_mg_dl: float
    heart_rate: float | None = None
    activity: float | None = None
    fast_insulin: float | None = None
    slow_insulin: float | None = None
    calories: float | None = None


class GlucoseSummary(BaseModel):
    count: int
    mean: float
    min: float
    max: float
    time_in_range_pct: float
    last_reading: float | None = None
    last_reading_at: datetime | None = None


class GlucoseSeriesResponse(BaseModel):
    patient_id: str
    summary: GlucoseSummary
    readings: list[GlucoseReading]


class MealInput(BaseModel):
    carbs_g: float = Field(..., ge=0)
    protein_g: float = Field(0, ge=0)
    fat_g: float = Field(0, ge=0)
    fiber_g: float = Field(0, ge=0)


class SpikePredictionRequest(BaseModel):
    patient_id: str
    meal: MealInput
    pre_meal_glucose: float | None = None


class SpikePredictionResponse(BaseModel):
    predicted_spike_mg_dl: float
    net_carbs_g: float
    time_to_peak_min: int
    with_walk_spike_mg_dl: float
    risk: str  # low | moderate | high
    explanation: str


class HypoCheckResponse(BaseModel):
    patient_id: str
    hypo_events: int
    critical_events: int
    last_event: datetime | None
    alert_level: str  # none | low | high | critical
