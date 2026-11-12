"""Profile + Patients routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.profile.schemas import (
    PatientListResponse,
    PatientProfile,
    QRCodeResponse,
)
from app.modules.profile.service import get_patient_qr, get_profile, list_patients

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


@router.get("", response_model=PatientListResponse)
def read_patients() -> PatientListResponse:
    """List every available patient across data adapters."""
    return list_patients()


@router.get("/{patient_id}/profile", response_model=PatientProfile)
def read_profile(patient_id: str) -> PatientProfile:
    return get_profile(patient_id)


@router.get("/{patient_id}/qr", response_model=QRCodeResponse)
def read_qr(patient_id: str) -> QRCodeResponse:
    return get_patient_qr(patient_id)
