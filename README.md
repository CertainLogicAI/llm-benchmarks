# LLM Accuracy, Freshness, and Latency Benchmark

Published April 18, 2026. Comparative study of 5 AI systems across 90 fact-based cases.

---

## Study Context

This study evaluates four large language models and one proprietary AI system — GPT-4o, Claude Opus 4, Claude Sonnet 4.5, Llama 3.3 70B, and CertainLogic Brain API — across five dimensions:

| Benchmark | Cases | What It Measures |
|-----------|-------|------------------|
| Hallucination | 30 | Factual errors across five domains |
| Freshness | 20 | Knowledge of annually-changing figures |
| Accuracy | 20 | Confident incorrect responses on established facts |
| Latency | 10 queries × 3 runs | Response time under different conditions |
| Cost | Documented case study | Token cost under three conditions |

**Systems tested:**
- openai/gpt-4o (knowledge cutoff: October 2023)
- anthropic/claude-opus-4 (knowledge cutoff: April 2024)
- anthropic/claude-sonnet-4.5 (knowledge cutoff: April 2024)
- meta-llama/llama-3.3-70b-instruct (knowledge cutoff: early 2023)
- certainlogic/brain-api (proprietary system, April 2026 run)

---

## Key Results

### Hallucination (30 cases)

| System | Overall |
|--------|---------|
| Llama 3.3 70B | 68% |
| GPT-4o | 74% |
| Claude Sonnet 4.5 | 78% |
| Claude Opus 4 | ~100% |
| Brain API | 100% |

### Freshness (20 cases — annually changing facts)

| System | Score | Pass Rate | Notes |
|--------|-------|-----------|-------|
| GPT-4o | 8.5/20 | 43% | Oct 2023 cutoff |
| Llama 3.3 70B | 8.5/20 | 43% | Early 2023 cutoff |
| **Brain API** | **15.5/20** | **78%** | 2 prior-year errors |
| Claude Sonnet 4.5 | 17.5/20 | 88% | April 2024 cutoff |
| Claude Opus 4 | 18/20 | 90% | April 2024 cutoff |

**Important note:** All systems failed on the federal funds rate question — no model had a knowledge cutoff capturing late-2024 rate cuts. Brain API had "off-by-one-year" errors on Social Security wage base and gift tax exclusion.

### Accuracy (20 cases)

| System | Score | Pass Rate |
|--------|-------|-----------|
| Llama 3.3 70B | 17.5/20 | 88% |
| GPT-4o | 18/20 | 90% |
| **Brain API** | **18/20** | **90%** |
| Claude Sonnet 4.5 | 19.5/20 | 98% |
| Claude Opus 4 | 20/20 | 100% |

### Latency

| Condition | Median Latency |
|-----------|---------------|
| Bare LLM (Llama 3.3 70B) | 55 ms |
| Brain API — fast path | 944 ms |
| Brain API — standard path | 2,382 ms |

The Brain API is ~17× slower (fast path) and ~43× slower (standard path) than a bare LLM. This reflects the additional verification processing it performs.

### Cost (documented case study)

| Condition | Cost per 10-query session |
|-----------|--------------------------|
| Bare LLM (Claude Opus 4) | $0.257 |
| With Guard layer | $0.246 |
| Full Brain (warm cache) | ~$0.00 |

Cache hit rate: 80–90% at steady state. These figures reflect a single documented session.

---

## Important Caveats

1. **Brain API is proprietary.** Its results cannot be independently reproduced without API access. Architecture and verification methods are not published.

2. **Single-session study.** All results are from one execution on April 17, 2026. Not replicated across multiple dates or conditions.

3. **Freshness is genuinely hard.** All systems had at least one failure on annually-changing figures. The "off-by-one-year" error (citing prior year's figure as current) appeared across multiple systems.

4. **Epistemic scoring is interpretive.** Traditional scoring (correct=1, uncertain=0.5, wrong=0) and epistemic scoring (correct=1, uncertain=1, wrong=0) produce different rankings. Neither is "correct" — they reflect different values about safety vs informativeness.

5. **Latency-cost tradeoff is real.** Brain API adds verification overhead. Whether 43x slower is worth it depends on whether incorrect answers carry downstream consequences.

---

## Reproducing Results

### Against bare LLMs
```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY=your_key
python run_benchmarks.py
```

### Against CertainLogic Brain API
Get a free API key at https://api.certainlogic.ai/signup

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

## Conflict of Interest

The CertainLogic Brain API is developed by the authors. All test cases, answers, scoring criteria, and raw data are included for independent verification of bare-LLM results.

## License

Business Source License 1.1 (BSL 1.1) — broad grant. See LICENSE.

---

*CertainLogic Research | Published April 18, 2026*
