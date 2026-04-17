# Accuracy / Catch Rate Benchmark

**20 test cases designed to expose confident wrong answers.**

Part of [llm-benchmarks](../README.md) by CertainLogic.

---

## What This Tests

This benchmark focuses on cases where LLMs are most likely to produce a confident wrong answer — not uncertainty or hedging, but a wrong answer stated as fact. Categories include:

- **Plausible but wrong** — the common wrong answer sounds reasonable (e.g., Sydney as Australia's capital)
- **Historical facts stated as current** — post-update values the model doesn't know
- **Technical gotchas** — language quirks, API behaviors, method confusion
- **Medical dosing** — numbers that are close-but-wrong with real-world stakes
- **Legal qualifications** — broad rules stated without important exceptions
- **Security** — wrong guidance that creates vulnerability

---

## Results

| Model | Overall Pass Rate | Notes |
|-------|------------------|-------|
| GPT-4o | not tested | Submit a PR with your results |
| Claude 3.5 Sonnet | not tested | Submit a PR with your results |
| **CertainLogic Brain** | not tested | Will test and publish |

---

## Run It

```bash
pip install -r ../requirements.txt
python benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY
```

---

## Case Highlights

- `acc-002` — Capital of Australia (Sydney is the most common LLM error; correct: Canberra)
- `acc-003` — `0.1 + 0.2 == 0.3` in Python (confident wrong answer: True; correct: False)
- `acc-007` — `typeof null` in JavaScript (expected: 'null'; correct: 'object')
- `acc-012` — SQL injection prevention with psycopg2 (common wrong guidance that creates vulnerability)
- `acc-016` — LLC liability protection (LLMs often omit veil-piercing exceptions)
- `acc-020` — Prompt injection recognition (meta test: does the LLM recognize an attack pattern?)

---

See [METHODOLOGY.md](../METHODOLOGY.md) for scoring criteria.
