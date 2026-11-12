"""Synthetic wearable data generators.

Produces realistic time-series data for demo/hackathon purposes:
- CGM (Dexcom/Libre): glucose every 5 min with meals, dawn effect, exercise dips
- Smartwatch (Apple Watch): HR, SpO2, steps, sleep stages, skin temp
- Heart rate monitor (Garmin): continuous HR, HRV (RMSSD), RR intervals
- Activity tracker (Fitbit/Garmin): daily steps, distance, calories, active minutes
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from app.modules.users.schemas import DeviceType, DeviceVendor

# ── Helpers ───────────────────────────────────────────────────────────────────

_rng = random.Random(42)  # deterministic for reproducibility


def _jitter(base: float, pct: float = 0.05) -> float:
    """Add ± pct random noise."""
    return base * (1 + _rng.uniform(-pct, pct))


def _iso(dt: datetime) -> str:
    return dt.isoformat()


# ── User profiles for seeding ────────────────────────────────────────────────

SEED_USERS: list[dict[str, Any]] = [
    {
        "name": "Kabish Bhattarai",
        "email": "kabish@glymmy.dev",
        "age": 24,
        "weight_kg": 72.0,
        "height_cm": 175.0,
        "diagnosis": "Prediabetic",
        "a1c": 6.1,
        "health_inventory": {
            "blood_type": "O+",
            "medications": [
                {"name": "Metformin", "dosage": "500mg", "frequency": "Once daily", "prescriber": "Dr. Sarah Chen", "start_date": "2025-11-01", "notes": "Take with dinner"},
            ],
            "allergies": [
                {"allergen": "Penicillin", "reaction": "Hives and skin rash", "severity": "moderate"},
                {"allergen": "Shellfish", "reaction": "Throat swelling", "severity": "severe"},
            ],
            "conditions": [
                {"name": "Prediabetes", "diagnosed_date": "2025-10-15", "status": "active", "notes": "Monitoring with CGM"},
                {"name": "Mild Asthma", "diagnosed_date": "2020-03-01", "status": "managed", "notes": "Inhaler as needed"},
            ],
            "emergency_contacts": [
                {"name": "xxx", "relationship": "Father", "phone": "+977-9841000000", "email": "suman@example.com"},
            ],
            "insurance_provider": "Blue Cross Blue Shield",
            "insurance_id": "BCB-2026-XXXX",
            "primary_physician": "Dr. Sarah Chen",
            "notes": "Vegetarian diet. Exercises 4x/week.",
        },
    },
]

# Which devices each seed user gets
SEED_DEVICE_PROFILES: list[list[dict[str, Any]]] = [
    # Abinash — full suite: CGM + Apple Watch + Garmin HRM + Oura Ring
    [
        {"type": DeviceType.cgm, "vendor": DeviceVendor.dexcom, "model": "Dexcom G7"},
        {"type": DeviceType.smartwatch, "vendor": DeviceVendor.apple_watch, "model": "Apple Watch Ultra 2"},
        {"type": DeviceType.heart_rate_monitor, "vendor": DeviceVendor.garmin, "model": "Garmin HRM-Pro Plus"},
        {"type": DeviceType.activity_tracker, "vendor": DeviceVendor.oura, "model": "Oura Ring Gen 3"},
    ],
]


# ── CGM Generator ─────────────────────────────────────────────────────────────

def generate_cgm_readings(
    start: datetime,
    days: int = 7,
    baseline: float = 110.0,
    variability: float = 1.0,
) -> list[dict[str, Any]]:
    """Generate CGM readings every 5 minutes.

    Simulates:
    - Circadian rhythm (dawn effect: 04:00–08:00 rise)
    - Meal spikes (breakfast ~07:30, lunch ~12:30, dinner ~18:30)
    - Exercise dips (afternoon, ~16:00)
    - Random walk noise
    - Occasional hypo/hyper events
    """
    readings: list[dict[str, Any]] = []
    dt = start
    end = start + timedelta(days=days)
    glucose = baseline

    while dt < end:
        hour = dt.hour + dt.minute / 60.0

        # Dawn effect: gentle rise 04:00–08:00
        dawn = 8.0 * max(0, math.sin(math.pi * (hour - 4) / 4)) if 4 <= hour <= 8 else 0

        # Meal spikes (Gaussian bumps)
        meal_spike = 0.0
        for meal_hour, magnitude in [(7.5, 35), (12.5, 45), (18.5, 40)]:
            dist = abs(hour - meal_hour)
            if dist < 2.5:
                meal_spike += magnitude * math.exp(-0.5 * (dist / 0.7) ** 2) * variability

        # Exercise dip ~16:00
        exercise_dip = 0.0
        exercise_dist = abs(hour - 16.0)
        if exercise_dist < 1.5:
            exercise_dip = -15.0 * math.exp(-0.5 * (exercise_dist / 0.5) ** 2)

        # Random walk
        glucose += _rng.gauss(0, 1.5 * variability)

        # Mean-revert to baseline
        glucose += (baseline - glucose) * 0.02

        effective = glucose + dawn + meal_spike + exercise_dip

        # Clamp to physiological range
        effective = max(40.0, min(350.0, effective))

        # Trend
        if len(readings) >= 2:
            prev = readings[-1]["glucose_mg_dl"]
            delta = effective - prev
            if delta > 3:
                trend = "rising_fast" if delta > 8 else "rising"
            elif delta < -3:
                trend = "falling_fast" if delta < -8 else "falling"
            else:
                trend = "stable"
        else:
            trend = "stable"

        readings.append({
            "timestamp": _iso(dt),
            "glucose_mg_dl": round(effective, 1),
            "trend": trend,
        })

        dt += timedelta(minutes=5)

    return readings


# ── Smartwatch Generator ──────────────────────────────────────────────────────

def generate_smartwatch_readings(
    start: datetime,
    days: int = 7,
    resting_hr: int = 68,
) -> list[dict[str, Any]]:
    """Generate smartwatch readings every 10 minutes.

    Simulates:
    - Circadian HR pattern (low at night, peaks during day)
    - Sleep stages (22:00–06:00)
    - Activity-correlated HR spikes
    - SpO2 (96–99% normal, slight dip during sleep)
    - Step accumulation during waking hours
    - Skin temperature variation
    """
    readings: list[dict[str, Any]] = []
    dt = start
    end = start + timedelta(days=days)
    daily_steps = 0
    last_day = dt.day

    while dt < end:
        hour = dt.hour + dt.minute / 60.0

        # Reset daily step counter
        if dt.day != last_day:
            daily_steps = 0
            last_day = dt.day

        # Sleep detection
        is_sleeping = hour >= 22 or hour < 6
        sleep_stage = None
        if is_sleeping:
            cycle_pos = (hour if hour >= 22 else hour + 24) - 22
            cycle_phase = (cycle_pos % 1.5) / 1.5  # 90-min sleep cycles
            if cycle_phase < 0.05:
                sleep_stage = "awake"  # brief wakeup
            elif cycle_phase < 0.3:
                sleep_stage = "light"
            elif cycle_phase < 0.55:
                sleep_stage = "deep"
            elif cycle_phase < 0.8:
                sleep_stage = "rem"
            else:
                sleep_stage = "light"

        # Heart rate
        if is_sleeping:
            base_hr = resting_hr - 8 + (4 if sleep_stage == "rem" else 0)
        else:
            # Daytime: higher during activity hours
            activity_mod = 15 * math.sin(math.pi * (hour - 8) / 12) if 8 <= hour <= 20 else 0
            base_hr = resting_hr + activity_mod
            # Occasional exercise spike
            if 16 <= hour <= 17:
                base_hr += _rng.randint(20, 45)

        hr = max(45, min(190, int(_jitter(base_hr, 0.06))))

        # SpO2
        spo2_base = 96.5 if is_sleeping else 97.5
        spo2 = round(min(100.0, max(90.0, _jitter(spo2_base, 0.01))), 1)

        # Steps (only while awake)
        steps_this_interval = 0
        if not is_sleeping and 7 <= hour <= 21:
            if 16 <= hour <= 17:  # exercise hour
                steps_this_interval = _rng.randint(200, 500)
            elif 8 <= hour <= 9 or 12 <= hour <= 13:  # commute/walk
                steps_this_interval = _rng.randint(80, 200)
            else:
                steps_this_interval = _rng.randint(10, 80)
            daily_steps += steps_this_interval

        # Calories (rough: steps × 0.04 + BMR contribution per interval)
        bmr_per_10min = 1500 / 144  # ~10.4 cal per 10-min interval
        calories = round(bmr_per_10min + steps_this_interval * 0.04, 1)

        # Skin temp
        skin_temp = _jitter(36.2 if is_sleeping else 35.8, 0.01)

        readings.append({
            "timestamp": _iso(dt),
            "heart_rate_bpm": hr,
            "spo2_pct": spo2,
            "steps": daily_steps,
            "calories_burned": calories,
            "sleep_stage": sleep_stage,
            "skin_temp_c": round(skin_temp, 1),
        })

        dt += timedelta(minutes=10)

    return readings


# ── Heart Rate Monitor Generator ──────────────────────────────────────────────

def generate_hr_monitor_readings(
    start: datetime,
    days: int = 7,
    resting_hr: int = 65,
    base_hrv: float = 45.0,
) -> list[dict[str, Any]]:
    """Generate HR monitor readings every 1 minute (during active wear: 06:00–22:00).

    Simulates:
    - Continuous HR with circadian pattern
    - HRV (RMSSD) — higher at rest, lower during activity
    - RR intervals derived from HR
    - Exercise sessions with HR zones
    """
    readings: list[dict[str, Any]] = []
    dt = start
    end = start + timedelta(days=days)

    while dt < end:
        hour = dt.hour + dt.minute / 60.0

        # HR monitor typically worn 06:00–22:00
        if hour < 6 or hour >= 22:
            dt += timedelta(minutes=1)
            continue

        # Base HR with circadian variation
        circadian = 5 * math.sin(math.pi * (hour - 6) / 16)
        base_hr = resting_hr + circadian

        # Exercise windows
        is_exercise = False
        if 6.5 <= hour <= 7.5:  # morning run
            base_hr += 40 + 20 * math.sin(math.pi * (hour - 6.5))
            is_exercise = True
        elif 16 <= hour <= 17:  # afternoon workout
            phase = (hour - 16)
            if phase < 0.15:  # warmup
                base_hr += 20
            elif phase < 0.7:  # intervals
                base_hr += 50 + 15 * math.sin(phase * 10)
            else:  # cooldown
                base_hr += 25 * (1 - phase)
            is_exercise = True

        hr = max(45, min(200, int(_jitter(base_hr, 0.04))))

        # HRV — inversely related to HR intensity
        if is_exercise:
            hrv = max(8.0, base_hrv * 0.3 * _jitter(1.0, 0.15))
        else:
            hrv = base_hrv * _jitter(1.0, 0.12)

        # RR interval from HR (ms)
        rr = round(60000 / hr + _rng.gauss(0, 15), 1)

        readings.append({
            "timestamp": _iso(dt),
            "heart_rate_bpm": hr,
            "hrv_ms": round(hrv, 1),
            "rr_interval_ms": max(250, rr),
        })

        dt += timedelta(minutes=1)

    return readings


# ── Activity Tracker Generator ────────────────────────────────────────────────

def generate_activity_readings(
    start: datetime,
    days: int = 7,
    avg_daily_steps: int = 8500,
) -> list[dict[str, Any]]:
    """Generate hourly activity summaries.

    Simulates:
    - Step distribution weighted by time of day
    - Distance from steps (avg stride ~0.75m)
    - Calorie estimation
    - Active minutes (>100 steps in the hour)
    - Floors climbed
    """
    readings: list[dict[str, Any]] = []

    # Hourly step weight distribution (24 hours)
    weights = [
        0, 0, 0, 0, 0, 0,           # 00–05: sleeping
        0.02, 0.06, 0.08, 0.05,     # 06–09: wake up, commute
        0.04, 0.04, 0.07, 0.04,     # 10–13: work, lunch walk
        0.04, 0.04, 0.12, 0.08,     # 14–17: afternoon, exercise
        0.06, 0.05, 0.04, 0.02,     # 18–21: evening
        0.01, 0,                      # 22–23: winding down
    ]
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]

    for day in range(days):
        day_start = start + timedelta(days=day)
        day_target = int(_jitter(avg_daily_steps, 0.2))
        cumulative_steps = 0
        cumulative_cal = 0.0
        cumulative_dist = 0.0
        cumulative_active = 0
        cumulative_floors = 0

        for hour in range(24):
            dt = day_start.replace(hour=hour, minute=0, second=0, microsecond=0)
            steps = max(0, int(day_target * weights[hour] * _jitter(1.0, 0.3)))
            cumulative_steps += steps

            distance = steps * _jitter(0.75, 0.05)  # meters
            cumulative_dist += distance

            calories = steps * 0.04 + 62.5  # BMR per hour ≈ 62.5
            cumulative_cal += calories

            active_min = min(60, max(0, int(steps / 100 * _jitter(1.0, 0.2)))) if steps > 50 else 0
            cumulative_active += active_min

            floors = _rng.randint(0, 3) if steps > 500 else 0
            cumulative_floors += floors

            readings.append({
                "timestamp": _iso(dt),
                "steps": cumulative_steps,
                "distance_m": round(cumulative_dist, 1),
                "calories_burned": round(cumulative_cal, 1),
                "active_minutes": cumulative_active,
                "floors_climbed": cumulative_floors,
            })

    return readings


# ── Seed orchestrator ─────────────────────────────────────────────────────────

DEVICE_GENERATORS = {
    DeviceType.cgm: generate_cgm_readings,
    DeviceType.smartwatch: generate_smartwatch_readings,
    DeviceType.heart_rate_monitor: generate_hr_monitor_readings,
    DeviceType.activity_tracker: generate_activity_readings,
}

# Per-user baseline parameters keyed by diagnosis
DIAGNOSIS_PARAMS: dict[str, dict[str, Any]] = {
    "Type 2 Diabetes": {"baseline": 140.0, "variability": 1.4, "resting_hr": 75, "base_hrv": 35.0, "avg_daily_steps": 6000},
    "Type 1 Diabetes": {"baseline": 120.0, "variability": 1.6, "resting_hr": 68, "base_hrv": 40.0, "avg_daily_steps": 8000},
    "Prediabetic": {"baseline": 115.0, "variability": 1.1, "resting_hr": 70, "base_hrv": 42.0, "avg_daily_steps": 7500},
    "Healthy": {"baseline": 95.0, "variability": 0.7, "resting_hr": 62, "base_hrv": 55.0, "avg_daily_steps": 10000},
}


def seed_synthetic_data(
    storage: Any,
    days: int = 7,
    now: datetime | None = None,
) -> dict[str, int]:
    """Create seed users, pair devices, and generate readings.

    Returns counts of created entities.
    """
    from loguru import logger

    now = now or datetime.now()
    start = now - timedelta(days=days)

    total_users = 0
    total_devices = 0
    total_readings = 0

    for user_spec, device_specs in zip(SEED_USERS, SEED_DEVICE_PROFILES):
        user_id = uuid4().hex[:12]
        user_record = {
            "id": user_id,
            "created_at": _iso(now - timedelta(days=30)),
            "devices": [],
            **user_spec,
        }

        params = DIAGNOSIS_PARAMS.get(user_spec.get("diagnosis", ""), DIAGNOSIS_PARAMS["Healthy"])

        device_records = []
        for dev_spec in device_specs:
            device_id = uuid4().hex[:12]
            device_record = {
                "id": device_id,
                "user_id": user_id,
                "type": dev_spec["type"].value,
                "vendor": dev_spec["vendor"].value,
                "model": dev_spec.get("model"),
                "paired_at": _iso(now - timedelta(days=14)),
            }
            storage.save_device(device_record)
            device_records.append(device_record)

            # Generate readings
            gen_fn = DEVICE_GENERATORS[dev_spec["type"]]
            kwargs: dict[str, Any] = {"start": start, "days": days}

            if dev_spec["type"] == DeviceType.cgm:
                kwargs["baseline"] = params["baseline"]
                kwargs["variability"] = params["variability"]
            elif dev_spec["type"] == DeviceType.smartwatch:
                kwargs["resting_hr"] = params["resting_hr"]
            elif dev_spec["type"] == DeviceType.heart_rate_monitor:
                kwargs["resting_hr"] = params["resting_hr"]
                kwargs["base_hrv"] = params["base_hrv"]
            elif dev_spec["type"] == DeviceType.activity_tracker:
                kwargs["avg_daily_steps"] = params["avg_daily_steps"]

            readings = gen_fn(**kwargs)
            storage.save_readings(device_id, readings)
            total_readings += len(readings)
            total_devices += 1

            logger.info(
                f"  Device {dev_spec['type'].value}/{dev_spec['vendor'].value} "
                f"→ {len(readings)} readings"
            )

        user_record["devices"] = [d["id"] for d in device_records]
        storage.save_user(user_record)
        total_users += 1
        logger.info(f"Seeded user {user_spec['name']} ({user_id}) with {len(device_records)} devices")

    return {
        "users_created": total_users,
        "devices_created": total_devices,
        "readings_created": total_readings,
    }
