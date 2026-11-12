"""Notification schemas for the AI alert / call system."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class NotificationType(str, Enum):
    hypo_critical = "hypo_critical"
    hypo_warning = "hypo_warning"
    hyper_critical = "hyper_critical"
    hyper_warning = "hyper_warning"
    prolonged_high = "prolonged_high"
    rapid_drop = "rapid_drop"


class Notification(BaseModel):
    id: str
    type: NotificationType
    severity: str  # critical | high | moderate
    title: str
    message: str  # LLM-generated personalized message
    voice_text: str  # TTS-friendly version
    glucose_mg_dl: float
    timestamp: str
    acknowledged: bool = False
    snoozed_until: str | None = None


class NotificationResponse(BaseModel):
    notifications: list[Notification]
    has_critical: bool
    user_name: str


class AcknowledgeRequest(BaseModel):
    action: str = "acknowledge"  # acknowledge | snooze
    snooze_minutes: int = 30
