# Freshness Benchmark

**20 test cases targeting stale training data — facts that change annually.**

Part of [llm-benchmarks](../README.md) by CertainLogic.

---

## What This Tests

LLMs have training cutoffs. Facts that change annually — IRS contribution limits, Medicare premiums, Node.js LTS schedules, Federal Reserve rates — are a reliable freshness signal. A model that confidently states the 2023 IRS 401(k) limit as current is demonstrating training data lag in a measurable, verifiable way.

This benchmark documents 20 such cases with verified correct answers and known LLM failure patterns.

---

## Results

| Model | Overall | Notes |
|-------|---------|-------|
| GPT-4o | not tested | Submit a PR with your results |
| Claude 3.5 Sonnet | not tested | Submit a PR with your results |
| Llama 3.3 70B | not tested | Submit a PR with your results |
| **CertainLogic Brain** | not tested | Will test and publish |

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
