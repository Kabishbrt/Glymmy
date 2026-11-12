"""Strawberry GraphQL schema — the public Query and Mutation roots.

Mirrors REST in capability but exposes a flexible query language. Both
APIs share `service.py` business logic.
"""

from __future__ import annotations

from typing import Optional

import strawberry

from app.graphql.resolvers import (
    resolve_chat,
    resolve_glucose_series,
    resolve_hypo_check,
    resolve_interpret_labs,
    resolve_lab_events,
    resolve_patient,
    resolve_patients,
    resolve_predict_spike,
)
from app.graphql.types import (
    ChatResponse,
    GlucoseSeries,
    HypoCheck,
    LabEventList,
    LabInterpretation,
    MealInput,
    Patient,
    SpikePrediction,
)


@strawberry.type
class Query:
    @strawberry.field
    async def patients(self) -> list[Patient]:
        """List every available patient across all data adapters."""
        return await resolve_patients()

    @strawberry.field
    async def patient(self, id: str) -> Optional[Patient]:
        """Fetch a single patient by ID."""
        return await resolve_patient(id)

    @strawberry.field
    async def glucose_series(
        self, patient_id: str, limit: int = 500
    ) -> GlucoseSeries:
        """Return CGM readings + summary stats for a patient."""
        return await resolve_glucose_series(patient_id, limit)

    @strawberry.field
    async def hypo_check(self, patient_id: str) -> HypoCheck:
        """Scan for nocturnal hypoglycemia events."""
        return await resolve_hypo_check(patient_id)

    @strawberry.field
    async def lab_events(
        self, patient_id: str, limit: int = 200
    ) -> LabEventList:
        """Return raw lab events for a patient."""
        return await resolve_lab_events(patient_id, limit)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def predict_meal_spike(
        self,
        patient_id: str,
        meal: MealInput,
        pre_meal_glucose: Optional[float] = None,
    ) -> SpikePrediction:
        """Predict the glucose spike from a proposed meal."""
        return await resolve_predict_spike(patient_id, meal, pre_meal_glucose)

    @strawberry.mutation
    async def interpret_labs(
        self, patient_id: str, limit: int = 50
    ) -> LabInterpretation:
        """Interpret recent lab events into plain-language insights."""
        return await resolve_interpret_labs(patient_id, limit)

    @strawberry.mutation
    async def chat(
        self,
        message: str,
        patient_id: Optional[str] = None,
    ) -> ChatResponse:
        """Send a message to the RAG-powered Glymmy chat."""
        return await resolve_chat(message, patient_id)


schema = strawberry.Schema(query=Query, mutation=Mutation)
