"""Patient and profile schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Patient(BaseModel):
    id: str
    source: str
    dataset: str | None = None
    name: str
    diagnosis: str | None = None
    age: float | None = None
    bmi: float | None = None
    a1c: float | None = None
    num_readings: int | None = None
    num_lab_events: int | None = None
    num_abnormal: int | None = None


class PatientListResponse(BaseModel):
    patients: list[Patient]
    total: int


class PatientProfile(BaseModel):
    patient: Patient
    glucose_summary: dict[str, Any] | None = None
    latest_labs: list[dict[str, Any]] | None = None
    abnormal_lab_count: int = 0


class QRCodeResponse(BaseModel):
    patient_id: str
    qr_data_url: str
    fhir_bundle: dict[str, Any]
