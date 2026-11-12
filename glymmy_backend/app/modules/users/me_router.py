"""Authenticated /users/me routes — namespace-scoped to the logged-in user.

Every route here uses `get_current_user` so data is always scoped to the
requesting user. No user can access another user's devices or readings.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from loguru import logger

from app.adapters.storage import get_storage_adapter
from app.core.auth import AuthenticatedUser, get_current_user
from app.modules.users.schemas import (
    Device,
    DeviceCreate,
    DeviceReadingsResponse,
    User,
    UserWearablesResponse,
)

router = APIRouter(prefix="/api/v1/users/me", tags=["me"])


# ── Profile ───────────────────────────────────────────────────────────────────


@router.get("", response_model=User)
def read_me(user: AuthenticatedUser = Depends(get_current_user)) -> User:
    """Get the authenticated user's profile + devices."""
    storage = get_storage_adapter()
    u = storage.load_user(user.internal_id)
    if not u:
        raise HTTPException(status_code=404, detail="User record not found")
    devices = storage.list_devices(user.internal_id)
    return User(
        id=u["id"],
        name=u["name"],
        email=u.get("email"),
        age=u.get("age"),
        weight_kg=u.get("weight_kg"),
        height_cm=u.get("height_cm"),
        diagnosis=u.get("diagnosis"),
        a1c=u.get("a1c"),
        created_at=u["created_at"],
        devices=[Device(**d) for d in devices],
    )


