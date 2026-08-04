# Reproducibility supplement

This reviewer archive accompanies *Calibrating Semantic Uncertainty from Observable Language-Model Probabilities*. It contains frozen derived observations and analysis artifacts; it makes no external model calls.

## Citation

If you use the archived results, experimental design, semantic measurement construction or analysis code, please cite the paper:

> Dixon, M. (2026). *Calibrating Semantic Uncertainty from Observable Language-Model Probabilities*. Manuscript.

Machine-readable citation metadata are provided in `CITATION.cff`. The citation will be updated with the journal DOI when one is assigned.

## Reproduction levels

The paper distinguishes two reproducibility tasks.

1. **Exact computational reanalysis** uses the archived probability observations and makes no provider calls. This is the appropriate route for checking the numerical decomposition and the frozen experimental records reported in the paper.
2. **New-observation replication** submits the frozen designs to a fitted language-model service. It requires provider credentials and the experimental software environment, incurs a cost, and may not reproduce the archived values exactly because the service can change.

## Contents

- `controlled/gpt-4.1-mini/` and `controlled/gpt-4o-mini/`: frozen designs, partitions, scenario records, conditional probability observations, held-out posterior estimates, prompt-perturbation results and analysis summaries for the two controlled posterior-recovery studies.
- `professional_text/`: the frozen semantic-reference protocol and derived professional-text measurement records used for the channel comparison, where available without credentials or application state.
- `analysis/`: the uncertainty-decomposition program and its frozen CSV and JSON outputs.
- `figures/`: the plotted data products included in the manuscript.
- `SHA256SUMS`: integrity hashes for the archived files.

Repeated observations are grouped by scenario. The archive preserves the original calibration, validation, conformal-calibration and untouched-test assignments. Files containing provider credentials, browser state, local database state or raw request logs are deliberately excluded.

The numerical results reproduce the archived language-model observations. Re-running an external fitted language-model service is a statistical replication rather than an exact reproduction because service weights and infrastructure may change.

## Quick start: exact reanalysis

From the extracted supplement root, run:

```bash
shasum -a 256 -c SHA256SUMS
python analysis/uncertainty_budget.py
```

The script requires Python 3 and NumPy and reads the two controlled-study directories included in this archive. The frozen `uncertainty_budget.csv` and `uncertainty_budget.json` permit direct verification without new provider calls.

The principal frozen results can also be inspected directly:

- `controlled/*/analysis/summary.json`: confirmatory recovery and coverage summaries;
- `controlled/*/analysis/test_results.jsonl`: untouched scenario-level posterior estimates;
- `controlled/*/robustness/observability_bootstrap.json`: smallest-singular-value bootstrap assessment;
- `controlled/*/robustness/prompt-study/summary.json`: prompt-equivalence and ablation assessment;
- `controlled/*/robustness/perturbation-extension/summary.json`: irrelevant and contradictory-evidence perturbations; and
- `professional_text/pilot_measurement_channels.jsonl`: archived language-derived and printed-confidence channel observations.

## Optional new-observation replication

The frozen design for each model is stored in `controlled/<model>/design.json`, with its partitions and semantic definitions beside it. A replication should preserve these files, the model identifier, deterministic sampling settings, five repeats per scenario and scenario-level partitioning. It should write results to a new directory rather than overwrite the archive. Provider credentials must be supplied through the provider's normal secret-management mechanism and must never be written into this supplement.

Because the archive is deliberately credential-free and does not bundle a proprietary service client, it does not initiate new provider calls. Such a run is a new statistical replication. The exact peer-review reproduction is the archived-observation analysis above.

## Integrity check

On macOS:

```bash
shasum -a 256 -c SHA256SUMS
```

On systems providing GNU coreutils:

```bash
sha256sum -c SHA256SUMS
```
