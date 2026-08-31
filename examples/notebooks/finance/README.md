# BeliefLens finance examples

These notebooks demonstrate how language-derived probabilities over market commentary can be mapped to calibrated probabilities over the declared states **Risk-on**, **Mixed** and **Risk-off**, then evaluated separately in a stylized SPY/SGOV allocation exercise.

The example has two deliberately separated modes.

| Notebook | Purpose | Credentials | Provider cost |
|---|---|---:|---:|
| [`SPY_SGOV_public_reproduction.ipynb`](SPY_SGOV_public_reproduction.ipynb) | Inspect the frozen evidence, semantic map, diagnostics, calibrated decisions and comparative portfolio table | None | None |
| [`SPY_SGOV_authenticated_workflow.ipynb`](SPY_SGOV_authenticated_workflow.ipynb) | Construct a private benchmark using user-supplied evidence, estimate cost, approve new observations and retrieve an audit certificate | BeliefLens key and user-supplied provider key | Shown before approval |
| [`BeliefLens_LangChain_measurement.ipynb`](BeliefLens_LangChain_measurement.ipynb) | Load the frozen JSON calibration map and apply it locally as a LangChain/LangGraph node | None | None |
| [`Stochastic_Semantic_Evidence_Graphs.ipynb`](Stochastic_Semantic_Evidence_Graphs.ipynb) | Inspect a provider-call-free semantic evidence-graph demonstration and learn the graph-backed API/certificate flow | None for the frozen example | None |

## What the example establishes

The statistical task is recovery of a declared broad-equity state from point-in-time evidence. The notebooks report identification, held-out recovery, conformal coverage, prompt stability, entropy and channel-comparison diagnostics. The portfolio calculation is a secondary illustration: it does not redefine the estimand, validate a production strategy or guarantee future returns.

## Semantic evidence graphs

BeliefLens represents an AI workflow as auditable channels: source evidence, retrieved evidence, prompt and model response, semantic state and qualified decision input. It tests whether retrieval support is sufficient for the declared task, whether equivalent prompt changes preserve the semantic state, and whether the terminal probability remains calibrated and covered on held-out data. The resulting certificate is conditional on the frozen benchmark, ontology, service version and error tolerances; it supports pass, analyst-review or abstention decisions rather than a blanket safety claim.

