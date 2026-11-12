"""Document scan / OCR routes.

Upload an image of a lab report, prescription, or food label and get
structured data back. Uses the multimodal LLM for vision-based OCR.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.adapters.storage import get_storage_adapter
from app.core.auth import AuthenticatedUser, get_current_user
from app.modules.scan.schemas import DocumentType, ScanResponse
from app.modules.scan.service import scan_document

router = APIRouter(prefix="/api/v1/scan", tags=["scan"])


@router.post("", response_model=ScanResponse)
async def scan_image(
    image: UploadFile = File(...),
    document_type: str | None = Form(None),
) -> ScanResponse:
    """Upload a document image → auto-classify + extract structured data.

    Supported types: lab_report, prescription, food_label, general.
    If `document_type` is not provided, the LLM classifies it automatically.
    """
    storage = get_storage_adapter()
    content = await image.read()
    path = storage.save_upload(image.filename or "scan.jpg", content)

    dtype = None
    if document_type:
        try:
            dtype = DocumentType(document_type)
        except ValueError:
            dtype = None

    return await scan_document(path, document_type=dtype)


@router.post("/lab-report", response_model=ScanResponse)
async def scan_lab_report(
    image: UploadFile = File(...),
) -> ScanResponse:
    """Shortcut: scan a lab report image directly."""
    storage = get_storage_adapter()
    content = await image.read()
    path = storage.save_upload(image.filename or "lab_report.jpg", content)
    return await scan_document(path, document_type=DocumentType.lab_report)


@router.post("/prescription", response_model=ScanResponse)
async def scan_prescription(
    image: UploadFile = File(...),
) -> ScanResponse:
    """Shortcut: scan a prescription image directly."""
    storage = get_storage_adapter()
    content = await image.read()
    path = storage.save_upload(image.filename or "prescription.jpg", content)
    return await scan_document(path, document_type=DocumentType.prescription)


@router.post("/food-label", response_model=ScanResponse)
async def scan_food_label(
    image: UploadFile = File(...),
) -> ScanResponse:
    """Shortcut: scan a nutrition label image directly."""
    storage = get_storage_adapter()
    content = await image.read()
    path = storage.save_upload(image.filename or "food_label.jpg", content)
    return await scan_document(path, document_type=DocumentType.food_label)


# ── Lab report storage (user-scoped) ────────────────────────────────────────

lab_router = APIRouter(tags=["lab-reports"])


@lab_router.post("/api/v1/users/me/lab-reports")
async def upload_lab_report(
    image: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    """Upload a lab report image, scan it, and save to user's records."""
    storage = get_storage_adapter()
    content = await image.read()
    path = storage.save_upload(image.filename or "lab_report.jpg", content)
    result = await scan_document(path, document_type=DocumentType.lab_report)

    report_id = uuid4().hex[:12]
    report = {
        "report_id": report_id,
        "scanned_at": datetime.now().isoformat(),
        "document_type": result.document_type.value,
        "lab_report": result.lab_report.model_dump() if result.lab_report else None,
        "raw_text": result.raw_text,
        "confidence": result.confidence,
    }

    u = storage.load_user(user.internal_id)
    if u:
        u.setdefault("lab_reports", []).append(report)
        storage.save_user(u)

    return report


@lab_router.get("/api/v1/users/me/lab-reports")
def list_lab_reports(
    user: AuthenticatedUser = Depends(get_current_user),
) -> list[dict]:
    """List all saved lab report scans for the user."""
    storage = get_storage_adapter()
    u = storage.load_user(user.internal_id)
    return u.get("lab_reports", []) if u else []
