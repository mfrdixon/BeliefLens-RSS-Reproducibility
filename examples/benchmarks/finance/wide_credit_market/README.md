# Broad US Credit-Market Distress Benchmark

This provisional benchmark extends the semantic-measurement experiment to a broad indication of current US credit-market distress. It is deliberately separate from the frozen broad-equity benchmark and does not alter its records, ontology, calibration, or results.

## Measurement target

The target is the **current broad US credit-market distress state**, not an issuer default probability, expected loss, recession probability, portfolio recommendation, or return forecast. The ordered states are:

1. **Normal** — credit pricing, liquidity, availability, and traded-credit behavior are broadly benign.
2. **Elevated** — meaningful deterioration is present but is not broadly stressed.
3. **Stressed** — deterioration is broad or pronounced across several channels.
4. **Severe** — conditions are exceptionally impaired relative to the walk-forward historical record.

`Unclear` is retained as a language-measurement residual and is not a benchmark reference state.

## Why the reference is not one-hot

The benchmark includes a categorical response for classification diagnostics and a constructed soft reference distribution for calibration research. The soft distribution is induced by a prespecified ordinal score; it is **not** claimed to be the market's latent true posterior.

For each weekly observation, indicators are transformed into expanding historical percentiles using only past-and-current values. Three group components receive equal weight:

- public spreads: Baa–Treasury and Baa–Aaa quality dispersion;
- traded credit: HYG/LQD relative return, LQD/SHY relative return, HYG drawdown, and HYG volatility;
- systemic credit conditions: the Federal Reserve credit subindex and the St. Louis Fed financial-stress index.

The distress score is

`D = (public-spread component + traded-credit component + systemic-credit component) / 3`.

Thresholds at `0.50`, `0.75`, and `0.90` define the ordered regions. Ordered logistic transitions with fixed softness `0.055` convert `D` into probabilities over Normal, Elevated, Stressed, and Severe. The categorical reference is the modal state of that distribution.

SLOOS lending standards and business-loan delinquencies are included in the textual evidence after a conservative 45-day lag, but they do not determine the reference score.

## Files

- `build_wide_credit_benchmark.py` — deterministic, zero-model-call builder.
- `wide_credit_market_benchmark.csv` — generated weekly evidence and references.
- `wide_credit_market_benchmark_manifest.json` — authoritative ontology, score construction, partitions, provenance, and integrity digest.
- `source_cache/` — FRED downloads used for this local research build.

## Status and limitations

Version `0.1.0` is a **provisional research candidate**, not a frozen benchmark. Market observations are archived, but the downloaded FRED histories are not yet verified observation-by-observation against archival vintages. Consequently, `point_in_time_certified` is false. Before freezing:

1. verify release-vintage availability and exact publication lags;
2. review data redistribution and source-license conditions;
3. obtain independent review of the ontology, indicator directions, weights, thresholds, and smoothing;
4. freeze the state-stratified measurement partitions, recent-period temporal holdout, and integrity hashes;
5. only then collect calibration and untouched-test language measurements.

Run from the reproducibility repository:

```bash
python examples/benchmarks/finance/wide_credit_market/build_wide_credit_benchmark.py
```
