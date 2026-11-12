"""Reminder routes: health check scheduling based on care guidelines."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.auth import AuthenticatedUser, get_current_user
from app.modules.reminders.schemas import DismissRequest, RemindersResponse
from app.modules.reminders.service import dismiss_reminder, get_reminders

router = APIRouter(prefix="/api/v1/users/me/reminders", tags=["reminders"])


@router.get("", response_model=RemindersResponse)
async def list_reminders(
    user: AuthenticatedUser = Depends(get_current_user),
) -> RemindersResponse:
    """Get pending health check reminders for the authenticated user.

    Returns personalized reminders based on diabetes care guidelines
    and the user's profile (diagnosis, A1C, etc.).
    """
    return get_reminders(user.internal_id)


@router.post("/{reminder_id}/dismiss")
async def dismiss_reminder_endpoint(
    reminder_id: str,
    req: DismissRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    """Dismiss or snooze a reminder.

    action: "dismiss" (hide permanently) or "snooze" (delay by snooze_days).
    """
    dismiss_reminder(
        user_id=user.internal_id,
        reminder_id=reminder_id,
        action=req.action,
        snooze_days=req.snooze_days,
    )
    return {"status": "ok", "action": req.action, "reminder_id": reminder_id}
