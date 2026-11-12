"""Pydantic schemas for the labs module."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LabEvent(BaseModel):
    test: str
    category: str | None = None
    value: float | None = None
    raw_value: str | None = None
    unit: str | None = None
    ref_low: float | None = None
    ref_high: float | None = None
    flag: str
    charttime: datetime | None = None


class AbnormalMarker(BaseModel):
    test: str
    value: float
    unit: str | None
    normal_range: str
    status: str  # LOW | HIGH | CRITICAL LOW | CRITICAL HIGH
    severity: str  # mild | moderate | severe
    explanation: str
    actions: list[str]


class RiskAssessment(BaseModel):
    diabetes_risk: str
    cardiovascular_risk: str
    liver_risk: str
    kidney_risk: str


class LabInterpretation(BaseModel):
    patient_id: str
    summary: str
    abnormal_markers: list[AbnormalMarker]
    risk_assessment: RiskAssessment
    recommendations: list[str]
    follow_up: str


class LabEventsResponse(BaseModel):
    patient_id: str
    events: list[LabEvent]
    total: int
