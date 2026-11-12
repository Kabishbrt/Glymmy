"""Notification routes: AI-triggered glucose alerts with voice messages."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.auth import AuthenticatedUser, get_current_user
from app.modules.notifications.schemas import AcknowledgeRequest, NotificationResponse
from app.modules.notifications.service import (
    acknowledge_notification,
    get_pending_notifications,
)

router = APIRouter(prefix="/api/v1/users/me/notifications", tags=["notifications"])


@router.get("", response_model=NotificationResponse)
async def list_notifications(
    user: AuthenticatedUser = Depends(get_current_user),
) -> NotificationResponse:
    """Get pending notifications for the authenticated user.

    Returns glucose alerts with personalized messages and voice text.
    The mobile app can use `voice_text` for TTS and display `message` as a card.
    """
    return get_pending_notifications(user.internal_id)


@router.post("/{notification_id}/acknowledge")
async def ack_notification(
    notification_id: str,
    req: AcknowledgeRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    """Acknowledge or snooze a notification.

    action: "acknowledge" (dismiss permanently) or "snooze" (delay by snooze_minutes).
    """
    acknowledge_notification(
        user_id=user.internal_id,
        notification_id=notification_id,
        action=req.action,
        snooze_minutes=req.snooze_minutes,
    )
    return {"status": "ok", "action": req.action, "notification_id": notification_id}


@router.get("/stream")
async def notification_stream(
    user: AuthenticatedUser = Depends(get_current_user),
) -> StreamingResponse:
    """SSE stream of notifications. Polls every 15 seconds."""

    async def event_generator():
        while True:
            try:
                result = get_pending_notifications(user.internal_id)
                if result.notifications:
                    for notif in result.notifications:
                        payload = json.dumps(notif.model_dump(), default=str)
                        yield f"event: notification\ndata: {payload}\n\n"
                else:
                    yield f"event: heartbeat\ndata: {{\"time\": \"{datetime.now().isoformat()}\"}}\n\n"
            except Exception as exc:
                yield f"event: error\ndata: {{\"error\": \"{exc}\"}}\n\n"

            await asyncio.sleep(15)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
