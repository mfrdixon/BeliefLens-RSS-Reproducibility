# Public Verity API

**Verity is powered by the BeliefLens analytics engine.**

Verity generates an evidence-bounded answer and measures where that answer is
sensitive to wording, evidence, and source attribution. The public API uses the
same analysis route as the browser demo.

Base URL: `https://demo.belieflens.org`

No API key is required for the public routes. The public service is intentionally
fixed and quota-limited. For private data, larger studies, configurable models,
or calibrated benchmark validation, request a BeliefLens workspace key at
<https://demo.belieflens.org/signup>.

## Analyze an answer

`POST /v1/seg/chat`

Web-grounded request:

```bash
curl -X POST https://demo.belieflens.org/v1/seg/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "What factors currently make US credit markets fragile?",
    "auto_retrieve": true,
    "evidence": []
  }'
```

Evidence-grounded request:

```json
{
  "prompt": "What changed in the policy stance?",
  "auto_retrieve": false,
  "evidence": [
    {
      "source_id": "fed-release",
      "title": "Federal Reserve release",
      "uri": "https://example.org/source",
      "passage": "The Committee raised the target range by 25 basis points."
    }
  ]
}
```

The response contains:

- `response`: generated answer;
- `spans`: phrase measurements, prompt perturbations, evidence-removal
  interventions, and source relations;
- `semantic_evidence_graph`: source-preserving evidence/claim graph;
- `gates`: individual governance diagnostics;
- `certificate`: aggregate conditional diagnostic and recommended action;
- `provenance_ranking`: sources ranked by measured influence;
- `trace_id`: request trace identifier;
- `public_budget`: conservative debit and remaining daily budget.

The probabilities and red/amber/green statuses are uncalibrated,
execution-specific diagnostics. They do not certify factual truth and should not
be interpreted as a reference posterior or regulatory approval.

## Fact-check a claim

`POST /v1/seg/fact-check`

```json
{
  "claim": "The Committee raised the target range by 25 basis points.",
  "evidence": [
    {
      "source_id": "fed-release",
      "title": "Federal Reserve release",
      "passage": "The Committee raised the target range by 25 basis points."
    }
  ],
  "retrieve_additional_sources": false,
  "exclude_uris": []
}
```

This route measures support, qualification, contradiction, and insufficient
evidence jointly and source-by-source. Setting `retrieve_additional_sources` to
`true` retrieves independent evidence and excludes URLs supplied in
`exclude_uris`.

## Quotas and safeguards

`GET /v1/seg/public-budget` reports the current UTC budget ledger.

Default public controls:

- 25 analyses per source IP per rolling hour;
- $3 conservative aggregate service debit per UTC day;
- $0.05 reserved per answer analysis and $0.02 per fact-check;
- at most three sources, 4,000 prompt characters, 160 answer tokens, eight
  analyzed phrases, and bounded provider calls;
- two concurrent analyses; excess traffic receives HTTP `429`;
- the budget is reserved before provider execution and persisted across restarts.

The administrator may lower these environment-configured limits. Clients should
respect `429`, inspect `Retry-After` when present, and avoid automatic retries.

## Python client

```python
from belieflens import Verity

verity = Verity()
result = verity.analyze(
    "What factors currently make US credit markets fragile?",
    auto_retrieve=True,
)
print(result["response"])
print(result["certificate"]["overall_status"])
print(result["trace_id"])
```

Install the local SDK from this repository:

```bash
pip install -e 'sdk/python[langchain]'
```

## LangChain and LangGraph

```python
from belieflens import Verity
from belieflens.integrations.langchain import VerityRunnable

node = VerityRunnable(client=Verity(), auto_retrieve=True)
result = node.invoke({"prompt": "What factors currently make US credit markets fragile?"})
```

`VerityRunnable` is an LCEL-compatible runnable and may be used as a LangGraph
node. It returns the complete Verity result so a later node can inspect individual
gates or apply a deliberately chosen action policy.

## OpenTelemetry and Jaeger

The service exports OpenTelemetry Protocol (OTLP) spans to its private Jaeger
collector. Each response includes `X-BeliefLens-Trace-Id` and, when configured,
`X-BeliefLens-Trace-Url`. The Python client copies these into `trace_id` and
`trace_url`.

The Jaeger interface at <https://traces.belieflens.org/> is
administrator-protected. This is deliberate: traces can reveal operational
metadata across users. Public callers can quote their trace ID when reporting a
problem, while authorized operators can open the corresponding trace. Prompt,
evidence, generated content, and credentials are not exported as trace attributes
by default.

The same instrumentation can target Grafana Tempo, Datadog, or another OTLP
backend by changing `OTEL_EXPORTER_OTLP_ENDPOINT`; the API contract is unchanged.
