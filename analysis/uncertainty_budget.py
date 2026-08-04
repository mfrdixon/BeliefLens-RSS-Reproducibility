"""Quantify the RSS uncertainty budget from frozen confirmatory archives.

No API calls are made. The primary decomposition is the exact Euclidean
variance identity in isometric log-ratio (ILR) coordinates. Calibration-sample
uncertainty and probability-interface defects are reported as auxiliary
diagnostics because they are not additional orthogonal terms in that identity.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
CONTROLLED = HERE.parent / "controlled"
STUDIES = {
    "GPT-4.1-mini-2025-04-14": CONTROLLED / "gpt-4.1-mini",
    "GPT-4o-mini-2024-07-18": CONTROLLED / "gpt-4.0-mini",
}
SEED = 20260714
BOOTSTRAPS = 2000
RIDGE = 0.05


def read_jsonl(path: Path) -> list[dict]:
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def alr(p: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    p = np.clip(np.asarray(p, float), eps, None)
    p /= p.sum(axis=-1, keepdims=True)
    return np.log(p[..., :-1] / p[..., [-1]])


def inverse_alr(z: np.ndarray) -> np.ndarray:
    z = np.asarray(z, float)
    logits = np.concatenate([z, np.zeros((*z.shape[:-1], 1))], axis=-1)
    logits -= logits.max(axis=-1, keepdims=True)
    p = np.exp(logits)
    return p / p.sum(axis=-1, keepdims=True)


def ilr(p: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Helmert ILR coordinates; squared Euclidean distance is Aitchison distance."""
    p = np.clip(np.asarray(p, float), eps, None)
    p /= p.sum(axis=-1, keepdims=True)
    clr = np.log(p) - np.log(p).mean(axis=-1, keepdims=True)
    k = p.shape[-1]
    basis = np.zeros((k, k - 1))
    for j in range(1, k):
        basis[:j, j - 1] = 1 / np.sqrt(j * (j + 1))
        basis[j, j - 1] = -j / np.sqrt(j * (j + 1))
    return clr @ basis


def solve_ridge(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    design = np.column_stack([x, np.ones(len(x))])
    gram = design.T @ design + np.diag([RIDGE] * x.shape[1] + [0.0])
    coef = np.linalg.pinv(gram) @ design.T @ y
    return coef[:-1].T, coef[-1]


def aggregate_raw(root: Path) -> list[dict]:
    rows = []
    for path in sorted(root.glob("seed-*/token_probability_results.jsonl")):
        flat = read_jsonl(path)
        groups: dict[tuple, list[dict]] = {}
        for row in flat:
            key = (row["scenario_id"], row["presentation_id"], int(row["repeat_id"]))
            groups.setdefault(key, []).append(row)
        for key, group in groups.items():
            rows.append({
                "scenario_id": key[0],
                "repeat_id": key[2],
                "token": np.asarray([r["normalized_probability"] for r in group], float),
                "reference": np.asarray(group[0]["reference_posterior"], float),
                "mass_defect": abs(1.0 - float(group[0]["observed_candidate_mass"])),
                "parser_difference": float(group[0]["distenum_crosscheck_error"] or 0.0),
            })
    return rows


def analyse(name: str, root: Path) -> dict:
    evaluated = read_jsonl(root / "analysis" / "test_results.jsonl")
    by_scenario: dict[str, list[dict]] = {}
    for row in evaluated:
        by_scenario.setdefault(row["scenario_id"], []).append(row)

    service_terms, stable_terms, total_terms = [], [], []
    for group in by_scenario.values():
        pred = ilr(np.asarray([r["token_implied_posterior"] for r in group]))
        truth = ilr(np.asarray(group[0]["reference_posterior"]))
        centre = pred.mean(axis=0)
        service_terms.extend(np.sum((pred - centre) ** 2, axis=1))
        stable = float(np.sum((centre - truth) ** 2))
        stable_terms.extend([stable] * len(group))
        total_terms.extend(np.sum((pred - truth) ** 2, axis=1))
    service = float(np.mean(service_terms))
    stable = float(np.mean(stable_terms))
    total = float(np.mean(total_terms))

    raw = aggregate_raw(root)
    parts = json.loads((root / "partitions.json").read_text())
    train_ids, test_ids = set(parts["train"]), set(parts["test"])
    train = [r for r in raw if r["scenario_id"] in train_ids]
    test = [r for r in raw if r["scenario_id"] in test_ids]
    x_train = np.asarray([alr(r["token"]) for r in train])
    y_train = np.asarray([alr(r["reference"]) for r in train])
    x_test = np.asarray([alr(r["token"]) for r in test])
    A, c = solve_ridge(x_train, y_train)
    full = ilr(inverse_alr(x_test @ A.T + c))

    clusters = np.asarray([r["scenario_id"] for r in train])
    unique = np.asarray(sorted(set(clusters)))
    rng = np.random.default_rng(SEED)
    calibration_mse = []
    for _ in range(BOOTSTRAPS):
        draw = rng.choice(unique, len(unique), replace=True)
        idx = np.concatenate([np.flatnonzero(clusters == sid) for sid in draw])
        Ab, cb = solve_ridge(x_train[idx], y_train[idx])
        boot = ilr(inverse_alr(x_test @ Ab.T + cb))
        calibration_mse.append(float(np.mean(np.sum((boot - full) ** 2, axis=1))))

    defects = np.asarray([r["mass_defect"] for r in raw])
    parser = np.asarray([r["parser_difference"] for r in raw])
    identity_error = abs(total - service - stable)
    return {
        "model": name,
        "test_scenarios": len(by_scenario),
        "repeats": len(evaluated),
        "total_aitchison_mse": total,
        "service_aitchison_mse": service,
        "service_share_percent": 100 * service / total,
        "stable_recovery_aitchison_mse": stable,
        "stable_share_percent": 100 * stable / total,
        "identity_roundoff": identity_error,
        "calibration_bootstrap_mse_mean": float(np.mean(calibration_mse)),
        "calibration_bootstrap_mse_q025": float(np.quantile(calibration_mse, 0.025)),
        "calibration_bootstrap_mse_q975": float(np.quantile(calibration_mse, 0.975)),
        "mean_probability_mass_defect": float(defects.mean()),
        "maximum_probability_mass_defect": float(defects.max()),
        "maximum_parser_crosscheck_difference": float(parser.max()),
        "bootstrap_replicates": BOOTSTRAPS,
        "semantic_map_error": None,
        "open_world_reference_error": None,
    }


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    results = [analyse(name, root) for name, root in STUDIES.items()]
    payload = {
        "schema_version": "belieflens-rss-uncertainty-budget-v1",
        "metric": "squared Aitchison distance (squared Euclidean distance in ILR coordinates)",
        "exact_identity": "total = within-scenario service variation + stable scenario-level recovery error",
        "calibration_note": "Bootstrap prediction variation is an auxiliary diagnostic nested within recovery uncertainty, not an additional orthogonal variance term.",
        "conditioning_scope": {
            "fixed_objects": ["semantic map", "reference experiment"],
            "sensitivity_dimensions": ["alternative ontology", "external validity"],
        },
        "results": results,
    }
    (HERE / "uncertainty_budget.json").write_text(json.dumps(payload, indent=2) + "\n")
    with (HERE / "uncertainty_budget.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
