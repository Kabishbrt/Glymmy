"""GlucoBench CGM adapter — loads Dubosson and Hall datasets from CSV.

- Dubosson (T1D): 9 patients with glucose + insulin + calories + HR + activity
- Hall: 57 patients across healthy/prediabetic/diabetic populations
"""

from __future__ import annotations

from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from app.adapters.cgm.base import CGMAdapter
from app.core.config import get_settings
from app.core.exceptions import DatasetNotFoundError, PatientNotFoundError


class GlucoBenchAdapter(CGMAdapter):
    """Reads CGM data from local GlucoBench CSV files."""

    def __init__(self) -> None:
        settings = get_settings()
        self._base = Path(settings.DATASET_DIR) / "GlucoBench" / "raw_data"
        self._dubosson_path = self._base / "dubosson.csv"
        self._hall_path = self._base / "hall.csv"
        logger.info(f"GlucoBenchAdapter initialized | base={self._base}")

    @property
    def provider_name(self) -> str:
        return "glucobench"

    @cached_property
    def _dubosson(self) -> pd.DataFrame:
        if not self._dubosson_path.exists():
            raise DatasetNotFoundError(f"Not found: {self._dubosson_path}")
        df = pd.read_csv(self._dubosson_path)
        df["time"] = pd.to_datetime(df["time"])
        df["id"] = df["id"].astype(str)
        logger.info(f"Loaded Dubosson: {len(df)} rows, {df['id'].nunique()} patients")
        return df

    @cached_property
    def _hall(self) -> pd.DataFrame:
        if not self._hall_path.exists():
            raise DatasetNotFoundError(f"Not found: {self._hall_path}")
        df = pd.read_csv(self._hall_path)
        df["time"] = pd.to_datetime(df["time"])
        df["id"] = df["id"].astype(str)
        logger.info(f"Loaded Hall: {len(df)} rows, {df['id'].nunique()} patients")
        return df

    def list_patients(self) -> list[dict[str, Any]]:
        patients: list[dict[str, Any]] = []

        # Dubosson — T1D with rich physiological signals
        for pid in sorted(self._dubosson["id"].unique()):
            rows = self._dubosson[self._dubosson["id"] == pid]
            patients.append(
                {
                    "id": f"dubosson_{pid}",
                    "source": "dubosson",
                    "dataset": "GlucoBench/Dubosson",
                    "name": f"T1D Patient {pid}",
                    "diagnosis": "Type 1 Diabetes",
                    "num_readings": int(len(rows)),
                    "start": rows["time"].min().isoformat(),
                    "end": rows["time"].max().isoformat(),
                    "has_insulin": True,
                    "has_activity": True,
                }
            )

        # Hall — population-level (healthy + prediabetic + diabetic)
        diag_map = {0: "Healthy", 1: "Prediabetic", 2: "Diabetic"}
        for pid in sorted(self._hall["id"].unique())[:20]:  # cap list size
            rows = self._hall[self._hall["id"] == pid]
            diag_val = int(rows["diagnosis"].iloc[0])
            age_val = rows["Age"].iloc[0] if "Age" in rows else None
            bmi_val = rows["BMI"].iloc[0] if "BMI" in rows else None
            a1c_val = rows["A1C"].iloc[0] if "A1C" in rows else None
            patients.append(
                {
                    "id": f"hall_{pid}",
                    "source": "hall",
                    "dataset": "GlucoBench/Hall",
                    "name": f"Hall Patient {pid[:8]}",
                    "diagnosis": diag_map.get(diag_val, "Unknown"),
                    "age": None if pd.isna(age_val) else float(age_val),
                    "bmi": None if pd.isna(bmi_val) else float(bmi_val),
                    "a1c": None if pd.isna(a1c_val) else float(a1c_val),
                    "num_readings": int(len(rows)),
                }
            )

        return patients

    def _select_df_and_pid(self, patient_id: str) -> tuple[pd.DataFrame, str]:
        if patient_id.startswith("dubosson_"):
            return self._dubosson, patient_id.removeprefix("dubosson_")
        if patient_id.startswith("hall_"):
            return self._hall, patient_id.removeprefix("hall_")
        raise PatientNotFoundError(f"Unknown patient prefix: {patient_id}")

    def get_readings(
        self,
        patient_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        df, pid = self._select_df_and_pid(patient_id)
        rows = df[df["id"] == pid].copy()
        if rows.empty:
            raise PatientNotFoundError(f"No readings for {patient_id}")

        if start is not None:
            rows = rows[rows["time"] >= pd.Timestamp(start)]
        if end is not None:
            rows = rows[rows["time"] <= pd.Timestamp(end)]

        rows = rows.sort_values("time")
        if limit:
            rows = rows.head(limit)

        readings: list[dict[str, Any]] = []
        for _, r in rows.iterrows():
            reading = {
                "timestamp": r["time"].isoformat(),
                "glucose_mg_dl": float(r["gl"]),
            }
            # Dubosson has extra physiological signals
            if "HR" in rows.columns and not pd.isna(r.get("HR")):
                reading["heart_rate"] = float(r["HR"])
            if "Activity" in rows.columns and not pd.isna(r.get("Activity")):
                reading["activity"] = float(r["Activity"])
            if "fast_insulin" in rows.columns and not pd.isna(r.get("fast_insulin")):
                reading["fast_insulin"] = float(r["fast_insulin"])
            if "slow_insulin" in rows.columns and not pd.isna(r.get("slow_insulin")):
                reading["slow_insulin"] = float(r["slow_insulin"])
            if "calories" in rows.columns and not pd.isna(r.get("calories")):
                reading["calories"] = float(r["calories"])
            readings.append(reading)

        return readings

    def get_meal_events(self, patient_id: str) -> list[dict[str, Any]]:
        # Only Dubosson has meal (calorie) data
        if not patient_id.startswith("dubosson_"):
            return []
        df, pid = self._select_df_and_pid(patient_id)
        rows = df[(df["id"] == pid) & (df["calories"] > 0)].copy()
        rows = rows.sort_values("time")
        return [
            {
                "timestamp": r["time"].isoformat(),
                "calories": float(r["calories"]),
                "pre_meal_glucose": float(r["gl"]),
            }
            for _, r in rows.iterrows()
        ]
