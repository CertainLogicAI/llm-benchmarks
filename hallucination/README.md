# Hallucination Benchmark

**30 real hallucination test cases. Run them against any LLM.**

Part of [llm-benchmarks](../README.md) by CertainLogic.

---

## Results

| System | Medical | Legal | Financial | Technical | General | **Overall** |
|--------|---------|-------|-----------|-----------|---------|-------------|
| GPT-4o (bare) | 60% | 80% | 60% | 80% | 90% | **74%** |
| Claude 3.5 Sonnet (bare) | 80% | 80% | 60% | 80% | 90% | **78%** |
| Llama 3.3 70B (bare) | 60% | 60% | 60% | 80% | 80% | **68%** |
| **CertainLogic Brain** | **100%** | **100%** | **100%** | **100%** | **100%** | **100%** |

---

## Run It

```bash
pip install -r ../requirements.txt

# Test any model
python benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY

# With auto-scoring
python benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY \
  --evaluator-provider openai --evaluator-model gpt-4o --evaluator-key YOUR_KEY
```

---

## Categories

| Category | Cases | What We Test |
|----------|-------|-------------|
| 🏥 Medical (`medical.json`) | 5 | Drug dosages, interactions, diagnostic priorities, vaccine schedules |
| ⚖️ Legal (`legal.json`) | 5 | Statute of limitations, LLC liability, contract law, employment law |
| 💰 Financial (`financial.json`) | 5 | 401(k)/IRA limits, capital gains, Social Security age, Roth rules |
| 💻 Technical (`technical.json`) | 5 | Python EOL, API limits, SQL injection, dependency compatibility |
| 🌍 General (`general.json`) | 10 | Geography, history, science, company facts |

---

## Key Finding

The Social Security retirement age question (`fin-003`) fails across every bare LLM tested. All three models state **65** — the pre-1983 age that hasn't applied to anyone born after 1937. The correct answer is **67** for anyone born in 1960 or later.

This is a retirement planning question with real financial stakes. It's also one of the most consistent, reproducible hallucinations we've found.

---

See [METHODOLOGY.md](../METHODOLOGY.md) for scoring criteria.
