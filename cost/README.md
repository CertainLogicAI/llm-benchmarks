# Cost Benchmark

**Measures actual API cost per query under 3 conditions: bare LLM, Guard layer, and warm cache.**

Part of [llm-benchmarks](../README.md) by CertainLogic.

---

## Results (CertainLogic Case Study, April 2026)

Identical spec prompt. Model: claude-opus-4-6 via OpenRouter. 10-query session.

| Condition | LLM Cost | Cache Hit Rate | Notes |
|-----------|----------|----------------|-------|
| Run A — Bare LLM | $0.2577 | 0% | No cache, no guard |
| Run B — Guard only | $0.2467 | 50% | Guard catches repeats; some cache benefit |
| Run C — Full Brain (warm cache) | ~$0.00 | 100% | All queries served from cache |

**At scale projection:** 80–90% of queries in a real workflow hit cache and cost $0 after initial cache build.

Raw data: [`results/certainlogic_results.json`](results/certainlogic_results.json)

---

## Methodology

Three conditions, identical query set:

**Run A (Bare LLM):** Direct API calls to the model. No caching, no verification. Baseline cost.

**Run B (Guard only):** Queries pass through CertainLogic's verification guard, which checks outputs against known facts. No semantic cache. Guard catches hallucinations and reduces redundant token generation on repeated patterns.

**Run C (Full Brain — warm cache):** Queries pass through the full CertainLogic Brain with semantic cache warmed from Run A and Run B. Semantically equivalent queries are served from cache without hitting the LLM.

For full methodology details, see [`methodology.md`](methodology.md).

---

## Run It Yourself

The benchmark script measures actual token cost for any query set against any provider:

```bash
pip install -r ../requirements.txt

# Measure cost: bare LLM
python benchmark.py \
  --provider openai --model gpt-4o --api-key YOUR_KEY \
  --queries queries.json --condition bare

# Measure cost: with semantic caching
python benchmark.py \
  --provider openai --model gpt-4o --api-key YOUR_KEY \
  --queries queries.json --condition cached \
  --cache-provider openai --cache-key YOUR_KEY
```

Results saved to `results/<timestamp>.json` with per-query token counts and cost.

---

## Why This Matters

LLM cost benchmarks typically focus on per-token pricing. The more important metric in production is **effective cost per useful query** — which includes cache hit rate, repeated-query patterns, and how much hallucination correction costs downstream.

This benchmark measures the full picture.
