"""Labs module business logic.

Interprets lab events against clinical reference ranges, produces
plain-language explanations and multi-organ risk assessment.
"""

from __future__ import annotations

from typing import Any

from app.adapters.labs import get_labs_adapter
from app.modules.labs.schemas import (
    AbnormalMarker,
    LabEventsResponse,
    LabInterpretation,
    RiskAssessment,
)

# Plain-language explanations keyed by test name (or substring match)
EXPLANATIONS: dict[str, dict[str, Any]] = {
    "Glucose": {
        "high": "Elevated blood sugar — may indicate prediabetes or diabetes if persistent.",
        "low": "Low blood sugar (hypoglycemia) — can cause dizziness or confusion.",
        "actions_high": [
            "Reduce refined carb intake",
            "Increase daily activity",
            "Schedule HbA1c test",
        ],
        "actions_low": ["Eat regular meals", "Carry glucose tablets"],
    },
    "Creatinine": {
        "high": "Elevated creatinine suggests reduced kidney filtering capacity.",
        "low": "Low creatinine may indicate reduced muscle mass.",
        "actions_high": ["Stay hydrated", "Avoid NSAIDs", "Get kidney function panel"],
        "actions_low": [],
    },
    "Hemoglobin": {
        "high": "High hemoglobin may indicate dehydration or a blood disorder.",
        "low": "Low hemoglobin indicates anemia — reduced oxygen-carrying capacity.",
        "actions_high": ["Stay hydrated"],
        "actions_low": [
            "Eat iron-rich foods (spinach, lentils, red meat)",
            "Check iron, B12, and folate levels",
        ],
    },
    "Potassium": {
        "high": "High potassium can affect heart rhythm — worth investigating.",
        "low": "Low potassium can cause muscle weakness and cramps.",
        "actions_high": ["Avoid potassium-rich supplements", "Review ACE inhibitors"],
        "actions_low": ["Eat bananas, oranges, and leafy greens"],
    },
    "Sodium": {
        "high": "Hypernatremia — often dehydration.",
        "low": "Hyponatremia — can be serious; check fluid balance.",
        "actions_high": ["Increase fluid intake"],
        "actions_low": ["Limit water intake briefly", "See doctor"],
    },
    "Urea Nitrogen": {
        "high": "Elevated BUN suggests reduced kidney function or high protein intake.",
        "low": "Low BUN usually not concerning.",
        "actions_high": ["Hydrate well", "Moderate protein intake"],
        "actions_low": [],
    },
    "Platelet Count": {
        "high": "Thrombocytosis — can increase clotting risk.",
        "low": "Thrombocytopenia — can increase bleeding risk.",
        "actions_high": ["Ask doctor about aspirin therapy"],
        "actions_low": ["Avoid NSAIDs", "Be cautious of injuries"],
    },
    "White Blood Cells": {
        "high": "High WBC suggests infection or inflammation.",
        "low": "Low WBC may indicate immune suppression.",
        "actions_high": ["Look for signs of infection"],
        "actions_low": ["Minimize exposure to illness"],
    },
    "Calcium": {
        "high": "High calcium can affect kidneys and heart.",
        "low": "Low calcium can cause muscle spasms.",
        "actions_high": ["Check parathyroid function"],
        "actions_low": ["Add dairy or calcium-rich foods", "Check vitamin D"],
    },
}


def _match_explanation(test: str) -> dict[str, Any] | None:
    """Return explanation dict by substring match on test name."""
    for key, expl in EXPLANATIONS.items():
        if key.lower() in test.lower():
            return expl
    return None


def _severity(value: float, low: float | None, high: float | None) -> str:
    if low is not None and value < low:
        deviation = (low - value) / low
    elif high is not None and value > high:
        deviation = (value - high) / high
    else:
        return "mild"
    if deviation > 0.5:
        return "severe"
    if deviation > 0.2:
        return "moderate"
    return "mild"


def get_lab_events(patient_id: str, limit: int = 200) -> LabEventsResponse:
    adapter = get_labs_adapter()
    raw = adapter.get_lab_events(patient_id, limit=limit)
    events = [
        {
            "test": r["test"],
            "category": r.get("category"),
            "value": r.get("value"),
            "raw_value": r.get("raw_value"),
            "unit": r.get("unit"),
            "ref_low": r.get("ref_low"),
            "ref_high": r.get("ref_high"),
            "flag": r.get("flag") or "normal",
            "charttime": r.get("charttime"),
        }
        for r in raw
    ]
    return LabEventsResponse(patient_id=patient_id, events=events, total=len(events))


def interpret_labs(patient_id: str, limit: int = 50) -> LabInterpretation:
    """Interpret the most recent N lab events for a patient."""
    adapter = get_labs_adapter()
    raw = adapter.get_lab_events(patient_id, limit=limit)

    abnormal_markers: list[AbnormalMarker] = []
    seen: set[str] = set()

    for r in raw:
        test = r["test"]
        if test in seen:
            continue  # only flag each test once (most recent)
        seen.add(test)

        value = r.get("value")
        low = r.get("ref_low")
        high = r.get("ref_high")
        flag = (r.get("flag") or "").lower()

        if value is None:
            continue
        if flag != "abnormal":
            continue
        if low is None and high is None:
            continue

        if low is not None and value < low:
            status = "LOW"
            high_status = False
        elif high is not None and value > high:
            status = "HIGH"
            high_status = True
        else:
            continue

        expl = _match_explanation(test)
        if expl is None:
            explanation = f"{test} is outside the normal range."
            actions: list[str] = ["Discuss with your doctor."]
        else:
            explanation = expl["high"] if high_status else expl["low"]
            actions = list(expl["actions_high" if high_status else "actions_low"])

        abnormal_markers.append(
            AbnormalMarker(
                test=test,
                value=value,
                unit=r.get("unit"),
                normal_range=f"{low}-{high}" if low is not None and high is not None else "n/a",
                status=status,
                severity=_severity(value, low, high),
                explanation=explanation,
                actions=actions,
            )
        )

    # Risk assessment heuristics based on which tests are flagged
    flagged_tests = {m.test.lower() for m in abnormal_markers}

    def _score(*keywords: str) -> str:
        hits = sum(1 for k in keywords if any(k in t for t in flagged_tests))
        return "high" if hits >= 2 else "moderate" if hits >= 1 else "low"

    risk = RiskAssessment(
        diabetes_risk=_score("glucose", "hba1c"),
        cardiovascular_risk=_score("cholesterol", "ldl", "triglyceride"),
        liver_risk=_score("sgot", "sgpt", "alt", "ast", "bilirubin"),
        kidney_risk=_score("creatinine", "urea", "bun"),
    )

    summary = (
        f"Reviewed {len(seen)} unique tests; flagged {len(abnormal_markers)} as abnormal."
    )
    recommendations = [
        "Discuss abnormal values with your primary care doctor.",
        "Re-test flagged markers in 4–6 weeks.",
        "Keep a consistent diet and activity log in Glymmy.",
    ]
    return LabInterpretation(
        patient_id=patient_id,
        summary=summary,
        abnormal_markers=abnormal_markers,
        risk_assessment=risk,
        recommendations=recommendations,
        follow_up="Re-check abnormal markers in 4–6 weeks unless otherwise advised.",
    )
