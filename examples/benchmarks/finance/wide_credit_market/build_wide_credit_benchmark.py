#!/usr/bin/env python3
"""Build a broad US credit-market distress benchmark without model API calls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
REPO = next(
    parent
    for parent in [HERE, *HERE.parents]
    if (parent / "examples/notebooks/finance/data/offline_reproduction/inputs/prices_total_return.csv").exists()
)
PRICE_FILE = REPO / "examples/notebooks/finance/data/offline_reproduction/inputs/prices_total_return.csv"
CACHE = HERE / "source_cache"
OUT = HERE / "wide_credit_market_benchmark.csv"
MANIFEST = HERE / "wide_credit_market_benchmark_manifest.json"

STATES = ["Normal", "Elevated", "Stressed", "Severe"]
THRESHOLDS = np.array([0.50, 0.75, 0.90])
SOFTNESS = 0.055
MIN_HISTORY_WEEKS = 104


def read_fred(series_id: str) -> pd.Series:
    frame = pd.read_csv(CACHE / f"{series_id}.csv", parse_dates=["observation_date"])
    values = pd.to_numeric(frame[series_id], errors="coerce")
    return pd.Series(values.to_numpy(), index=frame["observation_date"], name=series_id).sort_index()


def expanding_percentile(series: pd.Series, min_periods: int = MIN_HISTORY_WEEKS) -> pd.Series:
    """Past-and-present empirical percentile; no future observations enter."""
    values = series.to_numpy(float)
    out = np.full(len(values), np.nan)
    for i, value in enumerate(values):
        history = values[: i + 1]
        history = history[np.isfinite(history)]
        if np.isfinite(value) and len(history) >= min_periods:
            out[i] = (np.sum(history < value) + 0.5 * np.sum(history == value)) / len(history)
    return pd.Series(out, index=series.index, name=f"pct_{series.name}")


def ordinal_probabilities(score: float) -> np.ndarray:
    cumulative = 1.0 / (1.0 + np.exp((score - THRESHOLDS) / SOFTNESS))
    probs = np.array(
        [cumulative[0], cumulative[1] - cumulative[0], cumulative[2] - cumulative[1], 1.0 - cumulative[2]]
    )
    return np.maximum(probs, 0.0) / probs.sum()


def direction(value: float, previous: float, unit: str = "") -> str:
    change = value - previous
    if abs(change) < 1e-10:
        return "unchanged"
    return f"{abs(change):.2f}{unit} {'higher' if change > 0 else 'lower'}"


def assign_partitions(states: pd.Series) -> pd.Series:
    """Deterministic state-stratified split; chronology is tested separately."""
    names = ["calibration", "prompt_validation", "conformal", "test"]
    proportions = np.array([0.45, 0.10, 0.15, 0.30])
    values = pd.Series(index=states.index, dtype=object)
    rng = np.random.default_rng(20260827)
    for state in STATES:
        positions = np.flatnonzero(states.to_numpy() == state)
        positions = rng.permutation(positions)
        expected = proportions * len(positions)
        counts = np.floor(expected).astype(int)
        remainder = len(positions) - counts.sum()
        for j in np.argsort(-(expected - counts))[:remainder]:
            counts[j] += 1
        start = 0
        for name, count in zip(names, counts):
            selected = positions[start : start + count]
            values.iloc[selected] = name
            start += count
    return values


def main() -> None:
    prices = pd.read_csv(PRICE_FILE, index_col=0, parse_dates=True).sort_index()
    weekly_prices = prices[["HYG", "LQD", "SHY"]].resample("W-FRI").last().dropna()

    weekly = pd.DataFrame(index=weekly_prices.index)
    weekly["baa_spread"] = read_fred("BAA10Y").resample("W-FRI").last().reindex(weekly.index).ffill()
    weekly["aaa_spread"] = read_fred("AAA10Y").resample("W-FRI").last().reindex(weekly.index).ffill()
    weekly["quality_dispersion"] = weekly["baa_spread"] - weekly["aaa_spread"]
    weekly["nfci_credit"] = read_fred("NFCICREDIT").resample("W-FRI").last().reindex(weekly.index).ffill()
    weekly["stlfsi"] = read_fred("STLFSI4").resample("W-FRI").last().reindex(weekly.index).ffill()

    weekly["hyg_lqd_4w"] = -(weekly_prices["HYG"] / weekly_prices["LQD"]).pct_change(4)
    weekly["lqd_shy_4w"] = -(weekly_prices["LQD"] / weekly_prices["SHY"]).pct_change(4)
    weekly["hyg_drawdown_13w"] = -(weekly_prices["HYG"] / weekly_prices["HYG"].rolling(13).max() - 1.0)
    weekly["hyg_vol_13w"] = weekly_prices["HYG"].pct_change().rolling(13).std() * np.sqrt(52)

    # Slow-moving context is lagged conservatively; it does not define the score.
    for series_id, name in [("DRTSCILM", "sloos_large"), ("DRTSCIS", "sloos_small"), ("DRBLACBS", "business_delinquency")]:
        released = read_fred(series_id).copy()
        released.index = released.index + pd.Timedelta(days=45)
        weekly[name] = released.reindex(weekly.index, method="ffill")

    indicator_groups = {
        "spread": ["baa_spread", "quality_dispersion"],
        "traded": ["hyg_lqd_4w", "lqd_shy_4w", "hyg_drawdown_13w", "hyg_vol_13w"],
        "systemic": ["nfci_credit", "stlfsi"],
    }
    percentile_columns: list[str] = []
    for columns in indicator_groups.values():
        for column in columns:
            pct_name = f"pct_{column}"
            weekly[pct_name] = expanding_percentile(weekly[column])
            percentile_columns.append(pct_name)
    weekly["spread_component"] = weekly[[f"pct_{x}" for x in indicator_groups["spread"]]].mean(axis=1)
    weekly["traded_component"] = weekly[[f"pct_{x}" for x in indicator_groups["traded"]]].mean(axis=1)
    weekly["systemic_component"] = weekly[[f"pct_{x}" for x in indicator_groups["systemic"]]].mean(axis=1)
    weekly = weekly.dropna(subset=["spread_component", "traded_component", "systemic_component"]).copy()
    weekly["distress_score"] = weekly[["spread_component", "traded_component", "systemic_component"]].mean(axis=1)
    weekly = weekly.dropna(subset=["distress_score", "sloos_large", "sloos_small", "business_delinquency"]).copy()

    soft = np.vstack([ordinal_probabilities(value) for value in weekly["distress_score"]])
    for k, state in enumerate(STATES):
        weekly[f"reference_p_{state.lower()}"] = soft[:, k]
    weekly["reference_state"] = [STATES[i] for i in np.argmax(soft, axis=1)]
    weekly["partition"] = assign_partitions(weekly["reference_state"])
    temporal_cut = weekly.index[int(np.floor(0.80 * len(weekly)))]
    weekly["recent_temporal_holdout"] = weekly.index >= temporal_cut

    records = []
    for i, (date, row) in enumerate(weekly.iterrows()):
        prior = weekly.iloc[max(0, i - 1)]
        evidence = (
            f"As of {date.date()}, broad US credit conditions were summarized from independent market and lending channels. "
            f"The Baa-minus-Treasury spread was {row.baa_spread:.2f} percentage points "
            f"({direction(row.baa_spread, prior.baa_spread, ' pp')} over the latest week), while the Baa-minus-Aaa quality "
            f"dispersion was {row.quality_dispersion:.2f} percentage points. Over four weeks, high-yield credit returned "
            f"{(-row.hyg_lqd_4w):+.1%} relative to investment-grade credit, and investment-grade credit returned "
            f"{(-row.lqd_shy_4w):+.1%} relative to short Treasuries. High-yield drawdown from its 13-week peak was "
            f"{row.hyg_drawdown_13w:.1%}, with 13-week annualized volatility of {row.hyg_vol_13w:.1%}. "
            f"The Federal Reserve credit-conditions index was {row.nfci_credit:.2f} and the St. Louis financial-stress "
            f"index was {row.stlfsi:.2f}. The latest conservatively lagged bank survey readings showed net tightening of "
            f"{row.sloos_large:.1f}% for large and middle-market C&I loans and {row.sloos_small:.1f}% for small-firm C&I "
            f"loans; the business-loan delinquency rate was {row.business_delinquency:.2f}%."
        )
        records.append(
            {
                "source_id": f"wide-credit-{date.date()}",
                "decision_date": str(date.date()),
                "target_name": "current broad US credit-market distress state",
                "evaluation_horizon": "current weekly evidence snapshot",
                "evidence_text": evidence,
                "reference_state": row.reference_state,
                "reference_p_normal": row.reference_p_normal,
                "reference_p_elevated": row.reference_p_elevated,
                "reference_p_stressed": row.reference_p_stressed,
                "reference_p_severe": row.reference_p_severe,
                "distress_score": row.distress_score,
                "spread_component": row.spread_component,
                "traded_component": row.traded_component,
                "systemic_component": row.systemic_component,
                "partition": row.partition,
                "recent_temporal_holdout": bool(row.recent_temporal_holdout),
                "point_in_time_certified": False,
                "vintage_status": "market observations archived; FRED macro series use downloaded historical vintage",
            }
        )

    frame = pd.DataFrame(records)
    frame.to_csv(OUT, index=False, float_format="%.10f")
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    counts = frame["partition"].value_counts().to_dict()
    class_counts = frame["reference_state"].value_counts().to_dict()

    manifest = {
        "schema_version": "belieflens-benchmark-manifest-v1",
        "benchmark": {
            "id": "broad-us-credit-market-distress-v0.1",
            "name": "Broad US Credit-Market Distress Benchmark",
            "version": "0.1.0",
            "status": "provisional_research_candidate",
            "description": "Weekly semantic-measurement benchmark spanning public spreads, traded credit, systemic credit conditions, bank lending standards, and loan performance.",
            "domain": "finance",
            "use_case": "semantic_state_measurement",
            "record_count": len(frame),
        },
        "estimand": {
            "target_name": "current broad US credit-market distress state",
            "evaluation_horizon": "current weekly evidence snapshot",
            "scope": "system-wide US corporate and bank-intermediated credit conditions; not issuer default probability, expected loss, or a trading forecast",
        },
        "ontology": {
            "id": "broad-us-credit-distress-v1",
            "type": "finite_ordered",
            "ordered_states": STATES,
            "states": [
                {"value": "Normal", "definition": "Credit availability, pricing, liquidity, and traded-credit behavior are broadly benign."},
                {"value": "Elevated", "definition": "Credit conditions show a meaningful but not broadly stressed deterioration."},
                {"value": "Stressed", "definition": "Deterioration is broad or pronounced across several credit channels."},
                {"value": "Severe", "definition": "Credit conditions are exceptionally impaired relative to the walk-forward historical record."},
            ],
            "measurement_residual": {"value": "Unclear", "is_reference_state": False},
        },
        "reference_construction": {
            "type": "constructed_soft_ordinal_reference",
            "warning": "The reference distribution is induced by a prespecified index and is not claimed to be the market's latent true posterior.",
            "walk_forward_percentiles": True,
            "minimum_history_weeks": MIN_HISTORY_WEEKS,
            "group_weights": {"public_spreads": 1 / 3, "traded_credit": 1 / 3, "systemic_credit": 1 / 3},
            "ordinal_thresholds": THRESHOLDS.tolist(),
            "logistic_softness": SOFTNESS,
            "categorical_reference": "argmax of the constructed soft reference distribution",
            "slow_context_policy": "SLOOS and delinquency observations are shifted by a conservative 45 days and excluded from the reference score.",
        },
        "data": {
            "path": OUT.name,
            "sha256": digest,
            "date_range": {"start": frame.decision_date.min(), "end": frame.decision_date.max()},
            "primary_key": "source_id",
            "required_columns": list(frame.columns),
        },
        "partitions": {
            "frozen": False,
            "method": "deterministic state-stratified split with seed 20260827",
            "counts": counts,
            "temporal_holdout": {
                "field": "recent_temporal_holdout",
                "purpose": "separate recent-era distribution-shift audit; not used to fit the primary calibrator",
                "start": str(temporal_cut.date()),
            },
        },
        "class_counts": class_counts,
        "provenance": {
            "price_archive": str(PRICE_FILE.relative_to(REPO)),
            "fred_series": ["BAA10Y", "AAA10Y", "NFCICREDIT", "STLFSI4", "DRTSCILM", "DRTSCIS", "DRBLACBS"],
            "provider_model_calls": 0,
            "point_in_time_certified": False,
            "freeze_gate": "Obtain archival-vintage verification, independent label-rule review, and license review before freezing or claiming deployment-valid point-in-time performance.",
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"records": len(frame), "partitions": counts, "states": class_counts, "csv": str(OUT), "manifest": str(MANIFEST)}, indent=2))


if __name__ == "__main__":
    main()