Open [`Stochastic_Semantic_Evidence_Graphs.ipynb`](Stochastic_Semantic_Evidence_Graphs.ipynb) for the keyless walkthrough. The authenticated workflow uses the hosted API to build and freeze the required evidence, prompt and partition records. The server-side API guide is available at [Stochastic Semantic Evidence Graphs](https://github.com/mfrdixon/BeliefBench-Server/blob/main/docs/STOCHASTIC_SEMANTIC_EVIDENCE_GRAPHS.md).

The illustrative strategy is deliberately transparent. Each day it sets the SPY weight to `P(Risk-on) + 0.5 × P(Mixed)` and invests the remainder in SGOV; the next trading session's total returns are then recorded. A pure Risk-on distribution therefore gives 100% SPY, a pure Mixed distribution gives 50/50, and a pure Risk-off distribution gives 100% SGOV. The strategy is long-only and fully invested, with five basis points charged on each absolute change in SPY weight.

The public notebook now distinguishes the original frozen transport experiment from a recent deployment study. The latter constructs a new 2025 measurement channel using 122 January–June calibration sessions, 64 July–September prompt-validation sessions and 64 October–December conformal sessions. During the 2026 evaluation, the complete 250-session window rolls weekly: all three boundaries move forward, and every observation used in fitting precedes deployment. The derived files live under `data/derived/rolling_v5`; no earlier frozen measurement archive is overwritten. Because the provider did not expose every candidate among its returned top alternatives, the rolling estimator explicitly includes candidate-missingness and residual-mass information rather than silently declaring missing probabilities to be zero.

The frozen files in `data/offline_reproduction/` are included so the public notebook remains inspectable without credentials. They contain the minimal approved evidence records, row-level measurements, semantic-map description, market-price history and archived API result. They contain no credentials or private service state.

## Supplied benchmark package

The benchmark is a two-file package:

- [`SPY_SGOV_benchmark_manifest.json`](data/offline_reproduction/inputs/SPY_SGOV_benchmark_manifest.json) is the authoritative, versioned specification. It defines the target estimand, state ontology, residual category, frozen partitions, field types, provenance, validation rules and CSV integrity hash.
- [`SPY_SGOV_benchmark_example.csv`](data/offline_reproduction/inputs/SPY_SGOV_benchmark_example.csv) contains the 412 point-in-time evidence records. It may use only the state values declared by the manifest and cannot redefine the ontology.

This linked-manifest design keeps the metadata machine-readable without duplicating a moderately sized tabular dataset inside JSON. A portable single-file export may embed the same records under a `records` field, but the ontology and validation rules must remain identical and authoritative.

To use it in the authenticated notebook, set the path before starting Jupyter:

```bash
export BELIEFLENS_RECORDS_CSV="$(pwd)/examples/notebooks/finance/data/offline_reproduction/inputs/SPY_SGOV_benchmark_example.csv"
```

As of August 21, 2026, no public dataset named BeliefLens or BeliefBench is published on Hugging Face. The platform supports pinned Hugging Face datasets, and Financial PhraseBank is used in its integration examples, but it is a third-party dataset rather than the SPY/SGOV benchmark supplied here. A future Hugging Face release should be cited and pinned by immutable revision rather than referenced only by its mutable `main` branch; its dataset card should reproduce this manifest.

## Build a benchmark in the curator interface

Users who prefer a guided interface can open the [BeliefLens benchmark curator](https://demo.belieflens.org/curator). The curator supports application and state definition, record collection, automated or manual review, frozen partitioning and export. Approved BeliefLens access is required.

The preferred curator export is a benchmark manifest plus its referenced CSV. After export, verify that the records conform to the manifest ontology, then point the authenticated notebook to the CSV:

```bash
export BELIEFLENS_RECORDS_CSV="/absolute/path/to/exported_benchmark.csv"
```

The exported package must retain `source_id`, `evidence_text` and `reference_state`. The manifest—not values inferred from the CSV—determines the allowed states and their meanings. Preserve its provenance, review status, ontology version and frozen partition information with the experiment archive.

## Run the public notebook

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r examples/notebooks/finance/requirements.txt
python -m jupyter lab examples/notebooks/finance/SPY_SGOV_public_reproduction.ipynb
```

If you already have a suitable Python environment, activate it and skip the `venv` command. Neither notebook requires Uvicorn; Uvicorn is needed only to operate a complete BeliefLens backend locally.

The public notebook attempts the immutable hosted demonstration and automatically uses the archived copy of the same result if that route is unavailable. It makes no model-provider call.

## Run a configurable experiment

Request BeliefLens access at <https://demo.belieflens.org/signup>. Configure secrets in the shell that starts Jupyter; do not write them into the notebook:

```bash
export BELIEFLENS_API_KEY="your-key"
export OPENAI_API_KEY="your-provider-key"
python -m jupyter lab examples/notebooks/finance/SPY_SGOV_authenticated_workflow.ipynb
```

The configurable notebook expects a CSV containing at least:

- `evidence_text`;
- `source_id`; and
- `reference_state`.

Recommended provenance includes the evidence observation time, retrieval time, target, horizon, source, review status and point-in-time availability. The notebook separates specification, upload, frozen partitions, prompt registration, cost estimation, explicit execution approval, results and downstream strategy evaluation. Only the explicitly approved model-observation job incurs provider charges.

## Reproducibility and look-ahead control

- Treat each prompt as a versioned statistical instrument.
- Freeze the state ontology, verbalizers, partitions and calibration procedure before viewing untouched-test results.
- Use only evidence available at the recorded decision time.
- Align returns strictly after the observation time.
- Preserve the returned certificate, model identifier, prompt version and data vintage.
- Report transaction costs, turnover assumptions and any mapping from state probabilities to portfolio weights separately.
- A new provider run is a replication, not an exact reproduction, because fitted services can change.

## Uncertainty attribution

The public notebook calls the immutable, keyless [`GET /v1/examples/SPY-trading/attributions`](https://demo.belieflens.org/v1/examples/SPY-trading/attributions) route and falls back to the archived [`attribution_result.json`](data/offline_reproduction/attribution_result.json). The authenticated notebook uses `POST /v1/attributions/analyze` on stored private-run measurements. Both routes perform retrospective analysis and make no model-provider calls.

The notebooks visualize prompt-presentation instability and the contribution of each declared semantic state to uncertainty and held-out recovery error. Internal response encodings are deliberately hidden from user-facing reports because they are measurement-device details rather than financial-language explanations. These diagnostics do not claim that particular words in the evidence caused the result; evidence-word attribution requires a separate controlled span-perturbation experiment.

## OpenTelemetry and LangChain

BeliefLens emits W3C trace context and OTLP spans. OTLP is the transport layer; storage and visualization remain external. The same instrumented service can send traces to Jaeger, Grafana Tempo, Datadog, LangSmith or an OpenTelemetry Collector by changing configuration rather than analysis code:

```text
BELIEFLENS_OTEL_ENABLED=true
OTEL_SERVICE_NAME=belieflens-service
OTEL_EXPORTER_OTLP_ENDPOINT=<backend OTLP HTTP endpoint>
OTEL_EXPORTER_OTLP_HEADERS=<backend authentication headers, if required>
```

`GET /v1/health` reports whether telemetry is enabled and configured. Every instrumented response carries `X-BeliefLens-Trace-Id`, which can be searched in the selected backend. Raw evidence, prompts and generated text are not exported by default.

The standalone LangChain driver makes no hosted request. It loads the content-hashed JSON calibration map, applies the declared additive-log-ratio transformation and frozen multinomial coefficients through a local `RunnableLambda`, and routes the resulting calibrated state distribution. The archived language-probability vector makes the example deterministic: no BeliefLens key, provider key or hosted CPU capacity is required. A production workflow can place a provider-specific probability-observation node upstream and choose managed BeliefLens services separately when centralized profiles, audit logs or server-issued certificates are required.

## Citation requirements

Use of these notebooks, their frozen measurements, experimental design, semantic map, figures or derived benchmark should cite:

> Dixon, M. (2026). *Calibrating Semantic Uncertainty from Observable Language-Model Probabilities*. Manuscript.

and:

> Dixon, M. (2026). *BeliefLens reproducibility archive for Calibrating Semantic Uncertainty from Observable Language-Model Probabilities* (Version 1.0.0) [Data set and software]. <https://github.com/mfrdixon/BeliefLens-RSS-Reproducibility>

Also report the repository commit hash and disclose changes to the evidence, ontology, prompt, model, calibration, decision rule or market data. Market data and model-provider outputs remain subject to their respective provider terms.

## Security boundary

Never commit API keys, Cloudflare credentials, raw confidential evidence or private audit archives. The public example is suitable only for reproducible research and demonstration. Confidential or regulated data require an appropriately contracted and controlled deployment.
