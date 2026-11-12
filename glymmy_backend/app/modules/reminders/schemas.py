"""Reminder schemas for health check scheduling."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ReminderType(str, Enum):
    a1c_recheck = "a1c_recheck"
    lipid_panel = "lipid_panel"
    eye_exam = "eye_exam"
    foot_exam = "foot_exam"
    kidney_function = "kidney_function"
    blood_pressure = "blood_pressure"
    dental = "dental"
    general_checkup = "general_checkup"


class Reminder(BaseModel):
    id: str
    type: ReminderType
    title: str
    message: str  # personalized explanation
    priority: str  # high | medium | low
    due_context: str  # "3 months since last A1C", "recommended every 6 months"
    dismissed: bool = False
    snoozed_until: str | None = None


class RemindersResponse(BaseModel):
    reminders: list[Reminder]
    generated_at: str
    user_name: str


class DismissRequest(BaseModel):
    action: str = "dismiss"  # dismiss | snooze
    snooze_days: int = 7
