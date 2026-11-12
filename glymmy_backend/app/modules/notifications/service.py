"""Notification service: glucose alert detection + LLM-powered messages.

Pull-based system — the mobile app polls for pending notifications.
State (ack/snooze) is in-memory (resets on server restart).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from typing import Any

from loguru import logger

from app.adapters.storage import get_storage_adapter
from app.modules.notifications.schemas import (
    Notification,
    NotificationResponse,
    NotificationType,
)

# ── Thresholds ───────────────────────────────────────────────────────────────

HYPO_CRITICAL = 55.0
HYPO_THRESHOLD = 70.0
HYPER_THRESHOLD = 250.0
HYPER_WARNING = 180.0

# ── In-memory state ──────────────────────────────────────────────────────────
# Key: notification_id → {"acknowledged": bool, "snoozed_until": datetime | None}
_notification_state: dict[str, dict[str, Any]] = {}


def _make_id(user_id: str, ntype: str, timestamp: str) -> str:
    """Deterministic ID so the same alert doesn't create duplicates."""
    raw = f"{user_id}:{ntype}:{timestamp[:16]}"  # bucket to 1-min resolution
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _is_snoozed(notification_id: str) -> bool:
    state = _notification_state.get(notification_id)
    if not state:
        return False
    if state.get("acknowledged"):
        return True
    snoozed_until = state.get("snoozed_until")
    if snoozed_until and datetime.now() < snoozed_until:
        return True
    return False


# ── Alert detection ──────────────────────────────────────────────────────────


def _detect_alerts(user_id: str) -> list[dict[str, Any]]:
    """Analyze recent CGM readings and return raw alert dicts."""
    storage = get_storage_adapter()
    devices = storage.list_devices(user_id)
    cgm_devices = [d for d in devices if d["type"] == "cgm"]

    alerts: list[dict[str, Any]] = []

    for cgm in cgm_devices:
        readings = storage.load_readings(cgm["id"], limit=288)  # ~24h
        if not readings:
            continue

        latest = readings[-1]
        glucose = latest.get("glucose_mg_dl", 0)
        ts = latest.get("timestamp", datetime.now().isoformat())

        # Threshold alerts on latest reading
        if glucose < HYPO_CRITICAL:
            alerts.append({
                "type": NotificationType.hypo_critical,
                "severity": "critical",
                "glucose": glucose,
                "timestamp": ts,
                "detail": "dangerously low",
            })
        elif glucose < HYPO_THRESHOLD:
            alerts.append({
                "type": NotificationType.hypo_warning,
                "severity": "high",
                "glucose": glucose,
                "timestamp": ts,
                "detail": "low",
            })
        elif glucose > HYPER_THRESHOLD:
            alerts.append({
                "type": NotificationType.hyper_critical,
                "severity": "critical",
                "glucose": glucose,
                "timestamp": ts,
                "detail": "critically high",
            })
        elif glucose > HYPER_WARNING:
            alerts.append({
                "type": NotificationType.hyper_warning,
                "severity": "moderate",
                "glucose": glucose,
                "timestamp": ts,
                "detail": "elevated",
            })

        # Prolonged high: glucose > 180 for 2+ hours (24 five-min readings)
        if len(readings) >= 24:
            recent_2h = readings[-24:]
            all_high = all(
                r.get("glucose_mg_dl", 0) > HYPER_WARNING for r in recent_2h
            )
            if all_high:
                avg = sum(r["glucose_mg_dl"] for r in recent_2h) / len(recent_2h)
                alerts.append({
                    "type": NotificationType.prolonged_high,
                    "severity": "high",
                    "glucose": avg,
                    "timestamp": ts,
                    "detail": f"glucose above 180 for over 2 hours (avg {avg:.0f})",
                })

        # Rapid drop: > 30 mg/dL in 30 minutes (6 five-min readings)
        if len(readings) >= 6:
            recent_6 = readings[-6:]
            drop = recent_6[0].get("glucose_mg_dl", 0) - recent_6[-1].get("glucose_mg_dl", 0)
            if drop > 30:
                alerts.append({
                    "type": NotificationType.rapid_drop,
                    "severity": "high",
                    "glucose": glucose,
                    "timestamp": ts,
                    "detail": f"dropped {drop:.0f} mg/dL in 30 minutes",
                })

        break  # use first CGM device

    return alerts


# ── Message generation ───────────────────────────────────────────────────────

