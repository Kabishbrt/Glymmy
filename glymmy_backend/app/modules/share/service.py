"""Share service — generate QR codes and shareable links."""

from __future__ import annotations

import base64
import io
from datetime import datetime
from typing import Any

import qrcode
from loguru import logger

from app.adapters.storage import get_storage_adapter
from app.modules.share.schemas import ShareConfig, ShareResponse, SharedData
from app.modules.share.store import create_share, get_share


def create_share_link(user_id: str, config: ShareConfig, base_url: str) -> ShareResponse:
    """Create a share token, generate QR, return the response."""
    token = create_share(user_id, config.model_dump())
    share_url = f"{base_url.rstrip('/')}/share/{token}"

    # Generate QR code
    qr = qrcode.make(share_url)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    qr_data_url = f"data:image/png;base64,{qr_b64}"

    return ShareResponse(
        share_token=token,
        share_url=share_url,
        qr_data_url=qr_data_url,
        created_at=datetime.now().isoformat(),
    )


def get_shared_data(token: str) -> SharedData | None:
    """Look up a share token and build the shared data view."""
    share = get_share(token)
    if not share:
        return None

    user_id = share["user_id"]
    config = share["config"]
    storage = get_storage_adapter()
    user = storage.load_user(user_id)
    if not user:
        return None

    data = SharedData(
        user_name=user.get("name", "Unknown"),
        shared_at=share["created_at"],
    )

    if config.get("include_profile"):
        inv = user.get("health_inventory", {})
        data.profile = {
            "age": user.get("age"),
            "diagnosis": user.get("diagnosis"),
            "a1c": user.get("a1c"),
            "blood_type": inv.get("blood_type"),
        }

    if config.get("include_glucose"):
        devices = storage.list_devices(user_id)
        cgm_devices = [d for d in devices if d["type"] == "cgm"]
        for cgm in cgm_devices:
            readings = storage.load_readings(cgm["id"], limit=288)
            if readings:
                values = [r["glucose_mg_dl"] for r in readings if r.get("glucose_mg_dl")]
                if values:
                    data.glucose_summary = {
                        "current": values[-1],
                        "mean": round(sum(values) / len(values)),
                        "min": round(min(values)),
                        "max": round(max(values)),
                        "readings_count": len(values),
                    }
            break

    if config.get("include_vitals"):
        devices = storage.list_devices(user_id)
        watch_devices = [d for d in devices if d["type"] == "smartwatch"]
        for watch in watch_devices:
            readings = storage.load_readings(watch["id"], limit=1)
            if readings:
                latest = readings[-1]
                data.vitals = {
                    "heart_rate_bpm": latest.get("heart_rate_bpm"),
                    "spo2_pct": latest.get("spo2_pct"),
                    "steps": latest.get("steps"),
                }
            break

    if config.get("include_medications"):
        inv = user.get("health_inventory", {})
        data.medications = inv.get("medications", [])

    if config.get("include_conditions"):
        inv = user.get("health_inventory", {})
        data.conditions = inv.get("conditions", [])

    return data
