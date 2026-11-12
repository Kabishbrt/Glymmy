"""Chat routes including SSE streaming, user-aware /me variants, and history."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.auth import AuthenticatedUser, get_current_user
from app.modules.chat.schemas import ChatHistoryResponse, ChatMessage, ChatRequest, ChatResponse
from app.modules.chat.service import (
    chat,
    chat_stream,
    clear_chat_history,
    get_chat_history_raw,
)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest) -> ChatResponse:
    response, sources = await chat(
        patient_id=req.patient_id,
        user_message=req.message,
        history=req.history,
        user_id=req.user_id,
    )
    return ChatResponse(response=response, sources=sources)


@router.post("/stream")
async def chat_stream_endpoint(req: ChatRequest) -> StreamingResponse:
    async def event_generator():
        async for token in chat_stream(
            patient_id=req.patient_id,
            user_message=req.message,
            history=req.history,
            user_id=req.user_id,
        ):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── /chat/me — auto-resolves the authenticated (demo) user ──────────────────


@router.post("/me", response_model=ChatResponse)
async def chat_me_endpoint(
    req: ChatRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> ChatResponse:
    """Chat with Glymmy using the authenticated user's wearable data."""
    response, sources = await chat(
        patient_id=None,
        user_message=req.message,
        history=req.history,
        user_id=user.internal_id,
    )
    return ChatResponse(response=response, sources=sources)


@router.post("/me/stream")
async def chat_me_stream_endpoint(
    req: ChatRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> StreamingResponse:
    """Streaming chat using the authenticated user's wearable data."""
    async def event_generator():
        async for token in chat_stream(
            patient_id=None,
            user_message=req.message,
            history=req.history,
            user_id=user.internal_id,
        ):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/me/history", response_model=ChatHistoryResponse)
async def get_history(
    user: AuthenticatedUser = Depends(get_current_user),
) -> ChatHistoryResponse:
    """Load persisted chat history for the authenticated user."""
    raw = get_chat_history_raw(user.internal_id)
    messages = [ChatMessage(role=m["role"], content=m["content"]) for m in raw]
    return ChatHistoryResponse(messages=messages, total=len(messages))


@router.delete("/me/history")
async def delete_history(
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    """Clear all chat history for the authenticated user."""
    clear_chat_history(user.internal_id)
    return {"status": "cleared"}