# Pre-built templates (no LLM call needed — fast and reliable for hackathon)
_MESSAGE_TEMPLATES: dict[str, dict[str, str]] = {
    "hypo_critical": {
        "title": "Urgent: Dangerously Low Glucose",
        "message": "Your glucose has dropped to {glucose:.0f} mg/dL — this is dangerously low. Please consume 15-20g of fast-acting carbs immediately (glucose tablets, juice, or regular soda). Recheck in 15 minutes.",
        "voice": "Hey {name}, this is urgent. Your glucose is at {glucose:.0f}, which is dangerously low. Please eat or drink something with fast-acting sugar right now. Juice, glucose tablets, or regular soda. Then recheck in 15 minutes. Do you need help?",
    },
    "hypo_warning": {
        "title": "Low Glucose Alert",
        "message": "Your glucose is at {glucose:.0f} mg/dL, which is below the target range. Consider having a small snack with 15g of carbs to bring it back up.",
        "voice": "Hey {name}, your glucose is at {glucose:.0f}, which is a bit low. A small snack should help — maybe some crackers or a piece of fruit. Keep an eye on it over the next 15 minutes.",
    },
    "hyper_critical": {
        "title": "Very High Glucose Alert",
        "message": "Your glucose has reached {glucose:.0f} mg/dL — well above target. Check your insulin, drink water, and avoid additional carbs. If this persists, contact your care team.",
        "voice": "Hey {name}, your glucose is at {glucose:.0f}, which is very high. Please check your insulin, drink plenty of water, and skip any carbs for now. If it doesn't come down in the next hour, please reach out to your doctor.",
    },
    "hyper_warning": {
        "title": "Elevated Glucose",
        "message": "Your glucose is at {glucose:.0f} mg/dL, above the 180 target. A 15-minute walk can help bring it down. Stay hydrated.",
        "voice": "Hey {name}, your glucose is at {glucose:.0f}, a bit elevated. A short walk — even 10 to 15 minutes — can really help bring it down. And make sure you're drinking enough water.",
    },
    "prolonged_high": {
        "title": "Glucose Elevated for 2+ Hours",
        "message": "Your glucose has been above 180 mg/dL for over 2 hours (avg {glucose:.0f}). This sustained elevation deserves attention — consider exercise, hydration, or reviewing your medication timing.",
        "voice": "Hey {name}, your glucose has been running high for over two hours now, averaging around {glucose:.0f}. This is worth paying attention to. A walk, some extra water, or checking your medication timing could help.",
    },
    "rapid_drop": {
        "title": "Rapid Glucose Drop Detected",
        "message": "Your glucose is dropping fast — currently at {glucose:.0f} mg/dL ({detail}). Keep a snack handy in case it continues to fall.",
        "voice": "Hey {name}, heads up — your glucose is dropping quickly. It's at {glucose:.0f} right now and has {detail}. Keep a snack nearby just in case it keeps going down.",
    },
}


def _generate_notification(
    alert: dict[str, Any], user_id: str, user_name: str
) -> Notification | None:
    """Build a Notification from a raw alert dict."""
    ntype = alert["type"]
    nid = _make_id(user_id, ntype.value, alert["timestamp"])

    if _is_snoozed(nid):
        return None

    template = _MESSAGE_TEMPLATES.get(ntype.value, _MESSAGE_TEMPLATES["hyper_warning"])
    fmt = {"glucose": alert["glucose"], "name": user_name, "detail": alert.get("detail", "")}

    return Notification(
        id=nid,
        type=ntype,
        severity=alert["severity"],
        title=template["title"],
        message=template["message"].format(**fmt),
        voice_text=template["voice"].format(**fmt),
        glucose_mg_dl=alert["glucose"],
        timestamp=alert["timestamp"],
    )


# ── Public API ───────────────────────────────────────────────────────────────


def get_pending_notifications(user_id: str) -> NotificationResponse:
    """Check glucose alerts and return pending notifications."""
    storage = get_storage_adapter()
    user = storage.load_user(user_id)
    user_name = user.get("name", "there").split()[0] if user else "there"

    alerts = _detect_alerts(user_id)
    notifications = []
    for alert in alerts:
        notif = _generate_notification(alert, user_id, user_name)
        if notif:
            notifications.append(notif)

    has_critical = any(n.severity == "critical" for n in notifications)

    return NotificationResponse(
        notifications=notifications,
        has_critical=has_critical,
        user_name=user_name,
    )


def acknowledge_notification(
    user_id: str, notification_id: str, action: str, snooze_minutes: int = 30
) -> bool:
    """Acknowledge or snooze a notification."""
    if action == "snooze":
        _notification_state[notification_id] = {
            "acknowledged": False,
            "snoozed_until": datetime.now() + timedelta(minutes=snooze_minutes),
        }
        logger.info(f"Notification {notification_id} snoozed for {snooze_minutes}min")
    else:
        _notification_state[notification_id] = {
            "acknowledged": True,
            "snoozed_until": None,
        }
        logger.info(f"Notification {notification_id} acknowledged")
    return True
