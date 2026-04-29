# LLM Accuracy and Freshness Benchmark

> ⚠️ **STATUS: WITHDRAWN — INADEQUATE METHODOLOGY**
>
> The CertainLogic Brain API results presented in this benchmark (reported as improving Llama by "+40 percentage points on freshness," achieving 100% on epistemic scoring) were produced using a proprietary system with scoring frameworks designed to favor that system's outputs. The benchmark methodology failed to adequately disclose:
> - That the Brain API degraded accuracy on established facts (100% → 87.5% vs. raw GPT-4o)
> - That "epistemic scoring" (uncertain=1.0) was designed to reward hedging rather than correctness
> - That the Brain API could not be independently tested or verified by third parties
>
> **These results should not be cited as evidence of CertainLogic product performance.** The bare-LLM results (GPT-4o, Claude, Llama) may be independently reproducible. The CertainLogic results are not.
>
> This repo is retained for transparency. No further updates.

**Published:** April 18, 2026  
**Authors:** CertainLogic Research Team  
**Paper:** [paper1-benchmark-study-final.md](../docs/paper1-benchmark-study-final.md) *(withdrawn)*

## Overview

A comparative benchmark evaluating 5 AI systems across two dimensions:
- **Freshness:** Knowledge of facts established after common training cutoffs (20 cases)
- **Accuracy:** Established factual knowledge unlikely to change (20 cases)

Systems tested: OpenAI GPT-4o, Anthropic Claude Opus 4, Anthropic Claude Sonnet 4.5, Meta Llama 3.3 70B Instruct, CertainLogic Brain API.

## Key Findings

- Training data recency is the dominant source of variation on freshness queries
- GPT-4o and Llama 3.3 70B scored identically on freshness (42.5%) but failed in opposite ways: GPT-4o declined to answer (safer), Llama stated confidently wrong numbers (dangerous)
- Under epistemic scoring (which rewards "I don't know" over confident errors), rankings shift significantly
- The CertainLogic Brain API retrieval pipeline improved Llama 3.3 70B freshness by +40 percentage points with the same underlying model

## Scoring

Two frameworks are used:
- **Traditional:** correct=1.0, uncertain=0.5, incorrect=0.0
- **Epistemic:** correct=1.0, uncertain=1.0, incorrect=0.0 (rewards acknowledged ignorance over confident errors)

## Reproducing Results

### Against the LLMs directly
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

Results are saved to `freshness/results/` and `accuracy/results/`.

## Structure

```
freshness/
  cases/freshness.json      — 20 test cases with ground truth
  results/                  — scored results per system
accuracy/
  cases/accuracy.json       — 20 test cases with ground truth  
  results/                  — scored results per system
stress_test/
  cases/stress_test.json    — 20 harder cases (post-cutoff knowledge)
  results/                  — stress test results
run_benchmarks.py           — runs all 4 LLMs via OpenRouter
run_brain_benchmark.py      — runs CertainLogic Brain API
```

## Conflict of Interest

The CertainLogic Brain API is developed by the authors of this study. All test cases, correct answers, scoring criteria, and raw response data are included in this repository for independent verification.

## License

MIT — reproduce, extend, and publish your own results.
