"""Strawberry GraphQL types — thin wrappers over the Pydantic schemas.

We re-define types here (rather than auto-mapping from Pydantic) so the
GraphQL schema stays explicit and stable even if internal Pydantic
models evolve.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import strawberry


# ─── Patient ───
@strawberry.type
class Patient:
    id: str
    source: str
    name: str
    diagnosis: Optional[str] = None
    age: Optional[float] = None
    bmi: Optional[float] = None
    a1c: Optional[float] = None
    num_readings: Optional[int] = None
    num_lab_events: Optional[int] = None
    num_abnormal: Optional[int] = None
    dataset: Optional[str] = None


# ─── Glucose ───
@strawberry.type
class GlucoseReading:
    timestamp: datetime
    glucose_mg_dl: float
    heart_rate: Optional[float] = None
    activity: Optional[float] = None


@strawberry.type
class GlucoseSummary:
    count: int
    mean: float
    min: float
    max: float
    time_in_range_pct: float
    last_reading: Optional[float] = None
    last_reading_at: Optional[datetime] = None


@strawberry.type
class GlucoseSeries:
    patient_id: str
    summary: GlucoseSummary
    readings: list[GlucoseReading]


@strawberry.input
class MealInput:
    carbs_g: float
    protein_g: float = 0
    fat_g: float = 0
    fiber_g: float = 0


@strawberry.type
class SpikePrediction:
    predicted_spike_mg_dl: float
    net_carbs_g: float
    time_to_peak_min: int
    with_walk_spike_mg_dl: float
    risk: str
    explanation: str


@strawberry.type
class HypoCheck:
    patient_id: str
    hypo_events: int
    critical_events: int
    last_event: Optional[datetime] = None
    alert_level: str


# ─── Labs ───
@strawberry.type
class LabEvent:
    test: str
    value: Optional[float] = None
    unit: Optional[str] = None
    ref_low: Optional[float] = None
    ref_high: Optional[float] = None
    flag: str = "normal"
    charttime: Optional[datetime] = None
    category: Optional[str] = None


@strawberry.type
class AbnormalMarker:
    test: str
    value: float
    unit: Optional[str] = None
    normal_range: str
    status: str
    severity: str
    explanation: str
    actions: list[str]


@strawberry.type
class RiskAssessment:
    diabetes_risk: str
    cardiovascular_risk: str
    liver_risk: str
    kidney_risk: str


@strawberry.type
class LabInterpretation:
    patient_id: str
    summary: str
    abnormal_markers: list[AbnormalMarker]
    risk_assessment: RiskAssessment
    recommendations: list[str]
    follow_up: str


@strawberry.type
class LabEventList:
    patient_id: str
    events: list[LabEvent]
    total: int


# ─── Chat ───
@strawberry.type
class ChatSource:
    title: str
    source: str
    score: Optional[float] = None


@strawberry.type
class ChatResponse:
    response: str
    sources: list[ChatSource]
