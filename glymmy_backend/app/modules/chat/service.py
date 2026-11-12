"""Chat service: combines patient context + RAG retrieval + LLM response."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timedelta

from loguru import logger

from app.adapters.llm import get_llm_adapter
from app.core.exceptions import PatientNotFoundError
from app.modules.chat.schemas import ChatMessage, ChatSource
from app.modules.profile.service import get_profile
from app.rag import get_rag_pipeline


# ── Context builders ─────────────────────────────────────────────────────────


def _build_patient_context(patient_id: str | None) -> str:
    """Build context from GlucoBench/MIMIC dataset patients."""
    if not patient_id:
        return ""
    try:
        profile = get_profile(patient_id)
    except PatientNotFoundError:
        return ""

    lines = [f"Patient: {profile.patient.name}"]
    if profile.patient.diagnosis:
        lines.append(f"Diagnosis: {profile.patient.diagnosis}")
    if profile.patient.age is not None:
        lines.append(f"Age: {profile.patient.age}")
    if profile.patient.bmi is not None:
        lines.append(f"BMI: {profile.patient.bmi}")
    if profile.patient.a1c is not None:
        lines.append(f"A1C: {profile.patient.a1c}%")
    if profile.glucose_summary:
        s = profile.glucose_summary
        lines.append(
            f"Glucose summary: mean {s.get('mean')} mg/dL, "
            f"time-in-range {s.get('time_in_range_pct')}%"
        )
    if profile.latest_labs:
        abnormal = [
            lab for lab in profile.latest_labs if lab.get("flag") == "abnormal"
        ][:5]
        if abnormal:
            lines.append("Recent abnormal labs:")
            for lab in abnormal:
                lines.append(
                    f"  - {lab.get('test')}: {lab.get('value')} {lab.get('unit', '')}"
                )
    return "\n".join(lines)


def _build_user_context(user_id: str) -> str:
    """Build rich context from the demo user's synthetic wearable data."""
    from app.adapters.storage import get_storage_adapter

    storage = get_storage_adapter()
    user = storage.load_user(user_id)
    if not user:
        return ""

    lines = [f"Patient: {user.get('name', 'Unknown')}"]
    if user.get("diagnosis"):
        lines.append(f"Diagnosis: {user['diagnosis']}")
    if user.get("a1c"):
        lines.append(f"A1C: {user['a1c']}%")
    if user.get("age"):
        lines.append(f"Age: {user['age']}")
    if user.get("weight_kg") and user.get("height_cm"):
        bmi = user["weight_kg"] / (user["height_cm"] / 100) ** 2
        lines.append(f"Weight: {user['weight_kg']}kg | Height: {user['height_cm']}cm | BMI: {bmi:.1f}")

    devices = storage.list_devices(user_id)

    # ── CGM data ─────────────────────────────────────────────────────────
    cgm_devices = [d for d in devices if d["type"] == "cgm"]
    for cgm in cgm_devices:
        readings = storage.load_readings(cgm["id"], limit=288)  # ~24h of 5-min data
        if not readings:
            continue

        glucose_values = [r["glucose_mg_dl"] for r in readings if r.get("glucose_mg_dl")]
        if not glucose_values:
            continue

        current = glucose_values[-1]
        trend = readings[-1].get("trend", "stable")

        # 1h trend (last 12 readings)
        recent_12 = glucose_values[-12:] if len(glucose_values) >= 12 else glucose_values
        avg_1h = sum(recent_12) / len(recent_12)

        # 4h average (last 48 readings)
        recent_48 = glucose_values[-48:] if len(glucose_values) >= 48 else glucose_values
        avg_4h = sum(recent_48) / len(recent_48)

        # 24h stats
        mean_24h = sum(glucose_values) / len(glucose_values)
        min_24h = min(glucose_values)
        max_24h = max(glucose_values)
        in_range = sum(1 for g in glucose_values if 70 <= g <= 180)
        tir_pct = (in_range / len(glucose_values)) * 100

        lines.append("")
        lines.append(f"Current Glucose: {current:.0f} mg/dL ({trend})")
        lines.append(f"Last 1h average: {avg_1h:.0f} mg/dL")
        lines.append(f"Last 4h average: {avg_4h:.0f} mg/dL")
        lines.append(f"Last 24h: min {min_24h:.0f}, max {max_24h:.0f}, mean {mean_24h:.0f} mg/dL")
        lines.append(f"Time in range (70-180): {tir_pct:.0f}%")
        break  # use first CGM device

    # ── Smartwatch data ──────────────────────────────────────────────────
    watch_devices = [d for d in devices if d["type"] == "smartwatch"]
    for watch in watch_devices:
        readings = storage.load_readings(watch["id"], limit=6)  # last hour
        if not readings:
            continue
        latest = readings[-1]
        parts = []
        if latest.get("heart_rate_bpm"):
            parts.append(f"HR: {latest['heart_rate_bpm']} bpm")
        if latest.get("spo2_pct"):
            parts.append(f"SpO2: {latest['spo2_pct']}%")
        if latest.get("steps"):
            parts.append(f"Steps: {latest['steps']}")
        if latest.get("skin_temp_c"):
            parts.append(f"Skin temp: {latest['skin_temp_c']}°C")
        if latest.get("sleep_stage") and latest["sleep_stage"] != "awake":
            parts.append(f"Sleep: {latest['sleep_stage']}")
        if parts:
            lines.append("")
            lines.append("Smartwatch: " + " | ".join(parts))

        # Aggregate daily steps from all readings today
        all_steps = [r.get("steps", 0) for r in readings if r.get("steps")]
        if all_steps:
            lines.append(f"Recent steps (last hour): {sum(all_steps)}")
        break

    # ── Heart rate monitor ───────────────────────────────────────────────
    hr_devices = [d for d in devices if d["type"] == "heart_rate_monitor"]
    for hrm in hr_devices:
        readings = storage.load_readings(hrm["id"], limit=5)
        if not readings:
            continue
        latest = readings[-1]
        parts = []
        if latest.get("heart_rate_bpm"):
            parts.append(f"HR: {latest['heart_rate_bpm']} bpm")
        if latest.get("hrv_rmssd_ms"):
            parts.append(f"HRV: {latest['hrv_rmssd_ms']:.0f}ms")
        if parts:
            lines.append("Heart Rate Monitor: " + " | ".join(parts))
        break

    # ── Activity tracker ─────────────────────────────────────────────────
    activity_devices = [d for d in devices if d["type"] == "activity_tracker"]
    for tracker in activity_devices:
        readings = storage.load_readings(tracker["id"], limit=1)
        if not readings:
            continue
        latest = readings[-1]
        parts = []
        if latest.get("steps"):
            parts.append(f"Steps: {latest['steps']}")
        if latest.get("distance_km"):
            parts.append(f"Distance: {latest['distance_km']:.1f}km")
        if latest.get("calories_burned"):
            parts.append(f"Calories: {latest['calories_burned']:.0f}")
        if latest.get("active_minutes"):
            parts.append(f"Active: {latest['active_minutes']}min")
        if parts:
            lines.append("Activity: " + " | ".join(parts))
        break

    return "\n".join(lines)


