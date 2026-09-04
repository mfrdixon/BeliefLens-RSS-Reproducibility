# Verity public API example

Open [`Verity_public_API.ipynb`](Verity_public_API.ipynb) for a guided,
keyless walkthrough of Verity, powered by the BeliefLens analytics engine.

The notebook includes a genuine sanitized response in
`sample_verity_result.json`; it does not consume quota unless `RUN_LIVE` is
deliberately changed to `True`. It demonstrates direct HTTP use, response
processing, claim/source tables, diagnostic charts, the source-preserving
stochastic semantic evidence graph, LangChain/LangGraph use, and protected
OpenTelemetry/Jaeger trace lookup.

Read the [API guide](../../../../docs/PUBLIC_VERITY_API.md) and the
[SSEG preprint](https://belieflens.org/assets/belieflens-stochastic-evidence-graphs-preprint.pdf)
for further detail.
