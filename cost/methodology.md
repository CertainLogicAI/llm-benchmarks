# Cost Benchmark Methodology

## Setup

- **Model:** claude-opus-4-6 via OpenRouter
- **Task:** Generate a Task Manager REST API (FastAPI + SQLAlchemy 2.0 + Pydantic v2)
- **Query set:** Identical spec prompt across all 3 conditions
- **Date:** April 14, 2026

## Three Conditions

### Condition A: Bare LLM
Direct API calls. No preprocessing, no verification, no caching. Cost reflects raw LLM usage with zero optimization.

### Condition B: Guard only
Queries routed through CertainLogic's hallucination guard. The guard:
1. Checks model outputs against known facts before returning
2. Flags and corrects hallucinations
3. Has a basic pattern cache — duplicate queries within the session return cached responses

Result: 50% cache hit rate in the test session (validation queries repeated with minor variations).

### Condition C: Full Brain (warm cache)
Queries routed through the full CertainLogic Brain with semantic cache pre-warmed from Conditions A and B. The semantic cache:
1. Embeds each query
2. Performs similarity search against cached query-response pairs
3. Returns cached response for semantically equivalent queries without LLM call

Result: 100% cache hit rate in the test session. All validation queries matched cached results.

## Cost Measurement

Costs are measured from API billing records, not estimated. Token counts are pulled from response metadata. Rates used:
- claude-opus-4-6 via OpenRouter: $15/M input tokens, $75/M output tokens (approximate 2026 rates)

## Projection Methodology

The 80–90% at-scale projection is based on:
- Typical code generation workflows have high query repetition (same patterns, same validations, similar prompts)
- Cache hit rate compounds: Run A = 0%, Run B = 50%, Run C = 100% on the same query set
- Production deployments across multiple users create a larger shared cache pool

This is a projection, not a measurement. It is presented as such.

## What We Don't Measure

- Quality degradation from cached responses (we assume semantic match implies quality match)
- Latency (cached responses are faster; not quantified here)
- Cache build cost (the initial warm-up queries have full LLM cost)
- Cost of the guard/Brain service itself (priced separately)
