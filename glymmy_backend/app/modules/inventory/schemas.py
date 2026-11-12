"""Health inventory schemas."""

from __future__ import annotations

from pydantic import BaseModel


class Medication(BaseModel):
    name: str
    dosage: str
    frequency: str
    prescriber: str | None = None
    start_date: str | None = None
    notes: str | None = None


class Allergy(BaseModel):
    allergen: str
    reaction: str
    severity: str = "mild"  # mild | moderate | severe


class Condition(BaseModel):
    name: str
    diagnosed_date: str | None = None
    status: str = "active"  # active | resolved | managed
    notes: str | None = None


class EmergencyContact(BaseModel):
    name: str
    relationship: str
    phone: str
    email: str | None = None


class HealthInventory(BaseModel):
    blood_type: str | None = None
    medications: list[Medication] = []
    allergies: list[Allergy] = []
    conditions: list[Condition] = []
    emergency_contacts: list[EmergencyContact] = []
    insurance_provider: str | None = None
    insurance_id: str | None = None
    primary_physician: str | None = None
    notes: str | None = None
