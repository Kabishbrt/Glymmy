"""Reminder service: rule-based health check reminders.

Generates smart reminders based on diabetes care guidelines and the
user's profile. "Last done" dates are simulated for the demo.
State (dismiss/snooze) is in-memory.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from typing import Any

from loguru import logger

from app.adapters.storage import get_storage_adapter
from app.modules.reminders.schemas import (
    Reminder,
    ReminderType,
    RemindersResponse,
)

# ── In-memory state ──────────────────────────────────────────────────────────
# Key: reminder_id → {"dismissed": bool, "snoozed_until": datetime | None}
_reminder_state: dict[str, dict[str, Any]] = {}


def _make_id(user_id: str, rtype: str) -> str:
    raw = f"{user_id}:{rtype}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _is_hidden(reminder_id: str) -> bool:
    state = _reminder_state.get(reminder_id)
    if not state:
        return False
    if state.get("dismissed"):
        return True
    snoozed_until = state.get("snoozed_until")
    if snoozed_until and datetime.now() < snoozed_until:
        return True
    return False


# ── Reminder rules ───────────────────────────────────────────────────────────

# Each rule: type, condition function, frequency description, message template
# For the demo, we simulate "last done" dates relative to today.

RULES: list[dict[str, Any]] = [
    {
        "type": ReminderType.a1c_recheck,
        "title": "A1C Recheck Due",
        "applies_to": ["Type 1 Diabetes", "Type 2 Diabetes", "Prediabetic"],
        "check": lambda user, now: _a1c_check(user, now),
    },
    {
        "type": ReminderType.lipid_panel,
        "title": "Lipid Panel Due",
        "applies_to": ["Type 1 Diabetes", "Type 2 Diabetes", "Prediabetic"],
        "check": lambda user, now: _periodic_check(
            "lipid panel", 180, "every 6 months for diabetic patients", "medium"
        ),
    },
    {
        "type": ReminderType.eye_exam,
        "title": "Annual Eye Exam Due",
        "applies_to": ["Type 1 Diabetes", "Type 2 Diabetes"],
        "check": lambda user, now: _periodic_check(
            "dilated eye exam", 330, "annually to screen for diabetic retinopathy", "medium"
        ),
    },
    {
        "type": ReminderType.foot_exam,
        "title": "Foot Exam Due",
        "applies_to": ["Type 1 Diabetes", "Type 2 Diabetes"],
        "check": lambda user, now: _periodic_check(
            "comprehensive foot exam", 350, "annually to check for neuropathy", "low"
        ),
    },
    {
        "type": ReminderType.kidney_function,
        "title": "Kidney Function Test Due",
        "applies_to": ["Type 1 Diabetes", "Type 2 Diabetes"],
        "check": lambda user, now: _periodic_check(
            "kidney function test (eGFR + urine albumin)", 350,
            "annually — diabetes is the leading cause of kidney disease", "medium"
        ),
    },
    {
        "type": ReminderType.blood_pressure,
        "title": "Blood Pressure Check Due",
        "applies_to": ["Type 1 Diabetes", "Type 2 Diabetes", "Prediabetic"],
        "check": lambda user, now: _periodic_check(
            "blood pressure check", 85, "every 3 months for diabetic patients", "low"
        ),
    },
    {
        "type": ReminderType.dental,
        "title": "Dental Checkup Due",
        "applies_to": ["Type 1 Diabetes", "Type 2 Diabetes"],
        "check": lambda user, now: _periodic_check(
            "dental checkup", 170,
            "every 6 months — high glucose increases gum disease risk", "low"
        ),
    },
    {
        "type": ReminderType.general_checkup,
        "title": "General Health Checkup",
        "applies_to": None,  # applies to everyone
        "check": lambda user, now: _periodic_check(
            "general health checkup", 350, "annually for overall health screening", "low"
        ),
    },
]


def _a1c_check(user: dict, now: datetime) -> dict | None:
    """A1C recheck: every 3 months if >7.0, every 6 months if controlled."""
    a1c = user.get("a1c")
    if not a1c:
        return None

    if a1c > 7.0:
        days_since = 95  # simulate: last done ~3 months ago
        return {
            "priority": "high",
            "due_context": f"Your A1C was {a1c}% — recheck recommended every 3 months when above 7.0",
            "message": (
                f"Your last A1C was {a1c}%, which is above the 7.0% target. "
                f"It's been about {days_since} days since your last check. "
                "Regular monitoring helps track whether your management plan is working. "
                "Schedule an A1C test with your doctor soon."
            ),
        }
    else:
        days_since = 185  # simulate: last done ~6 months ago
        return {
            "priority": "medium",
            "due_context": f"Your A1C was {a1c}% (well controlled) — recheck every 6 months",
            "message": (
                f"Great job keeping your A1C at {a1c}%! "
                f"It's been about {days_since} days since your last check. "
                "Even with good control, regular monitoring every 6 months is recommended."
            ),
        }


def _periodic_check(
    test_name: str, days_since: int, guideline: str, priority: str
) -> dict:
    """Generic periodic check template."""
    return {
        "priority": priority,
        "due_context": f"Recommended {guideline} — ~{days_since} days since last {test_name}",
        "message": (
            f"It's been about {days_since} days since your last {test_name}. "
            f"Guidelines recommend this {guideline}. "
            "Consider scheduling this with your healthcare provider."
        ),
    }


# ── Public API ───────────────────────────────────────────────────────────────


def get_reminders(user_id: str) -> RemindersResponse:
    """Evaluate all reminder rules for the user and return pending reminders."""
    storage = get_storage_adapter()
    user = storage.load_user(user_id)
    if not user:
        return RemindersResponse(
            reminders=[], generated_at=datetime.now().isoformat(), user_name="Unknown"
        )

    user_name = user.get("name", "Unknown")
    diagnosis = user.get("diagnosis", "")
    now = datetime.now()
    reminders: list[Reminder] = []

    for rule in RULES:
        # Check if rule applies to this user's diagnosis
        applies_to = rule["applies_to"]
        if applies_to and not any(d in diagnosis for d in applies_to):
            continue

        rid = _make_id(user_id, rule["type"].value)
        if _is_hidden(rid):
            continue

        result = rule["check"](user, now)
        if not result:
            continue

        reminders.append(Reminder(
            id=rid,
            type=rule["type"],
            title=rule["title"],
            message=result["message"],
            priority=result["priority"],
            due_context=result["due_context"],
        ))

    # Sort: high priority first
    priority_order = {"high": 0, "medium": 1, "low": 2}
    reminders.sort(key=lambda r: priority_order.get(r.priority, 3))

    return RemindersResponse(
        reminders=reminders,
        generated_at=now.isoformat(),
        user_name=user_name,
    )


def dismiss_reminder(
    user_id: str, reminder_id: str, action: str, snooze_days: int = 7
) -> bool:
    """Dismiss or snooze a reminder."""
    if action == "snooze":
        _reminder_state[reminder_id] = {
            "dismissed": False,
            "snoozed_until": datetime.now() + timedelta(days=snooze_days),
        }
        logger.info(f"Reminder {reminder_id} snoozed for {snooze_days} days")
    else:
        _reminder_state[reminder_id] = {
            "dismissed": True,
            "snoozed_until": None,
        }
        logger.info(f"Reminder {reminder_id} dismissed")
    return True
