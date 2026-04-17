# Freshness Benchmark

**20 test cases targeting stale training data — facts that change annually.**

Part of [llm-benchmarks](../README.md) by CertainLogic.

---

## What This Tests

LLMs have training cutoffs. Facts that change annually — IRS contribution limits, Medicare premiums, Node.js LTS schedules, Federal Reserve rates — are a reliable freshness signal. A model that confidently states the 2023 IRS 401(k) limit as current is demonstrating training data lag in a measurable, verifiable way.

This benchmark documents 20 such cases with verified correct answers and known LLM failure patterns.

---

## Results

Run live on 2026-04-17 against 4 models via OpenRouter (temperature=0). Scoring: correct=1, uncertain/hedge=0.5, incorrect=0.

| Model | Score | Pass Rate | Key failure pattern |
|-------|-------|-----------|---------------------|
| `openai/gpt-4o` | 8.5/20 | 43% | Oct 2023 cutoff — refused 2025 regulatory figures as "not yet announced" |
| `anthropic/claude-opus-4` | 18/20 | 90% | April 2024 cutoff — strong across IRS/CMS/SSA; missed late-2024 Fed rate cuts |
| `anthropic/claude-sonnet-4.5` | 17.5/20 | 88% | April 2024 cutoff — used stale 2024 FPL base for ACA; stated wrong Fed rate |
| `meta-llama/llama-3.3-70b-instruct` | 8.5/20 | 43% | Early 2023 cutoff — confident wrong answers on HSA, SS wage base, Lambda timeout, gift tax |

**Most dangerous failure:** Llama 3.3 70B gave confident wrong numbers rather than hedging:
- frsh-003: HSA limit stated as $4,150 (2024 figure) — correct is $4,300
- frsh-015: SS wage base stated as $157,600 — correct is $176,100
- frsh-019: Gift tax exclusion stated as $17,000 (2023 figure) — correct is $19,000
- frsh-011: Lambda timeout stated as 14 minutes (840 sec) — correct is 15 minutes (900 sec)

**Universal blind spot (all 4 models):** frsh-007 (Fed funds rate as of early 2026 = 4.25–4.50%) — no model had data on the late-2024 FOMC rate cuts.

Full results: [results/certainlogic_results.json](results/certainlogic_results.json)

---

## Run It

```bash
pip install -r ../requirements.txt
python benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY
```

---

## Case Categories

| Topic | Cases | Last Changes |
|-------|-------|-------------|
| IRS retirement limits (401k, IRA, HSA) | 3 | Annual |
| Social Security (retirement age, wage base) | 2 | Annual / legacy |
| Federal Reserve rate | 1 | Each FOMC meeting (~8/year) |
| Healthcare (ACA thresholds, Medicare premiums) | 2 | Annual |
| Tech EOL (Python, Node.js) | 2 | Annual October cycle |
| AI model releases | 1 | Frequent |
| Legal/regulatory (corporate tax, Bitcoin, ARP) | 3 | Varies |
| FDA drug approvals | 1 | Rolling |
| Supreme Court composition | 1 | As appointments occur |
| OSHA PEL updates | 1 | Periodic |
| Gift tax exclusion | 1 | Annual |
| Tech leadership (CEO) | 1 | As changes occur |
| AWS service limits | 1 | As updated |

---

## Re-Verification Policy

Facts in this benchmark change. Every case includes a `last_verified` date. Cases should be re-verified before each benchmark run.

If a correct answer has changed since `last_verified`, open a PR to update the case.

---

See [METHODOLOGY.md](../METHODOLOGY.md) for scoring criteria and case schema.
