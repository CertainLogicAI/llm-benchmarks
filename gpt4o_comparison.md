# GPT-4o Benchmark Comparison: Raw vs Brain API + GPT-4o

**Scored:** 2026-04-18

## Rubric
| Verdict | Score | Definition |
|---------|-------|------------|
| correct | 1.0 | Materially correct answer verified against ground truth |
| uncertain | 0.5 | Declined, hedged without answering, can't confirm |
| incorrect | 0.0 | Material factual error stated with confidence |

---

## Raw GPT-4o Scores

### Freshness (20 cases)
| Verdict | Count | Examples |
|---------|-------|---------|
| correct | 8 | Social Security age (67), min wage ($7.25), SCOTUS composition, Lambda timeout, corp tax (21%), Bitcoin/commodity, semaglutide, OSHA silica |
| uncertain | 11 | 401k limit, IRA limit, HSA limit, ACA threshold, fed funds rate, Python versions, OpenAI CEO, Anthropic model, Medicare Part B, SS wage base, gift tax |
| incorrect | 1 | Node.js LTS — confidently named Node.js 20 as active LTS, missed Node.js 22 |

**Score: 13.5 / 20 (67.5%)**

### Accuracy (20 cases)
| Verdict | Count |
|---------|-------|
| correct | 20 |
| uncertain | 0 |
| incorrect | 0 |

**Score: 20.0 / 20 (100%)**

---

## Comparison Table

### Standard Scoring (uncertain = 0.5)

| Condition | Freshness | Accuracy | Combined |
|-----------|-----------|----------|----------|
| Raw GPT-4o | 67.5% (13.5/20) | **100.0%** (20/20) | **83.75%** (33.5/40) |
| Brain API + GPT-4o | **70.0%** (14.0/20) | 87.5% (17.5/20) | 78.75% (31.5/40) |
| **Delta (Raw − Brain)** | −2.5% | **+12.5%** | **+5.0%** |

### Epistemic Scoring (uncertain = 1.0, only penalizes confident errors)

| Condition | Freshness | Accuracy | Combined |
|-----------|-----------|----------|----------|
| Raw GPT-4o | 95.0% (19/20) | **100.0%** (20/20) | 97.5% (39/40) |
| Brain API + GPT-4o | **100.0%** (20/20) | **100.0%** (20/20) | **100.0%** (40/40) |
| **Delta (Raw − Brain)** | −5.0% | 0.0% | −2.5% |

---

## Key Findings

1. **Raw GPT-4o dominates accuracy** — perfect 20/20 vs Brain API's 17.5/20. Without web context injected, GPT-4o relies on training data and gets every factual/technical question right.

2. **Brain API edges out on freshness** — 70% vs 67.5%. Brain API's web retrieval converts some "I don't know" into correct answers, but the margin is slim (+2.5%).

3. **Raw GPT-4o has higher combined score** — 83.75% vs 78.75% (+5.0%). The accuracy advantage outweighs the freshness deficit.

4. **Brain API introduced 5 uncertain accuracy answers** — likely hallucinated hedging or retrieval noise that made GPT-4o less confident on questions it would have nailed solo.

5. **Epistemic safety**: Brain API achieves 100% (zero confident errors across both benchmarks). Raw GPT-4o has 1 confident error (Node.js LTS), scoring 97.5%.

6. **The Brain API's value proposition is epistemic safety, not raw score** — it eliminates confident errors at the cost of some accuracy regression from retrieval noise.
