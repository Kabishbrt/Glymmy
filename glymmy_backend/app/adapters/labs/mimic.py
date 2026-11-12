"""MIMIC-IV Demo lab adapter — reads real hospital lab data (100 patients, 107K events)."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from app.adapters.labs.base import LabAdapter
from app.core.config import get_settings
from app.core.exceptions import DatasetNotFoundError, PatientNotFoundError


class MimicLabAdapter(LabAdapter):
    """Loads MIMIC-IV Demo lab events and item dictionary."""

    def __init__(self) -> None:
        settings = get_settings()
        base = Path(settings.DATASET_DIR)
        self._events_path = base / "mimic_labevents.csv"
        self._items_path = base / "mimic_d_labitems.csv"
        logger.info(f"MimicLabAdapter initialized | base={base}")

    @property
    def provider_name(self) -> str:
        return "mimic-iv-demo"

    @cached_property
    def _events(self) -> pd.DataFrame:
        if not self._events_path.exists():
            raise DatasetNotFoundError(f"Not found: {self._events_path}")
        df = pd.read_csv(self._events_path, low_memory=False)
        df["charttime"] = pd.to_datetime(df["charttime"], errors="coerce")
        logger.info(f"Loaded MIMIC lab events: {len(df)} rows")
        return df

    @cached_property
    def _items(self) -> pd.DataFrame:
        if not self._items_path.exists():
            raise DatasetNotFoundError(f"Not found: {self._items_path}")
        df = pd.read_csv(self._items_path)
        logger.info(f"Loaded MIMIC lab items: {len(df)} tests")
        return df

    @cached_property
    def _merged(self) -> pd.DataFrame:
        return self._events.merge(self._items, on="itemid", how="left")

    def list_patients(self, limit: int = 20) -> list[dict[str, Any]]:
        df = self._merged
        # Sort by abnormal flag count — interesting demo patients first
        abnormal = (
            df[df["flag"] == "abnormal"]
            .groupby("subject_id")
            .size()
            .rename("abnormal_count")
        )
        totals = df.groupby("subject_id").size().rename("total_events")
        latest = (
            df.dropna(subset=["charttime"])
            .groupby("subject_id")["charttime"]
            .max()
            .rename("latest")
        )
        summary = pd.concat([abnormal, totals, latest], axis=1).fillna(0)
        summary = summary.sort_values("abnormal_count", ascending=False).head(limit)

        patients: list[dict[str, Any]] = []
        for sid, row in summary.iterrows():
            latest_val = row["latest"]
            latest_iso = (
                latest_val.isoformat() if isinstance(latest_val, pd.Timestamp) else None
            )
            patients.append(
                {
                    "id": f"mimic_{sid}",
                    "source": "mimic",
                    "dataset": "MIMIC-IV Demo",
                    "name": f"Patient {sid}",
                    "diagnosis": "Hospital patient",
                    "num_lab_events": int(row["total_events"]),
                    "num_abnormal": int(row["abnormal_count"]),
                    "latest_lab": latest_iso,
                }
            )
        return patients

    def get_lab_events(
        self,
        patient_id: str,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        if not patient_id.startswith("mimic_"):
            raise PatientNotFoundError(f"Not a MIMIC patient: {patient_id}")
        sid = int(patient_id.removeprefix("mimic_"))
        rows = self._merged[self._merged["subject_id"] == sid].copy()
        if rows.empty:
            raise PatientNotFoundError(f"No lab events for {patient_id}")

        rows = rows.sort_values("charttime", ascending=False)
        if limit:
            rows = rows.head(limit)

        events: list[dict[str, Any]] = []
        for _, r in rows.iterrows():
            ct = r["charttime"]
            events.append(
                {
                    "test": str(r.get("label") or "Unknown"),
                    "category": str(r.get("category") or ""),
                    "value": (
                        float(r["valuenum"]) if not pd.isna(r["valuenum"]) else None
                    ),
                    "raw_value": str(r.get("value") or ""),
                    "unit": str(r.get("valueuom") or ""),
                    "ref_low": (
                        float(r["ref_range_lower"])
                        if not pd.isna(r["ref_range_lower"])
                        else None
                    ),
                    "ref_high": (
                        float(r["ref_range_upper"])
                        if not pd.isna(r["ref_range_upper"])
                        else None
                    ),
                    "flag": str(r.get("flag") or "normal"),
                    "charttime": ct.isoformat() if isinstance(ct, pd.Timestamp) else None,
                }
            )
        return events

    def get_test_catalog(self) -> list[dict[str, Any]]:
        counts = self._events.groupby("itemid").size().rename("count")
        merged = self._items.merge(counts, on="itemid", how="left").fillna(0)
        merged = merged.sort_values("count", ascending=False).head(100)
        return [
            {
                "itemid": int(r["itemid"]),
                "label": str(r["label"]),
                "category": str(r["category"]),
                "fluid": str(r["fluid"]),
                "count": int(r["count"]),
            }
            for _, r in merged.iterrows()
        ]
