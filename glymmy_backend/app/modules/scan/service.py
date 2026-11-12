"""Document scan / OCR service.

Uses the multimodal LLM (Gemma 4 vision) to extract structured data from
images of lab reports, prescriptions, and food nutrition labels. No
external OCR library needed — the LLM reads the image directly.
"""

from __future__ import annotations

import json
import re
from typing import Any

from loguru import logger

from app.adapters.llm import get_llm_adapter
from app.modules.scan.schemas import (
    DocumentType,
    ExtractedField,
    FoodLabelResult,
    LabReportResult,
    PrescriptionResult,
    ScanResponse,
)

# ── Prompts ──────────────────────────────────────────────────────────────────

CLASSIFY_PROMPT = """You are Glymmy, a medical document analysis AI.

Look at this image and determine the document type. Return ONLY one of:
- lab_report
- prescription
- food_label
- general

Return just the single label, nothing else."""

LAB_REPORT_PROMPT = """You are Glymmy, a medical document analysis AI.

Extract ALL information from this lab report image. Return a JSON object:

{
  "patient_name": string or null,
  "date": string or null,
  "lab_name": string or null,
  "tests": [
    {"key": "test name", "value": "result value", "unit": "unit or null",
     "reference_range": "range or null", "flag": "normal|abnormal|critical"}
  ],
  "summary": "brief clinical summary of findings"
}

Be thorough — extract EVERY test result visible. Flag abnormal values.
Return ONLY valid JSON, no prose outside it."""

PRESCRIPTION_PROMPT = """You are Glymmy, a medical document analysis AI.

Extract ALL information from this prescription image. Return a JSON object:

{
  "patient_name": string or null,
  "doctor_name": string or null,
  "date": string or null,
  "medications": [
    {"name": "drug name", "dosage": "dose", "frequency": "how often",
     "duration": "how long"}
  ],
  "notes": "any additional instructions or null"
}

Return ONLY valid JSON, no prose outside it."""

FOOD_LABEL_PROMPT = """You are Glymmy, a nutrition analysis AI.

Extract ALL information from this food nutrition label. Return a JSON object:

{
  "product_name": string or null,
  "serving_size": string or null,
  "calories": number or null,
  "carbs_g": number or null,
  "sugar_g": number or null,
  "protein_g": number or null,
  "fat_g": number or null,
  "fiber_g": number or null,
  "sodium_mg": number or null,
  "ingredients": ["ingredient1", "ingredient2", ...] or null
}

Return ONLY valid JSON, no prose outside it."""

GENERAL_OCR_PROMPT = """You are Glymmy, a document analysis AI.

Extract ALL text visible in this image. Preserve the structure and layout
as much as possible. Return the extracted text as plain text."""


def _parse_json(text: str) -> dict[str, Any]:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No JSON found in LLM response")


async def classify_document(image_path: str) -> DocumentType:
    """Use vision LLM to classify the document type."""
    llm = get_llm_adapter()
    messages = [
        {"role": "system", "content": CLASSIFY_PROMPT},
        {"role": "user", "content": "What type of document is this?"},
    ]
    raw = await llm.chat_with_image(messages, image_path=image_path, temperature=0.1)
    raw = raw.strip().lower().replace('"', "").replace("'", "")
    for dt in DocumentType:
        if dt.value in raw:
            return dt
    return DocumentType.general


async def scan_document(
    image_path: str,
    document_type: DocumentType | None = None,
) -> ScanResponse:
    """Scan a document image and extract structured data.

    If document_type is None, the LLM classifies it first.
    """
    llm = get_llm_adapter()
    if not llm.supports_vision:
        raise RuntimeError(f"LLM provider {llm.provider_name} does not support vision")

    # Step 1: classify if not provided
    if document_type is None:
        document_type = await classify_document(image_path)
        logger.info(f"Auto-classified document as: {document_type.value}")

    # Step 2: extract based on type
    prompt_map = {
        DocumentType.lab_report: LAB_REPORT_PROMPT,
        DocumentType.prescription: PRESCRIPTION_PROMPT,
        DocumentType.food_label: FOOD_LABEL_PROMPT,
        DocumentType.general: GENERAL_OCR_PROMPT,
    }
    prompt = prompt_map[document_type]
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Extract all information from this document."},
    ]
    raw = await llm.chat_with_image(messages, image_path=image_path, temperature=0.1)
    logger.debug(f"Scan LLM raw response ({document_type.value}): {raw[:300]}")

    # Step 3: parse into structured response
    response = ScanResponse(
        document_type=document_type,
        raw_text=raw,
        confidence=0.85,
    )

    if document_type == DocumentType.general:
        # For general OCR, raw_text is the output — no structured parse
        return response

    try:
        data = _parse_json(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning(f"Failed to parse structured scan output: {exc}")
        response.confidence = 0.4
        return response

    if document_type == DocumentType.lab_report:
        response.lab_report = LabReportResult(
            patient_name=data.get("patient_name"),
            date=data.get("date"),
            lab_name=data.get("lab_name"),
            tests=[ExtractedField(**t) for t in data.get("tests", [])],
            summary=data.get("summary", ""),
        )
        response.confidence = 0.9

    elif document_type == DocumentType.prescription:
        response.prescription = PrescriptionResult(
            patient_name=data.get("patient_name"),
            doctor_name=data.get("doctor_name"),
            date=data.get("date"),
            medications=data.get("medications", []),
            notes=data.get("notes"),
        )
        response.confidence = 0.85

    elif document_type == DocumentType.food_label:
        response.food_label = FoodLabelResult(**{
            k: data.get(k)
            for k in FoodLabelResult.model_fields
        })
        response.confidence = 0.9

    return response
