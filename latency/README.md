# Latency Benchmark

**What's faster: Brain API or bare LLM? We measured. Bare LLM wins on speed. Here's what that trade looks like.**

---

## What We Measured

Response time (full round-trip, wall-clock ms) for 10 factual queries across two conditions:

1. **CertainLogic Brain API** — local instance at `127.0.0.1:8000`. Queries routed through structured knowledge lookup (facts cache) or LLM fallback with verification layer.
2. **Bare LLM via OpenRouter** — `meta-llama/llama-3.3-70b-instruct:free`. No cache, no verification. Raw model output.

## Methodology

- 10 queries: mix of common factual questions (some hit facts cache, some fall through to LLM)
- 3 runs per query per condition
- Median of 3 runs reported (reduces network noise)
- Brain API: localhost — no network hop beyond loopback
- Bare LLM: OpenRouter API — includes full internet round-trip

## Results

| Query | Brain API Method | Brain API (ms) | Bare LLM (ms) | Speed Ratio |
|-------|-----------------|---------------|---------------|-------------|
| Max acetaminophen dose for adults? | llm | 4,482 | 61 | LLM 73x faster |
| 2024 401k limit under 50? | llm | 6,802 | 56 | LLM 121x faster |
| SS full retirement age (born after 1960)? | llm | 1,964 | 50 | LLM 39x faster |
| FDIC insurance limit per depositor? | llm | 2,575 | 65 | LLM 40x faster |
| Federal minimum wage? | llm | 2,189 | 49 | LLM 45x faster |
| HTTP status code 418 meaning? | facts_cache | 1,049 | 54 | LLM 19x faster |
| Capital of Australia? | facts_cache | 944 | 47 | LLM 20x faster |
| Boiling point of water in Celsius? | facts_cache | 913 | 52 | LLM 18x faster |
| Justices on US Supreme Court? | llm | 1,580 | 50 | LLM 32x faster |
| Speed of light in m/s? | facts_cache | 904 | 62 | LLM 15x faster |

### Summary by category

| Condition | Median Latency | Queries |
|-----------|---------------|---------|
| Brain API — facts_cache hits | **944 ms** | 4 of 10 |
| Brain API — LLM fallback | **2,382 ms** | 6 of 10 |
| Bare LLM (OpenRouter) | **55 ms** | all 10 |

## Key Finding

**Bare LLM is faster.** That's not surprising — it's not doing anything beyond generating text. No structured knowledge lookup. No claim verification. No cache check.

Brain API cache hits come in at ~944ms. LLM fallback (cache miss → verification layer → model) runs 1.5–7 seconds. The bare LLM returns in ~55ms regardless.

**The latency cost buys accuracy.** On the same query set, Llama 3.3 70B (the bare LLM model used here) scored:
- 68% on the hallucination benchmark
- 43% on the freshness benchmark (stale training data)

Brain API scored 100% on hallucination and 78% on freshness.

For domains where wrong answers have consequences — medical dosing, tax limits, legal rules — 944ms is a reasonable cost. For speed-critical applications where answers don't require verification, bare LLM latency wins clearly.

Cache hit rate matters. At 80–90% cache coverage on a warm cache, the effective median drops to ~944ms for most queries. At cold cache or novel queries, fallback to 2–7s applies.

---

## Run It Yourself

```bash
python latency/benchmark.py \
  --brain-api-url http://127.0.0.1:8000 \
  --brain-api-key YOUR_BRAIN_KEY \
  --openrouter-key YOUR_OR_KEY \
  --runs 3
```

No Brain API account? Skip the `--brain-api-*` flags to measure bare LLM latency only.

Full results: [results/certainlogic_results.json](results/certainlogic_results.json)
