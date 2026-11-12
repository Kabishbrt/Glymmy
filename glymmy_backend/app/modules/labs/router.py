"""Labs FastAPI routes."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.modules.labs.schemas import LabEventsResponse, LabInterpretation
from app.modules.labs.service import get_lab_events, interpret_labs

router = APIRouter(prefix="/api/v1/labs", tags=["labs"])


@router.get("/{patient_id}", response_model=LabEventsResponse)
def read_events(patient_id: str, limit: int = Query(200, ge=1, le=2000)) -> LabEventsResponse:
    return get_lab_events(patient_id, limit=limit)


@router.post("/{patient_id}/interpret", response_model=LabInterpretation)
def interpret(patient_id: str, limit: int = Query(50, ge=1, le=500)) -> LabInterpretation:
    return interpret_labs(patient_id, limit=limit)