@router.patch("")
def update_me(
    body: dict,
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    """Update the authenticated user's profile fields."""
    storage = get_storage_adapter()
    u = storage.load_user(user.internal_id)
    if not u:
        raise HTTPException(status_code=404, detail="User record not found")

    allowed = {"name", "email", "age", "weight_kg", "height_cm", "diagnosis", "a1c"}
    for key, value in body.items():
        if key in allowed:
            u[key] = value
    storage.save_user(u)
    return {"status": "updated", "user_id": user.internal_id}


# ── Devices ───────────────────────────────────────────────────────────────────


@router.get("/devices", response_model=list[Device])
def list_my_devices(user: AuthenticatedUser = Depends(get_current_user)) -> list[Device]:
    """List all devices paired to the authenticated user."""
    storage = get_storage_adapter()
    return [Device(**d) for d in storage.list_devices(user.internal_id)]


@router.post("/devices", response_model=Device, status_code=201)
def pair_my_device(
    body: DeviceCreate,
    user: AuthenticatedUser = Depends(get_current_user),
) -> Device:
    """Pair a new device to the authenticated user."""
    storage = get_storage_adapter()
    device_id = uuid4().hex[:12]
    now = datetime.now().isoformat()
    record = {
        "id": device_id,
        "user_id": user.internal_id,
        "paired_at": now,
        "type": body.type.value,
        "vendor": body.vendor.value,
        "model": body.model,
    }
    storage.save_device(record)
    return Device(**record)


# ── Wearable readings (query) ────────────────────────────────────────────────


@router.get("/wearables", response_model=UserWearablesResponse)
def get_my_wearables(
    device_type: str | None = Query(None, description="Filter by device type"),
    limit: int = Query(200, ge=1, le=5000),
    start: str | None = Query(None, description="ISO start datetime"),
    end: str | None = Query(None, description="ISO end datetime"),
    user: AuthenticatedUser = Depends(get_current_user),
) -> UserWearablesResponse:
    """Get wearable readings for the authenticated user's devices."""
    storage = get_storage_adapter()
    devices = storage.list_devices(user.internal_id)
    if device_type:
        devices = [d for d in devices if d["type"] == device_type]

    result: list[DeviceReadingsResponse] = []
    for d in devices:
        readings = storage.load_readings(d["id"], start=start, end=end, limit=limit)
        result.append(DeviceReadingsResponse(
            device=Device(**d),
            readings=readings,
            count=len(readings),
        ))
    return UserWearablesResponse(user_id=user.internal_id, devices=result)


@router.get("/wearables/{device_id}", response_model=DeviceReadingsResponse)
def get_my_device_readings(
    device_id: str,
    limit: int = Query(500, ge=1, le=10000),
    start: str | None = Query(None),
    end: str | None = Query(None),
    user: AuthenticatedUser = Depends(get_current_user),
) -> DeviceReadingsResponse:
    """Get readings for a specific device owned by the authenticated user."""
    storage = get_storage_adapter()
    device = storage.load_device(device_id)
    if not device or device["user_id"] != user.internal_id:
        raise HTTPException(status_code=404, detail="Device not found")
    readings = storage.load_readings(device_id, start=start, end=end, limit=limit)
    return DeviceReadingsResponse(
        device=Device(**device),
        readings=readings,
        count=len(readings),
    )


# ── Wearable readings (ingest from mobile) ───────────────────────────────────


@router.post("/devices/{device_id}/readings", status_code=201)
def ingest_readings(
    device_id: str,
    body: list[dict],
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    """Ingest wearable readings from a mobile device (HealthKit, Garmin SDK, etc).

    The mobile app periodically syncs readings by POSTing a batch here.
    Each reading must have at least a `timestamp` field.
    """
    storage = get_storage_adapter()
    device = storage.load_device(device_id)
    if not device or device["user_id"] != user.internal_id:
        raise HTTPException(status_code=404, detail="Device not found")

    # Validate timestamps exist
    for r in body:
        if "timestamp" not in r:
            raise HTTPException(status_code=422, detail="Each reading must have a 'timestamp'")

    count = storage.save_readings(device_id, body)
    return {"status": "ok", "device_id": device_id, "readings_ingested": count}


# ── CGM shortcut ──────────────────────────────────────────────────────────────


@router.get("/cgm/latest")
def get_my_latest_cgm(
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    """Get the authenticated user's latest CGM reading."""
    storage = get_storage_adapter()
    devices = storage.list_devices(user.internal_id)
    cgm_devices = [d for d in devices if d["type"] == "cgm"]
    if not cgm_devices:
        raise HTTPException(status_code=404, detail="No CGM device paired")

    for cgm in cgm_devices:
        readings = storage.load_readings(cgm["id"], limit=1)
        if readings:
            return {
                "user_id": user.internal_id,
                "device_id": cgm["id"],
                "latest_reading": readings[-1],
            }

    raise HTTPException(status_code=404, detail="No CGM readings available")


# ── Real-time SSE alert stream ────────────────────────────────────────────────

HYPO_THRESHOLD = 70.0
HYPO_CRITICAL = 55.0
HYPER_THRESHOLD = 250.0
HYPER_WARNING = 180.0


@router.get("/alerts/stream")
async def alert_stream(
    user: AuthenticatedUser = Depends(get_current_user),
) -> StreamingResponse:
    """Server-Sent Events stream for real-time glucose alerts.

    The mobile/web app connects to this endpoint and receives push alerts
    whenever the user's CGM reading crosses a threshold:
    - hypo_warning: glucose < 70 mg/dL
    - hypo_critical: glucose < 55 mg/dL
    - hyper_warning: glucose > 180 mg/dL
    - hyper_critical: glucose > 250 mg/dL

    Also sends periodic heartbeats and the latest reading every 30s.
    """

    async def event_generator():
        storage = get_storage_adapter()
        last_alert_ts: str | None = None

        while True:
            try:
                devices = storage.list_devices(user.internal_id)
                cgm_devices = [d for d in devices if d["type"] == "cgm"]

                for cgm in cgm_devices:
                    readings = storage.load_readings(cgm["id"], limit=1)
                    if not readings:
                        continue

                    latest = readings[-1]
                    ts = latest["timestamp"]
                    glucose = latest.get("glucose_mg_dl", 0)
                    trend = latest.get("trend", "unknown")

                    # Send the latest reading
                    reading_event = {
                        "type": "reading",
                        "timestamp": ts,
                        "glucose_mg_dl": glucose,
                        "trend": trend,
                        "device_id": cgm["id"],
                    }
                    yield f"event: reading\ndata: {json.dumps(reading_event)}\n\n"

                    # Check thresholds and emit alerts (only for new readings)
                    if ts != last_alert_ts:
                        alert = None
                        if glucose < HYPO_CRITICAL:
                            alert = {
                                "type": "hypo_critical",
                                "severity": "critical",
                                "message": f"CRITICAL: Glucose at {glucose} mg/dL — seek help immediately",
                                "glucose_mg_dl": glucose,
                                "timestamp": ts,
                            }
                        elif glucose < HYPO_THRESHOLD:
                            alert = {
                                "type": "hypo_warning",
                                "severity": "high",
                                "message": f"Low glucose: {glucose} mg/dL — consume fast-acting carbs",
                                "glucose_mg_dl": glucose,
                                "timestamp": ts,
                            }
                        elif glucose > HYPER_THRESHOLD:
                            alert = {
                                "type": "hyper_critical",
                                "severity": "critical",
                                "message": f"Very high glucose: {glucose} mg/dL — check insulin and hydrate",
                                "glucose_mg_dl": glucose,
                                "timestamp": ts,
                            }
                        elif glucose > HYPER_WARNING:
                            alert = {
                                "type": "hyper_warning",
                                "severity": "moderate",
                                "message": f"Elevated glucose: {glucose} mg/dL — consider a walk",
                                "glucose_mg_dl": glucose,
                                "timestamp": ts,
                            }

                        if alert:
                            yield f"event: alert\ndata: {json.dumps(alert)}\n\n"

                        last_alert_ts = ts

                # Heartbeat
                yield f"event: heartbeat\ndata: {json.dumps({'time': datetime.now().isoformat()})}\n\n"

            except Exception as exc:  # noqa: BLE001
                logger.error(f"Alert stream error: {exc}")
                yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

            await asyncio.sleep(30)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
