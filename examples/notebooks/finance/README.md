# BeliefLens finance examples

These notebooks demonstrate how language-derived probabilities over market commentary can be mapped to calibrated probabilities over the declared states **Risk-on**, **Mixed** and **Risk-off**, then evaluated separately in a stylized SPY/SGOV allocation exercise.

The example has two deliberately separated modes.

| Notebook | Purpose | Credentials | Provider cost |
|---|---|---:|---:|
| [`SPY_SGOV_public_reproduction.ipynb`](SPY_SGOV_public_reproduction.ipynb) | Inspect the frozen evidence, semantic map, diagnostics, calibrated decisions and comparative portfolio table | None | None |
| [`SPY_SGOV_authenticated_workflow.ipynb`](SPY_SGOV_authenticated_workflow.ipynb) | Construct a private benchmark using user-supplied evidence, estimate cost, approve new observations and retrieve an audit certificate | BeliefLens key and user-supplied provider key | Shown before approval |

## What the example establishes

The statistical task is recovery of a declared broad-equity state from point-in-time evidence. The notebooks report identification, held-out recovery, conformal coverage, prompt stability, entropy and channel-comparison diagnostics. The portfolio calculation is a secondary illustration: it does not redefine the estimand, validate a production strategy or guarantee future returns.

The frozen files in `data/offline_reproduction/` are included so the public notebook remains inspectable without credentials. They contain the minimal approved evidence records, row-level measurements, semantic-map description, market-price history and archived API result. They contain no credentials or private service state.

## Supplied benchmark CSV

[`data/offline_reproduction/inputs/SPY_SGOV_benchmark_example.csv`](data/offline_reproduction/inputs/SPY_SGOV_benchmark_example.csv) is a ready-to-use local benchmark containing 412 point-in-time broad-equity evidence records. It includes the three required fields—`source_id`, `evidence_text` and `reference_state`—plus decision date, target, horizon, frozen partition and point-in-time certification.

To use it in the authenticated notebook, set the path before starting Jupyter:

```bash
export BELIEFLENS_RECORDS_CSV="$(pwd)/examples/notebooks/finance/data/offline_reproduction/inputs/SPY_SGOV_benchmark_example.csv"
```

As of August 21, 2026, no public dataset named BeliefLens or BeliefBench is published on Hugging Face. The platform supports pinned Hugging Face datasets, and Financial PhraseBank is used in its integration examples, but it is a third-party dataset rather than the SPY/SGOV benchmark supplied here. A future Hugging Face release should be cited and pinned by immutable revision rather than referenced only by its mutable `main` branch.

## Build a benchmark in the curator interface

Users who prefer a guided interface can open the [BeliefLens benchmark curator](https://demo.belieflens.org/curator). The curator supports application and state definition, record collection, automated or manual review, frozen partitioning and export. Approved BeliefLens access is required.

After exporting the reviewed benchmark as CSV, point the authenticated notebook to it:

```bash
export BELIEFLENS_RECORDS_CSV="/absolute/path/to/exported_benchmark.csv"
```

The exported file must retain `source_id`, `evidence_text` and `reference_state`; preserve its provenance, review status, state definitions and frozen partition information with the experiment archive.

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

## Citation requirements

Use of these notebooks, their frozen measurements, experimental design, semantic map, figures or derived benchmark should cite:

> Dixon, M. (2026). *Calibrating Semantic Uncertainty from Observable Language-Model Probabilities*. Manuscript.

and:

> Dixon, M. (2026). *BeliefLens reproducibility archive for Calibrating Semantic Uncertainty from Observable Language-Model Probabilities* (Version 1.0.0) [Data set and software]. <https://github.com/mfrdixon/BeliefLens-RSS-Reproducibility>

Also report the repository commit hash and disclose changes to the evidence, ontology, prompt, model, calibration, decision rule or market data. Market data and model-provider outputs remain subject to their respective provider terms.

## Security boundary

Never commit API keys, Cloudflare credentials, raw confidential evidence or private audit archives. The public example is suitable only for reproducible research and demonstration. Confidential or regulated data require an appropriately contracted and controlled deployment.
