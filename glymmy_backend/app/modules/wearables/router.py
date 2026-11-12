"""Wearables routes — extracts HR and activity from Dubosson CGM patients."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.adapters.cgm import get_cgm_adapter

router = APIRouter(prefix="/api/v1/wearables", tags=["wearables"])


@router.get("/{patient_id}")
def read_wearables(patient_id: str) -> dict:
    """Return unified wearable data (HR, activity, insulin) for a patient."""
    adapter = get_cgm_adapter()
    try:
        readings = adapter.get_readings(patient_id, limit=500)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    heart_rate = [
        {"timestamp": r["timestamp"], "bpm": r["heart_rate"]}
        for r in readings
        if "heart_rate" in r
    ]
    activity = [
        {"timestamp": r["timestamp"], "level": r["activity"]}
        for r in readings
        if "activity" in r
    ]
    insulin = [
        {
            "timestamp": r["timestamp"],
            "fast": r.get("fast_insulin", 0),
            "slow": r.get("slow_insulin", 0),
        }
        for r in readings
        if r.get("fast_insulin") or r.get("slow_insulin")
    ]
    return {
        "patient_id": patient_id,
        "heart_rate": heart_rate,
        "activity": activity,
        "insulin": insulin,
        "source": "GlucoBench/Dubosson (physiological sensors)",
    }