# ── Message assembly ─────────────────────────────────────────────────────────


def _build_messages(
    patient_id: str | None,
    user_message: str,
    history: list[ChatMessage],
    user_id: str | None = None,
) -> tuple[list[dict[str, str]], list[ChatSource]]:
    rag = get_rag_pipeline()
    retrieved = rag.retrieve(user_message, top_k=3)
    sources = [
        ChatSource(
            title=r["metadata"].get("title", "Unknown"),
            source=r["metadata"].get("source", ""),
            score=r.get("score"),
        )
        for r in retrieved
    ]

    context_blocks: list[str] = []

    # Prefer user_id (demo user with wearable data) over patient_id (dataset)
    if user_id:
        user_ctx = _build_user_context(user_id)
        if user_ctx:
            context_blocks.append(f"=== PATIENT CONTEXT ===\n{user_ctx}")
    else:
        patient_ctx = _build_patient_context(patient_id)
        if patient_ctx:
            context_blocks.append(f"=== PATIENT CONTEXT ===\n{patient_ctx}")

    if retrieved:
        kb = "\n\n".join(
            f"[{r['metadata'].get('title', 'Document')}]\n{r['content']}"
            for r in retrieved
        )
        context_blocks.append(f"=== MEDICAL KNOWLEDGE ===\n{kb}")

    system = (
        "You are Glymmy, a friendly AI health assistant. "
        "Use the patient context and medical knowledge below to give "
        "personalized, clear, and safe answers. Reference the patient's "
        "actual data (glucose readings, heart rate, activity) when relevant. "
        "Always include a brief reminder to consult a doctor for medical decisions.\n\n"
        + "\n\n".join(context_blocks)
    )

    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    for h in history[-10:]:  # keep last 10 turns
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": user_message})

    logger.debug(f"Chat messages prepared | patient={patient_id} user={user_id} sources={len(sources)}")
    return messages, sources


# ── Public API ───────────────────────────────────────────────────────────────


async def chat(
    patient_id: str | None,
    user_message: str,
    history: list[ChatMessage],
    user_id: str | None = None,
) -> tuple[str, list[ChatSource]]:
    # If no client-side history provided, load from storage
    if not history and user_id:
        history = get_chat_history_as_messages(user_id, limit=10)

    messages, sources = _build_messages(patient_id, user_message, history, user_id=user_id)
    llm = get_llm_adapter()
    response = await llm.chat(messages, temperature=0.3)

    # Persist both messages
    if user_id:
        _save_message(user_id, "user", user_message)
        _save_message(user_id, "assistant", response)

    return response, sources


def _save_message(user_id: str, role: str, content: str) -> None:
    from app.adapters.storage import get_storage_adapter

    storage = get_storage_adapter()
    storage.save_chat_message(user_id, {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    })


def get_chat_history_as_messages(user_id: str, limit: int = 20) -> list[ChatMessage]:
    """Load persisted chat history for a user."""
    from app.adapters.storage import get_storage_adapter

    storage = get_storage_adapter()
    raw = storage.load_chat_history(user_id)
    messages = [ChatMessage(role=m["role"], content=m["content"]) for m in raw]
    return messages[-limit:]


def get_chat_history_raw(user_id: str) -> list[dict]:
    """Load raw chat history dicts (with timestamps)."""
    from app.adapters.storage import get_storage_adapter

    storage = get_storage_adapter()
    return storage.load_chat_history(user_id)


def clear_chat_history(user_id: str) -> None:
    """Clear all chat history for a user."""
    from app.adapters.storage import get_storage_adapter

    storage = get_storage_adapter()
    # The memory adapter stores chats in _chats dict keyed by patient_id
    storage._chats.pop(user_id, None)


async def chat_stream(
    patient_id: str | None,
    user_message: str,
    history: list[ChatMessage],
    user_id: str | None = None,
) -> AsyncIterator[str]:
    messages, _ = _build_messages(patient_id, user_message, history, user_id=user_id)
    llm = get_llm_adapter()
    async for token in llm.chat_stream(messages, temperature=0.3):
        yield token
