"""Pydantic schemas for the document scan / OCR module."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class DocumentType(str, Enum):
    lab_report = "lab_report"
    prescription = "prescription"
    food_label = "food_label"
    general = "general"


class ExtractedField(BaseModel):
    key: str
    value: str
    unit: str | None = None
    reference_range: str | None = None
    flag: str | None = None  # normal | abnormal | critical


class LabReportResult(BaseModel):
    patient_name: str | None = None
    date: str | None = None
    lab_name: str | None = None
    tests: list[ExtractedField]
    summary: str


class PrescriptionResult(BaseModel):
    patient_name: str | None = None
    doctor_name: str | None = None
    date: str | None = None
    medications: list[dict]  # name, dosage, frequency, duration
    notes: str | None = None


class FoodLabelResult(BaseModel):
    product_name: str | None = None
    serving_size: str | None = None
    calories: float | None = None
    carbs_g: float | None = None
    sugar_g: float | None = None
    protein_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None
    sodium_mg: float | None = None
    ingredients: list[str] | None = None


class ScanResponse(BaseModel):
    document_type: DocumentType
    raw_text: str
    lab_report: LabReportResult | None = None
    prescription: PrescriptionResult | None = None
    food_label: FoodLabelResult | None = None
    confidence: float
    source: str = "vision-llm"
