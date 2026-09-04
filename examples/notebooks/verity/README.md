# Verity public API example

Open [`Verity_public_API.ipynb`](Verity_public_API.ipynb) for a guided,
keyless walkthrough of Verity, powered by the BeliefLens analytics engine.

The notebook includes `credit_market_timeseries.csv`, a compact initial-release
ALFRED example covering Baa and Aaa credit spreads and the NFCI credit subindex.
It validates and plots the CSV, converts the dated observations into a bounded
evidence passage, and asks whether credit stress rose and remained above its
starting level. The genuine sanitized response in `sample_verity_result.json`
is bundled with the notebook, so no quota is consumed unless `RUN_LIVE` is
deliberately changed to `True`.

The remaining sections demonstrate response processing, claim/source tables,
diagnostic charts, the source-preserving stochastic semantic evidence graph,
LangChain/LangGraph use, and protected OpenTelemetry/Jaeger trace lookup.

Read the [API guide](../../../../docs/PUBLIC_VERITY_API.md) and the
[SSEG preprint](https://belieflens.org/assets/belieflens-stochastic-evidence-graphs-preprint.pdf)
for further detail.
