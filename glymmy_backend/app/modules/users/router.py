"""User management, device pairing, wearable data, and seed routes."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query

from app.adapters.storage import get_storage_adapter
from app.modules.users.schemas import (
    Device,
    DeviceCreate,
    DeviceReadingsResponse,
    SeedResponse,
    User,
    UserCreate,
    UserListResponse,
    UserWearablesResponse,
)
from app.modules.users.synthetic import seed_synthetic_data

router = APIRouter(prefix="/api/v1/users", tags=["users"])


# ── User CRUD ─────────────────────────────────────────────────────────────────


@router.get("", response_model=UserListResponse)
def list_users() -> UserListResponse:
    """List all registered users."""
    storage = get_storage_adapter()
    raw = storage.list_users()
    users = []
    for u in raw:
        devices = storage.list_devices(u["id"])
        users.append(User(
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
        ))
    return UserListResponse(users=users, total=len(users))


@router.post("", response_model=User, status_code=201)
def create_user(body: UserCreate) -> User:
    """Register a new user."""
    storage = get_storage_adapter()
    user_id = uuid4().hex[:12]
    now = datetime.now().isoformat()
    record = {"id": user_id, "created_at": now, "devices": [], **body.model_dump()}
    storage.save_user(record)
    return User(id=user_id, created_at=now, **body.model_dump())


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str) -> User:
    """Get user by ID with their paired devices."""
    storage = get_storage_adapter()
    u = storage.load_user(user_id)
    if not u:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    devices = storage.list_devices(user_id)
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


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str) -> None:
    """Delete a user and all their devices/data."""
    storage = get_storage_adapter()
    if not storage.delete_user(user_id):
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")


# ── Device management ─────────────────────────────────────────────────────────


@router.post("/{user_id}/devices", response_model=Device, status_code=201)
def pair_device(user_id: str, body: DeviceCreate) -> Device:
    """Pair a new device to a user."""
    storage = get_storage_adapter()
    u = storage.load_user(user_id)
    if not u:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    device_id = uuid4().hex[:12]
    now = datetime.now().isoformat()
    record = {
        "id": device_id,
        "user_id": user_id,
        "paired_at": now,
        **body.model_dump(),
    }
    # Serialize enums to strings for storage
    record["type"] = record["type"].value
    record["vendor"] = record["vendor"].value
    storage.save_device(record)
    return Device(**record)


@router.get("/{user_id}/devices", response_model=list[Device])
def list_devices(user_id: str) -> list[Device]:
    """List all devices paired to a user."""
    storage = get_storage_adapter()
    u = storage.load_user(user_id)
    if not u:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return [Device(**d) for d in storage.list_devices(user_id)]


# ── Wearable readings ────────────────────────────────────────────────────────


@router.get("/{user_id}/wearables", response_model=UserWearablesResponse)
def get_user_wearables(
    user_id: str,
    device_type: str | None = Query(None, description="Filter by device type"),
    limit: int = Query(200, ge=1, le=5000),
    start: str | None = Query(None, description="ISO start datetime"),
    end: str | None = Query(None, description="ISO end datetime"),
) -> UserWearablesResponse:
    """Get wearable readings for all (or filtered) devices of a user."""
    storage = get_storage_adapter()
    u = storage.load_user(user_id)
    if not u:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    devices = storage.list_devices(user_id)
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

    return UserWearablesResponse(user_id=user_id, devices=result)


@router.get("/{user_id}/wearables/{device_id}", response_model=DeviceReadingsResponse)
def get_device_readings(
    user_id: str,
    device_id: str,
    limit: int = Query(500, ge=1, le=10000),
    start: str | None = Query(None),
    end: str | None = Query(None),
) -> DeviceReadingsResponse:
    """Get readings for a specific device."""
    storage = get_storage_adapter()
    device = storage.load_device(device_id)
    if not device or device["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Device not found for this user")

    readings = storage.load_readings(device_id, start=start, end=end, limit=limit)
    return DeviceReadingsResponse(
        device=Device(**device),
        readings=readings,
        count=len(readings),
    )


# ── CGM shortcut (for food scanning integration) ─────────────────────────────


@router.get("/{user_id}/cgm/latest", response_model=dict)
def get_latest_cgm(user_id: str) -> dict:
    """Get the most recent CGM reading for a user (used by food scan for personalized spike prediction)."""
    storage = get_storage_adapter()
    u = storage.load_user(user_id)
    if not u:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    devices = storage.list_devices(user_id)
    cgm_devices = [d for d in devices if d["type"] == "cgm"]
    if not cgm_devices:
        raise HTTPException(status_code=404, detail="No CGM device paired for this user")

    for cgm in cgm_devices:
        readings = storage.load_readings(cgm["id"], limit=1)
        if readings:
            return {
                "user_id": user_id,
                "device_id": cgm["id"],
                "latest_reading": readings[-1],
            }

    raise HTTPException(status_code=404, detail="No CGM readings available")


# ── Seed ──────────────────────────────────────────────────────────────────────


@router.post("/seed", response_model=SeedResponse)
def seed_data(
    days: int = Query(7, ge=1, le=30, description="Days of historical data"),
) -> SeedResponse:
    """Populate the system with synthetic users, devices, and wearable data."""
    storage = get_storage_adapter()

    # Guard against double-seeding
    if storage.list_users():
        raise HTTPException(
            status_code=409,
            detail="Data already seeded. Delete users first or restart the server.",
        )

    counts = seed_synthetic_data(storage, days=days)
    return SeedResponse(
        users_created=counts["users_created"],
        devices_created=counts["devices_created"],
        readings_created=counts["readings_created"],
        message=f"Seeded {counts['users_created']} users with {counts['devices_created']} devices and {counts['readings_created']} readings ({days} days).",
    )
