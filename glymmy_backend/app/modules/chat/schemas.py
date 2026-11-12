"""Chat schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # user | assistant | system
    content: str


class ChatRequest(BaseModel):
    patient_id: str | None = None
    user_id: str | None = None  # internal storage user ID (demo user)
    message: str
    history: list[ChatMessage] = []


class ChatSource(BaseModel):
    title: str
    source: str
    score: float | None = None


class ChatResponse(BaseModel):
    response: str
    sources: list[ChatSource]


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessage]
    total: int
