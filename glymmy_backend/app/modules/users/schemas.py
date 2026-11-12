"""User, device, and wearable-reading schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ── Device types ──────────────────────────────────────────────────────────────

class DeviceType(str, Enum):
    cgm = "cgm"
    smartwatch = "smartwatch"
    heart_rate_monitor = "heart_rate_monitor"
    activity_tracker = "activity_tracker"


class DeviceVendor(str, Enum):
    dexcom = "dexcom"
    libre = "libre"
    apple_watch = "apple_watch"
    garmin = "garmin"
    fitbit = "fitbit"
    oura = "oura"
    whoop = "whoop"


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: str | None = None
    age: int | None = None
    weight_kg: float | None = None
    height_cm: float | None = None
    diagnosis: str | None = None  # e.g. "Type 2 Diabetes", "Prediabetic"
    a1c: float | None = None


class User(UserCreate):
    id: str
    created_at: datetime
    devices: list[Device] = []


class UserListResponse(BaseModel):
    users: list[User]
    total: int


# ── Device ────────────────────────────────────────────────────────────────────

class DeviceCreate(BaseModel):
    type: DeviceType
    vendor: DeviceVendor
    model: str | None = None  # e.g. "Dexcom G7", "Apple Watch Ultra 2"


class Device(DeviceCreate):
    id: str
    user_id: str
    paired_at: datetime


# ── Readings (per device type) ────────────────────────────────────────────────

class CGMReading(BaseModel):
    timestamp: datetime
    glucose_mg_dl: float
    trend: str | None = None  # rising, falling, stable, rising_fast, falling_fast


class SmartwatchReading(BaseModel):
    timestamp: datetime
    heart_rate_bpm: int | None = None
    spo2_pct: float | None = None
    steps: int | None = None
    calories_burned: float | None = None
    sleep_stage: str | None = None  # awake, light, deep, rem
    skin_temp_c: float | None = None


class HeartRateMonitorReading(BaseModel):
    timestamp: datetime
    heart_rate_bpm: int
    hrv_ms: float | None = None  # heart rate variability (RMSSD)
    rr_interval_ms: float | None = None  # beat-to-beat interval


class ActivityTrackerReading(BaseModel):
    timestamp: datetime
    steps: int = 0
    distance_m: float = 0.0
    calories_burned: float = 0.0
    active_minutes: int = 0
    floors_climbed: int = 0


# ── Unified response ─────────────────────────────────────────────────────────

class DeviceReadingsResponse(BaseModel):
    device: Device
    readings: list[
        CGMReading | SmartwatchReading | HeartRateMonitorReading | ActivityTrackerReading
    ]
    count: int


class UserWearablesResponse(BaseModel):
    user_id: str
    devices: list[DeviceReadingsResponse]


# ── For the seed endpoint ─────────────────────────────────────────────────────

class SeedResponse(BaseModel):
    users_created: int
    devices_created: int
    readings_created: int
    message: str


# Forward ref update
User.model_rebuild()
