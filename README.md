# LLM Accuracy, Freshness, and Latency Benchmark

Published April 18, 2026. Comparative study across 90 fact-based cases.

> ⚠️ **Conflict of Interest:** CertainLogic Brain API is developed by the authors of this benchmark. All Brain API results are proprietary and reserved for NDA review. The public results below are limited to independently reproducible bare-LLM runs.

---

## Study Context

This study evaluates four large language models — GPT-4o, Claude Opus 4, Claude Sonnet 4.5, and Llama 3.3 70B — across five dimensions:

| Benchmark | Cases | What It Measures |
|-----------|-------|------------------|
| Hallucination | 30 | Factual errors across five domains |
| Freshness | 20 | Knowledge of annually-changing figures |
| Accuracy | 20 | Confident incorrect responses on established facts |
| Latency | 10 queries × 3 runs | Response time under different conditions |
| Cost | Documented case study | Token cost under three conditions |

**Bare-LLM systems tested (independently reproducible):**
- openai/gpt-4o (knowledge cutoff: October 2023)
- anthropic/claude-opus-4 (knowledge cutoff: April 2024)
- anthropic/claude-sonnet-4.5 (knowledge cutoff: April 2024)
- meta-llama/llama-3.3-70b-instruct (knowledge cutoff: early 2023)

**Proprietary system also tested (NDA-only):**
- certainlogic/brain-api (proprietary, April 2026 internal run)

---

## Key Results — Public (Bare LLMs)

### Hallucination (30 cases)

| System | Overall |
|--------|---------|
| Llama 3.3 70B | 68% |
| GPT-4o | 74% |
| Claude Sonnet 4.5 | 78% |
| Claude Opus 4 | ~100% |

### Freshness (20 cases — annually changing facts)

| System | Score | Pass Rate | Notes |
|--------|-------|-----------|-------|
| GPT-4o | 8.5/20 | 43% | Oct 2023 cutoff |
| Llama 3.3 70B | 8.5/20 | 43% | Early 2023 cutoff |
| Claude Sonnet 4.5 | 17.5/20 | 88% | April 2024 cutoff |
| Claude Opus 4 | 18/20 | 90% | April 2024 cutoff |

**Important note:** All systems failed on the federal funds rate question — no model had a knowledge cutoff capturing late-2024 rate cuts.

### Accuracy (20 cases)

| System | Score | Pass Rate |
|--------|-------|-----------|
| Llama 3.3 70B | 17.5/20 | 88% |
| GPT-4o | 18/20 | 90% |
| Claude Sonnet 4.5 | 19.5/20 | 98% |
| Claude Opus 4 | 20/20 | 100% |

### Latency

| Condition | Median Latency |
|-----------|---------------|
| Bare LLM (Llama 3.3 70B) | 55 ms |
| GPT-4o | ~TBD |
| Claude Sonnet 4.5 | ~TBD |
| Claude Opus 4 | ~TBD |

Note: Comprehensive latency figures for other bare LLMs available via reproduction with your own API keys.

---

## NDA-Only Results

CertainLogic Brain API was evaluated on the same benchmarks during an April 2026 internal run. Results (hallucination, freshness, accuracy, latency, cost) and methodology are proprietary — not independently verifiable without NDA. Contact anton@certainlogic.ai for NDA access.

Key known caveats (apply to all systems):
- All systems failed on federal funds rate question (post-2024 cutoffs)
- Freshness "off-by-one-year" errors appear across multiple systems
- This is a single-session study, not replicated

---

## Reproducing Results

### Against bare LLMs
```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY=your_key
python run_benchmarks.py
```

All test cases, answers, scoring criteria, and raw data are included for independent verification of bare-LLM results.

### Against CertainLogic Brain API
Get a free API key at https://certainlogic.ai

```bash
export BRAIN_API_KEY=your_cl_live_key
python run_brain_benchmark.py
```

## Structure

```
freshness/
  cases/freshness.json      — 20 test cases
  results/                  — scored results
accuracy/
  cases/accuracy.json       — 20 test cases
  results/
stress_test/
  cases/stress_test.json    — 20 harder cases
  results/
run_benchmarks.py           — runs bare LLMs via OpenRouter
run_brain_benchmark.py      — runs Brain API
```

## License

Business Source License 1.1 (BSL 1.1) — broad grant. See LICENSE.

---

*CertainLogic Research | Published April 18, 2026*