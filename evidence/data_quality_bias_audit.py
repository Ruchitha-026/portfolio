"""Clean a synthetic training-selection dataset and audit group-level outcomes.

The example intentionally contains a duplicate, a missing value, an impossible
attendance value, and inconsistent shift labels. It compares historical manager
nominations with a transparent objective eligibility rule. The script is an
educational audit, not an automated employment decision system.
"""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = Path(__file__).resolve().parent.parent

RAW_RECORDS = [
    {"candidate_id": "C01", "shift": "Day", "assessment_score": 92, "attendance_pct": 98, "manager_nominated": 1},
    {"candidate_id": "C02", "shift": "Day", "assessment_score": 88, "attendance_pct": 95, "manager_nominated": 1},
    {"candidate_id": "C03", "shift": "Day", "assessment_score": 76, "attendance_pct": 90, "manager_nominated": 1},
    {"candidate_id": "C04", "shift": "Day", "assessment_score": 70, "attendance_pct": 87, "manager_nominated": 0},
    {"candidate_id": "C05", "shift": "Day", "assessment_score": 68, "attendance_pct": 89, "manager_nominated": 1},
    {"candidate_id": "C06", "shift": "Day", "assessment_score": 84, "attendance_pct": 93, "manager_nominated": 0},
    {"candidate_id": "C07", "shift": "Evening", "assessment_score": 91, "attendance_pct": 96, "manager_nominated": 0},
    {"candidate_id": "C08", "shift": "evening", "assessment_score": 89, "attendance_pct": 94, "manager_nominated": 0},
    {"candidate_id": "C09", "shift": " Evening ", "assessment_score": 82, "attendance_pct": 92, "manager_nominated": 1},
    {"candidate_id": "C10", "shift": "Evening", "assessment_score": 78, "attendance_pct": 88, "manager_nominated": 0},
    {"candidate_id": "C11", "shift": "EVENING", "assessment_score": np.nan, "attendance_pct": 90, "manager_nominated": 0},
    {"candidate_id": "C12", "shift": "Evening", "assessment_score": 73, "attendance_pct": 145, "manager_nominated": 0},
    # Intentional duplicate.
    {"candidate_id": "C04", "shift": "Day", "assessment_score": 70, "attendance_pct": 87, "manager_nominated": 0},
]


def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Standardize, validate, deduplicate, and impute the demonstration data."""
    issues = {
        "raw_rows": len(raw),
        "duplicate_rows": int(raw.duplicated(subset=["candidate_id"]).sum()),
        "missing_scores": int(raw["assessment_score"].isna().sum()),
        "invalid_attendance": int((raw["attendance_pct"] > 100).sum() + (raw["attendance_pct"] < 0).sum()),
        "shift_label_variants": int(raw["shift"].nunique()),
    }

    cleaned = raw.drop_duplicates(subset=["candidate_id"], keep="first").copy()
    cleaned["shift"] = cleaned["shift"].str.strip().str.title()

    cleaned.loc[~cleaned["attendance_pct"].between(0, 100), "attendance_pct"] = np.nan
    cleaned["assessment_score"] = cleaned.groupby("shift")["assessment_score"].transform(
        lambda series: series.fillna(series.median())
    )
    cleaned["attendance_pct"] = cleaned.groupby("shift")["attendance_pct"].transform(
        lambda series: series.fillna(series.median())
    )

    # Transparent eligibility rule used for audit comparison.
    cleaned["objective_eligible"] = (
        (cleaned["assessment_score"] >= 75) & (cleaned["attendance_pct"] >= 88)
    ).astype(int)
    cleaned["review_note"] = np.where(
        cleaned["objective_eligible"].eq(1),
        "Eligible for documented human review",
        "Does not meet current published threshold",
    )
    issues["clean_rows"] = len(cleaned)
    return cleaned, issues


def selection_rates(data: pd.DataFrame, column: str) -> pd.Series:
    """Return group-level positive rates for a binary outcome column."""
    return data.groupby("shift")[column].mean().sort_index()


def save_evidence(cleaned: pd.DataFrame, issues: dict[str, int]) -> None:
    """Save cleaned data, audit summary, and a comparison chart."""
    evidence_dir = OUTPUT_DIR / "evidence"
    assets_dir = OUTPUT_DIR / "assets"
    cleaned.to_csv(evidence_dir / "data_quality_cleaned.csv", index=False)

    historical = selection_rates(cleaned, "manager_nominated")
    objective = selection_rates(cleaned, "objective_eligible")
    summary = {
        **issues,
        "historical_day_rate": round(float(historical.get("Day", 0)), 3),
        "historical_evening_rate": round(float(historical.get("Evening", 0)), 3),
        "historical_rate_gap": round(abs(float(historical.get("Day", 0) - historical.get("Evening", 0))), 3),
        "objective_day_rate": round(float(objective.get("Day", 0)), 3),
        "objective_evening_rate": round(float(objective.get("Evening", 0)), 3),
        "objective_rate_gap": round(abs(float(objective.get("Day", 0) - objective.get("Evening", 0))), 3),
    }
    (evidence_dir / "data_quality_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    chart = pd.DataFrame({"Historical nomination": historical, "Objective review rule": objective})
    chart.plot(kind="bar", figsize=(8, 4.8), rot=0)
    plt.title("Training-Selection Rate Audit by Shift")
    plt.xlabel("Shift group")
    plt.ylabel("Positive rate")
    plt.ylim(0, 1)
    plt.grid(axis="y", alpha=0.25)
    plt.legend(loc="upper center", ncol=2)
    plt.tight_layout()
    plt.savefig(assets_dir / "data_bias_audit.png", dpi=180)
    plt.close()

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    raw_data = pd.DataFrame(RAW_RECORDS)
    clean_records, audit_issues = clean_data(raw_data)
    save_evidence(clean_records, audit_issues)
