import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FINANCE = ROOT / "examples" / "notebooks" / "finance"
DERIVED = FINANCE / "data" / "derived" / "walk_forward_v1"
SOURCE = FINANCE / "data" / "offline_reproduction" / "row_level_measurements.csv"


def test_walk_forward_vintages_are_strictly_point_in_time() -> None:
    result = json.loads((DERIVED / "walk_forward_result.json").read_text())
    rows = pd.read_csv(DERIVED / "walk_forward_measurements.csv", parse_dates=["date"])
    vintages = {row["vintage_id"]: row for row in result["vintages"]}

    for vintage_id, group in rows.groupby("calibration_vintage"):
        vintage = vintages[vintage_id]
        deployment = pd.Timestamp(vintage["deployment_date"])
        assert (group["date"] >= deployment).all()
        latest = vintage["latest_eligible_outcome_end"]
        if latest is not None:
            assert pd.Timestamp(latest) < deployment


def test_walk_forward_analysis_preserves_frozen_measurements() -> None:
    result = json.loads((DERIVED / "walk_forward_result.json").read_text())
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert result["source_artifacts_modified"] is False
    assert digest == result["source_sha256"]
