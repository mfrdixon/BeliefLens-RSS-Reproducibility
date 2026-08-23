"""Build the derived SPY/SGOV walk-forward calibration analysis.

This script never modifies the frozen measurement archive.  It fits deployment
calibration vintages from stored language measurements whose reference outcome
was available strictly before each vintage date.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "data" / "offline_reproduction" / "row_level_measurements.csv"
OUT = HERE / "data" / "derived" / "walk_forward_v1"
FEATURES = [
    "alr_risk_on_vs_unsure",
    "alr_mixed_vs_unsure",
    "alr_risk_off_vs_unsure",
]
PROBABILITY_COLUMNS = ["wf_risk_on", "wf_mixed", "wf_risk_off"]
STATE_NAMES = ["Risk-on", "Mixed", "Risk-off"]
STATE_TO_INDEX = {state: index for index, state in enumerate(STATE_NAMES)}
TRANSACTION_COST = 0.0005


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def portfolio_metrics(returns: np.ndarray, safe_returns: np.ndarray) -> dict[str, float | int]:
    returns = np.asarray(returns, dtype=float)
    safe_returns = np.asarray(safe_returns, dtype=float)
    wealth = np.cumprod(1.0 + returns)
    drawdown = wealth / np.maximum.accumulate(wealth) - 1.0
    excess = returns - safe_returns
    excess_sd = float(np.std(excess, ddof=1))
    return {
        "observations": int(len(returns)),
        "total_return": float(wealth[-1] - 1.0),
        "annualized_return": float(wealth[-1] ** (252.0 / len(returns)) - 1.0),
        "annualized_volatility": float(np.std(returns, ddof=1) * np.sqrt(252.0)),
        "excess_sharpe_vs_sgov": float(np.mean(excess) / excess_sd * np.sqrt(252.0)) if excess_sd else 0.0,
        # Report the conventional loss magnitude so that, for example, 0.026
        # means a 2.6% peak-to-trough decline.  This matches the archived
        # comparator metrics used by the public notebook.
        "maximum_drawdown": float(-np.min(drawdown)),
    }


def measurement_metrics(probabilities: np.ndarray, labels: np.ndarray) -> dict[str, float | int]:
    one_hot = np.eye(3)[labels]
    return {
        "observations": int(len(labels)),
        "accuracy": float(accuracy_score(labels, probabilities.argmax(axis=1))),
        "log_loss": float(log_loss(labels, probabilities, labels=[0, 1, 2])),
        "multiclass_brier": float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1))),
    }


def main() -> None:
    rows = pd.read_csv(SOURCE, parse_dates=["date", "outcome_end"]).sort_values("date").reset_index(drop=True)
    historical = rows.loc[rows["date"] < "2026-01-01"].copy()
    test = rows.loc[rows["partition"] == "test"].copy().sort_values("date").reset_index(drop=True)
    historical["label"] = historical["external_regime"].map(STATE_TO_INDEX)
    test["label"] = test["external_regime"].map(STATE_TO_INDEX)

    predicted: list[np.ndarray] = []
    vintage_rows: list[dict[str, object]] = []
    fitted_week: tuple[int, int] | None = None
    model: LogisticRegression | None = None
    vintage_id = ""

    for _, observation in test.iterrows():
        date = pd.Timestamp(observation["date"])
        week = (int(date.isocalendar().year), int(date.isocalendar().week))
        if week != fitted_week:
            matured = test.loc[test["outcome_end"] < date].copy()
            train = pd.concat([historical, matured], ignore_index=True)
            model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=20260822)
            model.fit(train[FEATURES].to_numpy(), train["label"].to_numpy())
            vintage_id = f"weekly-{date.date().isoformat()}"
            vintage_rows.append(
                {
                    "vintage_id": vintage_id,
                    "deployment_date": date.date().isoformat(),
                    "latest_eligible_outcome_end": (
                        matured["outcome_end"].max().date().isoformat() if len(matured) else None
                    ),
                    "pre_2026_records": int(len(historical)),
                    "matured_2026_records": int(len(matured)),
                    "total_fit_records": int(len(train)),
                    "classes": [int(value) for value in model.classes_],
                    "coefficients": model.coef_.tolist(),
                    "intercept": model.intercept_.tolist(),
                }
            )
            fitted_week = week
        assert model is not None
        predicted.append(model.predict_proba(observation[FEATURES].to_numpy(dtype=float).reshape(1, -1))[0])

    probabilities = np.vstack(predicted)
    test[PROBABILITY_COLUMNS] = probabilities
    vintage_by_week = {
        (pd.Timestamp(row["deployment_date"]).isocalendar().year, pd.Timestamp(row["deployment_date"]).isocalendar().week): row["vintage_id"]
        for row in vintage_rows
    }
    test["calibration_vintage"] = [
        vintage_by_week[(date.isocalendar().year, date.isocalendar().week)] for date in test["date"]
    ]
    test["wf_spy_weight"] = test["wf_risk_on"] + 0.5 * test["wf_mixed"]
    # Match the archived comparator convention: the initial allocation is the
    # starting portfolio, so turnover costs begin with the first rebalance.
    previous_weight = test["wf_spy_weight"].shift(1, fill_value=float(test["wf_spy_weight"].iloc[0]))
    test["wf_turnover"] = (test["wf_spy_weight"] - previous_weight).abs()
    test["wf_strategy_return"] = (
        test["wf_spy_weight"] * test["portfolio_spy_return"]
        + (1.0 - test["wf_spy_weight"]) * test["portfolio_safe_return"]
        - TRANSACTION_COST * test["wf_turnover"]
    )

    static_probabilities = test[["calibrated_risk_on", "calibrated_mixed", "calibrated_risk_off"]].to_numpy()
    labels = test["label"].to_numpy(dtype=int)
    result = {
        "schema_version": "belieflens-spy-sgov-walk-forward-v1",
        "status": "derived_prequential_analysis",
        "source_archive": str(SOURCE.relative_to(HERE)),
        "source_sha256": sha256(SOURCE),
        "source_artifacts_modified": False,
        "model_measurement_note": "Stored language probabilities are reused; no provider calls are made.",
        "design": {
            "initial_fit": "All 285 labelled measurements dated before 2026, after completion of the original frozen validation study.",
            "recalibration_frequency": "Weekly, at the first observed trading date of each ISO week.",
            "availability_rule": "A 2026 observation enters a later calibration vintage only when outcome_end is strictly earlier than the vintage deployment date.",
            "application_rule": "Every fitted vintage is applied only on or after its deployment date and never retrospectively.",
            "regularization_C": 1.0,
            "allocation_rule": "SPY weight = P(Risk-on) + 0.5 P(Mixed); residual weight in SGOV.",
            "transaction_cost": TRANSACTION_COST,
            "test_start": test["date"].min().date().isoformat(),
            "test_end": test["date"].max().date().isoformat(),
        },
        "counts": {
            "pre_2026_fit_records": int(len(historical)),
            "test_decisions": int(len(test)),
            "weekly_vintages": int(len(vintage_rows)),
            "final_matured_2026_records": int(vintage_rows[-1]["matured_2026_records"]),
        },
        "measurement_metrics": {
            "static_2018_2020_calibrator": measurement_metrics(static_probabilities, labels),
            "weekly_walk_forward_calibrator": measurement_metrics(probabilities, labels),
        },
        "portfolio_metrics": {
            "weekly_walk_forward_calibrated": portfolio_metrics(
                test["wf_strategy_return"].to_numpy(), test["portfolio_safe_return"].to_numpy()
            )
        },
        "limitations": [
            "This derived analysis does not alter or replace the original frozen measurement study.",
            "The initial deployment fit reuses all pre-2026 labelled observations after the original validation exercise; its metrics must not be reported as new untouched validation evidence.",
            "Stored outputs from a model version frozen before 2026 are reused rather than collecting contemporaneous daily provider observations.",
            "The allocation rule is illustrative and is not evidence of investment alpha unless it was fixed before inspecting the 2026 returns.",
        ],
        "vintages": vintage_rows,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    output_columns = [
        "date", "outcome_end", "scenario_id", "calibration_vintage", "external_regime",
        *FEATURES, *PROBABILITY_COLUMNS, "wf_spy_weight", "wf_turnover",
        "portfolio_spy_return", "portfolio_safe_return", "wf_strategy_return",
    ]
    test[output_columns].to_csv(OUT / "walk_forward_measurements.csv", index=False)
    (OUT / "walk_forward_result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(OUT), "counts": result["counts"], "measurement_metrics": result["measurement_metrics"], "portfolio_metrics": result["portfolio_metrics"]}, indent=2))


if __name__ == "__main__":
    main()
