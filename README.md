# BeliefLens reproducibility archive

This public archive accompanies *Calibrating Semantic Uncertainty from Observable Language-Model Probabilities*. It contains frozen derived observations, experimental designs, analysis artifacts and worked notebooks. Exact computational reanalysis makes no external model calls.

## BeliefLens overview

BeliefLens is a statistical measurement and auditing framework for language-model uncertainty. It groups prespecified, meaning-equivalent verbal continuations into declared application states, calibrates the resulting language-derived probabilities against a reference distribution, and tests whether the measurement is sufficiently identifiable, stable and well calibrated for its stated use.

The framework distinguishes probabilities calculated from the model's language channel from numerical confidence printed in generated text. Its diagnostics include held-out recovery, uncertainty coverage, prompt-equivalence stability, incomplete expressed mass and reproducible provenance. BeliefLens measures a declared state distribution; it does not certify a downstream recommendation, trading strategy or future outcome.

## Citation requirements

If you use BeliefLens methodology, the semantic-map construction, experimental designs, archived results, figures, analysis code, financial examples or a derivative benchmark, cite both the accompanying paper and this reproducibility archive.

**Methodology citation**

> Dixon, M. (2026). *Calibrating Semantic Uncertainty from Observable Language-Model Probabilities*. Manuscript.

**Software and archive citation**

> Dixon, M. (2026). *BeliefLens reproducibility archive for Calibrating Semantic Uncertainty from Observable Language-Model Probabilities* (Version 1.0.0) [Data set and software]. <https://github.com/mfrdixon/BeliefLens-RSS-Reproducibility>

In publications, reports and presentations, identify the BeliefLens version or commit hash, model and model version, prompt-instrument version, benchmark partition, observation date and any changes to the state ontology or calibration procedure. Do not describe altered experiments as exact reproductions.

Machine-readable metadata are provided in [`CITATION.cff`](CITATION.cff). The preferred article citation will be updated when a journal DOI is assigned. Citation is part of responsible scholarly attribution and does not replace any applicable software, data-provider or third-party licence terms.

## Reproduction levels

The paper distinguishes two reproducibility tasks.

1. **Exact computational reanalysis** uses the archived probability observations and makes no provider calls. This is the appropriate route for checking the numerical decomposition and the frozen experimental records reported in the paper.
2. **New-observation replication** submits the frozen designs to a fitted language-model service. It requires provider credentials and the experimental software environment, incurs a cost, and may not reproduce the archived values exactly because the service can change.

## Contents

- `controlled/gpt-4.1-mini/` and `controlled/gpt-4o-mini/`: frozen designs, partitions, scenario records, conditional probability observations, held-out posterior estimates, prompt-perturbation results and analysis summaries for the two controlled posterior-recovery studies.
- `professional_text/`: the frozen semantic-reference protocol and derived professional-text measurement records used for the channel comparison, where available without credentials or application state.
- `analysis/`: the uncertainty-decomposition program and its frozen CSV and JSON outputs.
- `figures/`: the plotted data products included in the manuscript.
- `examples/notebooks/finance/SPY_SGOV_public_reproduction.ipynb`: keyless, non-configurable reproduction of the frozen SPY/SGOV semantic-state and portfolio example. It makes no provider calls and falls back transparently to the archived API response when the public demonstration route is unavailable.
- `examples/notebooks/finance/SPY_SGOV_authenticated_workflow.ipynb`: separate configurable workflow for user-supplied evidence. It requires a [BeliefLens API key](https://demo.belieflens.org/signup) and a user-supplied model-provider key, presents a cost estimate before execution and preserves the resulting audit certificate.
- `examples/notebooks/finance/data/offline_reproduction/`: immutable inputs, measurements, fitted semantic-map artifact, diagnostics and expected outputs used by the finance notebooks.
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

## Finance notebooks

Start with the public notebook to inspect the frozen SPY/SGOV example without credentials or external model calls. Install the packages in `examples/notebooks/finance/requirements.txt`, then open:

```text
examples/notebooks/finance/SPY_SGOV_public_reproduction.ipynb
```

The authenticated companion is deliberately separate. Use it only when constructing a new private benchmark or collecting new model observations. Request access at <https://demo.belieflens.org/signup>, configure credentials as environment variables, inspect the returned cost estimate, and explicitly approve execution. Neither notebook requires Uvicorn; that package is needed only to run the complete BeliefLens backend locally. Never save credentials in a notebook.

## Integrity check

On macOS:

```bash
shasum -a 256 -c SHA256SUMS
```

On systems providing GNU coreutils:

```bash
sha256sum -c SHA256SUMS
```
