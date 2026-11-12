"""Profile module — lists patients across adapters, builds unified profiles,
and produces FHIR bundles + QR codes for doctor sharing.
"""

from __future__ import annotations

import base64
import io
import json
from typing import Any

import qrcode
from loguru import logger

from app.adapters.cgm import get_cgm_adapter
from app.adapters.labs import get_labs_adapter
from app.core.exceptions import PatientNotFoundError
from app.modules.glucose.service import get_glucose_series
from app.modules.labs.service import get_lab_events
from app.modules.profile.schemas import (
    Patient,
    PatientListResponse,
    PatientProfile,
    QRCodeResponse,
)


def list_patients() -> PatientListResponse:
    """Combine patients from every data adapter into one list."""
    patients: list[Patient] = []
    try:
        cgm = get_cgm_adapter()
        for p in cgm.list_patients():
            patients.append(Patient.model_validate(p))
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"CGM adapter list_patients failed: {exc}")

    try:
        labs = get_labs_adapter()
        for p in labs.list_patients():
            patients.append(Patient.model_validate(p))
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Labs adapter list_patients failed: {exc}")

    return PatientListResponse(patients=patients, total=len(patients))


def get_profile(patient_id: str) -> PatientProfile:
    """Build a unified profile for a single patient."""
    all_patients = list_patients().patients
    match = next((p for p in all_patients if p.id == patient_id), None)
    if match is None:
        raise PatientNotFoundError(f"No such patient: {patient_id}")

    glucose_summary: dict[str, Any] | None = None
    latest_labs: list[dict[str, Any]] | None = None
    abnormal_count = 0

    if patient_id.startswith(("dubosson_", "hall_")):
        try:
            series = get_glucose_series(patient_id, limit=500)
            glucose_summary = series.summary.model_dump()
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"No glucose series for {patient_id}: {exc}")

    if patient_id.startswith("mimic_"):
        try:
            events = get_lab_events(patient_id, limit=30)
            latest_labs = [e.model_dump() for e in events.events]
            abnormal_count = sum(1 for e in events.events if e.flag == "abnormal")
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"No lab events for {patient_id}: {exc}")

    return PatientProfile(
        patient=match,
        glucose_summary=glucose_summary,
        latest_labs=latest_labs,
        abnormal_lab_count=abnormal_count,
    )


def _build_fhir_bundle(profile: PatientProfile) -> dict[str, Any]:
    entries: list[dict[str, Any]] = [
        {
            "resource": {
                "resourceType": "Patient",
                "id": profile.patient.id,
                "name": [{"text": profile.patient.name}],
                "extension": [
                    {"url": "diagnosis", "valueString": profile.patient.diagnosis or ""},
                ],
            }
        }
    ]
    if profile.glucose_summary:
        entries.append(
            {
                "resource": {
                    "resourceType": "Observation",
                    "code": {"text": "CGM Summary"},
                    "subject": {"reference": f"Patient/{profile.patient.id}"},
                    "valueCodeableConcept": {"text": json.dumps(profile.glucose_summary)},
                }
            }
        )
    if profile.latest_labs:
        for lab in profile.latest_labs[:5]:
            entries.append(
                {
                    "resource": {
                        "resourceType": "Observation",
                        "code": {"text": lab.get("test", "")},
                        "subject": {"reference": f"Patient/{profile.patient.id}"},
                        "valueQuantity": {
                            "value": lab.get("value"),
                            "unit": lab.get("unit", ""),
                        },
                        "interpretation": [{"text": lab.get("flag", "")}],
                    }
                }
            )
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": entries,
    }


def get_patient_qr(patient_id: str) -> QRCodeResponse:
    """Create a FHIR bundle + QR-code data URL for doctor sharing."""
    profile = get_profile(patient_id)
    bundle = _build_fhir_bundle(profile)
    # QR payload is kept small — just a summary + identifier
    payload = json.dumps(
        {
            "patient_id": profile.patient.id,
            "name": profile.patient.name,
            "diagnosis": profile.patient.diagnosis,
            "glucose_mean": (profile.glucose_summary or {}).get("mean"),
            "abnormal_lab_count": profile.abnormal_lab_count,
        }
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    data_url = f"data:image/png;base64,{b64}"

    return QRCodeResponse(
        patient_id=profile.patient.id,
        qr_data_url=data_url,
        fhir_bundle=bundle,
    )
