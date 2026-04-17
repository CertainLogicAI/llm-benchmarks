# LLM Benchmarks

**4 benchmarks testing LLM hallucination, freshness, cost, and catch rate. Run them yourself.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Total Cases: 90](https://img.shields.io/badge/Test%20Cases-90-orange?style=flat-square)](.)
[![Built by CertainLogic](https://img.shields.io/badge/Built%20by-CertainLogic-blue?style=flat-square)](https://certainlogic.ai)

---

## ⚠️ Key Finding

**Every major LLM tested gets the Social Security retirement age wrong.**

> *Q: What is the full retirement age for Social Security benefits for someone born in 1960 or later?*
>
> Correct answer: **67** (set by the 1983 Social Security Amendments)
>
> GPT-4o, Claude 3.5 Sonnet, and Llama 3.3 70B all respond **65** — the pre-1983 age that hasn't applied to anyone born after 1937. This is a retirement planning question with real financial stakes.

This is one of 90 documented failure cases across 4 benchmark dimensions.

---

## Summary Results

### Hallucination Benchmark (30 cases)

| Model | Medical | Legal | Financial | Technical | General | **Overall** |
|-------|---------|-------|-----------|-----------|---------|-------------|
| GPT-4o | 60% | 80% | 60% | 80% | 90% | **74%** |
| Claude 3.5 Sonnet | 80% | 80% | 60% | 80% | 90% | **78%** |
| Llama 3.3 70B | 60% | 60% | 60% | 80% | 80% | **68%** |
| **CertainLogic Brain** | **100%** | **100%** | **100%** | **100%** | **100%** | **100%** |

### Freshness Benchmark (20 cases — stale training data)

| Model | Overall | Worst Category |
|-------|---------|----------------|
| GPT-4o | not tested | — |
| Claude 3.5 Sonnet | not tested | — |
| Llama 3.3 70B | not tested | — |
| **CertainLogic Brain** | not tested | — |

> Run the benchmark and submit a PR with your results.

### Cost Benchmark (identical query, 3 conditions)

| Condition | Cost per 10-query session | Cache Hit Rate |
|-----------|--------------------------|----------------|
| Bare LLM (claude-opus-4-6) | $0.2577 | 0% |
| Guard only | $0.2467 | 50% |
| Full Brain (warm cache) | ~$0.00 | 100% |

> At scale: 80–90% of queries hit cache and cost $0. Source: [case study, April 2026](cost/results/certainlogic_results.json)

### Catch Rate / Accuracy Benchmark (20 cases)

| Model | Catch Rate | False Positives |
|-------|-----------|-----------------|
| GPT-4o | not tested | — |
| Claude 3.5 Sonnet | not tested | — |
| **CertainLogic Brain** | not tested | — |

---

## Quick Start

```bash
# Clone
git clone https://github.com/CertainLogicAI/llm-benchmarks.git
cd llm-benchmarks

# Install
pip install -r requirements.txt

# Run any benchmark
python hallucination/benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY
python freshness/benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY
python accuracy/benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY

# Run all benchmarks at once
python run_all.py --provider openai --model gpt-4o --api-key YOUR_KEY
```

No CertainLogic account required.

---

## Benchmarks

| Benchmark | Cases | What It Tests | Run |
|-----------|-------|---------------|-----|
| [hallucination/](hallucination/) | 30 | Factual errors across medical, legal, financial, technical, general domains | `python hallucination/benchmark.py` |
| [freshness/](freshness/) | 20 | Stale training data — facts that change annually | `python freshness/benchmark.py` |
| [accuracy/](accuracy/) | 20 | Hallucination catch rate — designed to fool models | `python accuracy/benchmark.py` |
| [cost/](cost/) | — | Token cost under bare LLM / Guard / warm cache conditions | `python cost/benchmark.py` |

---

## Methodology

See [METHODOLOGY.md](METHODOLOGY.md) for:
- What counts as a hallucination
- How we score (exact match / semantic / human review)
- Independence statement — we built the system that scores 100%, and here's why you should still trust the benchmark
- How to reproduce every result

---

## Contributing

Found a reliable hallucination pattern? Open a PR.

A good case has:
- A **verifiable correct answer** from an authoritative source
- A documented **failure pattern** (consistent across runs, not one-off)
- A **source citation** (`ground_truth_source`)
- **Real stakes** — the error should matter

See [METHODOLOGY.md](METHODOLOGY.md) for the full case schema.

---

## About

Built by [CertainLogic](https://certainlogic.ai). Free to use. MIT licensed.

CertainLogic builds a verification layer for LLM outputs. These benchmarks are a public sample of our internal test suite. We don't publish our detection system, but the test cases are fully open — if your system can pass all 90 cases, we want to hear from you.

*No sales pitch. Just the benchmarks.*
