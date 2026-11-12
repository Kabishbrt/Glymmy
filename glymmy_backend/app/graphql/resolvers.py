"""GraphQL resolvers — they call the same service.py functions used by REST.

This is the whole point of the protocol-agnostic service layer: REST and
GraphQL share business logic, validation, and side effects. Maintaining
both costs nothing extra at the service level.
"""

from __future__ import annotations

from typing import Optional

from app.graphql.types import (
    AbnormalMarker,
    ChatResponse,
    ChatSource,
    GlucoseReading,
    GlucoseSeries,
    GlucoseSummary,
    HypoCheck,
    LabEvent,
    LabEventList,
    LabInterpretation,
    MealInput,
    Patient,
    RiskAssessment,
    SpikePrediction,
)
from app.modules.chat.service import chat as chat_service
from app.modules.glucose.schemas import MealInput as PydanticMealInput
from app.modules.glucose.service import (
    check_hypoglycemia,
    get_glucose_series,
    predict_meal_spike,
)
from app.modules.labs.service import get_lab_events, interpret_labs
from app.modules.profile.service import get_profile, list_patients


# ─── Patients ───
async def resolve_patients() -> list[Patient]:
    res = list_patients()
    return [
        Patient(
            id=p.id,
            source=p.source,
            name=p.name,
            diagnosis=p.diagnosis,
            age=p.age,
            bmi=p.bmi,
            a1c=p.a1c,
            num_readings=p.num_readings,
            num_lab_events=p.num_lab_events,
            num_abnormal=p.num_abnormal,
            dataset=p.dataset,
        )
        for p in res.patients
    ]


async def resolve_patient(patient_id: str) -> Optional[Patient]:
    try:
        profile = get_profile(patient_id)
    except Exception:
        return None
    p = profile.patient
    return Patient(
        id=p.id,
        source=p.source,
        name=p.name,
        diagnosis=p.diagnosis,
        age=p.age,
        bmi=p.bmi,
        a1c=p.a1c,
        num_readings=p.num_readings,
        num_lab_events=p.num_lab_events,
        num_abnormal=p.num_abnormal,
        dataset=p.dataset,
    )


# ─── Glucose ───
async def resolve_glucose_series(patient_id: str, limit: int = 500) -> GlucoseSeries:
    res = get_glucose_series(patient_id, limit=limit)
    return GlucoseSeries(
        patient_id=res.patient_id,
        summary=GlucoseSummary(
            count=res.summary.count,
            mean=res.summary.mean,
            min=res.summary.min,
            max=res.summary.max,
            time_in_range_pct=res.summary.time_in_range_pct,
            last_reading=res.summary.last_reading,
            last_reading_at=res.summary.last_reading_at,
        ),
        readings=[
            GlucoseReading(
                timestamp=r.timestamp,
                glucose_mg_dl=r.glucose_mg_dl,
                heart_rate=r.heart_rate,
                activity=r.activity,
            )
            for r in res.readings
        ],
    )


async def resolve_predict_spike(
    patient_id: str,
    meal: MealInput,
    pre_meal_glucose: Optional[float] = None,
) -> SpikePrediction:
    res = predict_meal_spike(
        patient_id=patient_id,
        meal=PydanticMealInput(
            carbs_g=meal.carbs_g,
            protein_g=meal.protein_g,
            fat_g=meal.fat_g,
            fiber_g=meal.fiber_g,
        ),
        pre_meal_glucose=pre_meal_glucose,
    )
    return SpikePrediction(
        predicted_spike_mg_dl=res.predicted_spike_mg_dl,
        net_carbs_g=res.net_carbs_g,
        time_to_peak_min=res.time_to_peak_min,
        with_walk_spike_mg_dl=res.with_walk_spike_mg_dl,
        risk=res.risk,
        explanation=res.explanation,
    )


async def resolve_hypo_check(patient_id: str) -> HypoCheck:
    res = check_hypoglycemia(patient_id)
    return HypoCheck(
        patient_id=res.patient_id,
        hypo_events=res.hypo_events,
        critical_events=res.critical_events,
        last_event=res.last_event,
        alert_level=res.alert_level,
    )


# ─── Labs ───
async def resolve_lab_events(patient_id: str, limit: int = 200) -> LabEventList:
    res = get_lab_events(patient_id, limit=limit)
    return LabEventList(
        patient_id=res.patient_id,
        events=[
            LabEvent(
                test=e.test,
                value=e.value,
                unit=e.unit,
                ref_low=e.ref_low,
                ref_high=e.ref_high,
                flag=e.flag,
                charttime=e.charttime,
                category=e.category,
            )
            for e in res.events
        ],
        total=res.total,
    )


async def resolve_interpret_labs(patient_id: str, limit: int = 50) -> LabInterpretation:
    res = interpret_labs(patient_id, limit=limit)
    return LabInterpretation(
        patient_id=res.patient_id,
        summary=res.summary,
        abnormal_markers=[
            AbnormalMarker(
                test=m.test,
                value=m.value,
                unit=m.unit,
                normal_range=m.normal_range,
                status=m.status,
                severity=m.severity,
                explanation=m.explanation,
                actions=m.actions,
            )
            for m in res.abnormal_markers
        ],
        risk_assessment=RiskAssessment(
            diabetes_risk=res.risk_assessment.diabetes_risk,
            cardiovascular_risk=res.risk_assessment.cardiovascular_risk,
            liver_risk=res.risk_assessment.liver_risk,
            kidney_risk=res.risk_assessment.kidney_risk,
        ),
        recommendations=res.recommendations,
        follow_up=res.follow_up,
    )


# ─── Chat ───
async def resolve_chat(
    message: str,
    patient_id: Optional[str] = None,
) -> ChatResponse:
    response, sources = await chat_service(
        patient_id=patient_id,
        user_message=message,
        history=[],
    )
    return ChatResponse(
        response=response,
        sources=[
            ChatSource(title=s.title, source=s.source, score=s.score) for s in sources
        ],
    )
