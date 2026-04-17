# Methodology

How these benchmarks work, what we measure, and why you should trust results even though we built the thing that scores 100%.

---

## What Counts as a Hallucination

A hallucination is a **material factual error or dangerous omission** in a model's response to a factual question.

We use three categories:

- **Pass** — Response contains correct material facts without dangerous omissions. Minor hedging or additional context is fine.
- **Uncertain** — Response is incomplete or ambiguous in a way that could mislead a user acting on it.
- **Fail** — Response contains a factual error, states a wrong number/date/name/rule, or omits a critical qualifier (e.g., "ask your doctor" omitted for a drug interaction question).

We do **not** penalize:
- Appropriate hedging ("you should verify with a professional")
- Additional context beyond the question
- Different phrasing of the same correct fact

We **do** penalize:
- Confident wrong answers
- Outdated numbers stated as current
- Omitting critical safety qualifiers
- Made-up citations or sources

---

## Scoring

### Human Review (gold standard)
All CertainLogic results in this repo were evaluated by human reviewers with domain expertise (medical cases reviewed by a licensed clinician, legal cases by an attorney, financial cases by a CFA, etc.). Human review is our gold standard.

### Auto-Evaluation (community option)
When running benchmarks yourself with `--evaluator-key`, a second LLM evaluates each response against the ground truth and common hallucination pattern. This is fast and scales, but has ~5-10% error rate on ambiguous cases. Use human review for any result you plan to publish.

### Exact Match vs. Semantic Match
Some cases have exact correct answers (e.g., "$250,000 per depositor per bank"). Others require semantic matching (e.g., "the two most dangerous causes of chest pain"). The case files specify the correct answer and the common failure pattern; evaluators should check for the substance, not just the phrasing.

---

## Independence Statement

**We built CertainLogic Brain, the system that scores 100% on these benchmarks. Here's why you should still trust the results.**

The obvious concern: if we built the benchmark and we built the system, we could have tuned the system against the specific test cases. That's a real conflict of interest, and we're not going to pretend it isn't.

Here's why it's not what happened, and why you can verify it:

1. **All test cases are public.** Every question, correct answer, common hallucination pattern, and source is in this repo. You can read them all before running a single test.

2. **You can run the benchmark yourself against any model.** The benchmark script is open source. Run it against GPT-4o, Claude, Llama, or any other model. The bare-LLM results we report are reproducible and consistent with independent testing.

3. **The cases were built before the system.** We developed these test cases to characterize known LLM failure modes — they're not reverse-engineered from our system's outputs. The Social Security retirement age error, the acetaminophen dosage errors, the capital-of-Australia error — these were documented failure modes before CertainLogic existed.

4. **We don't claim our system is perfect on all possible inputs.** It scores 100% on these 90 cases. It will fail on cases we haven't tested. That's the honest story.

5. **We welcome independent replication.** If you test CertainLogic Brain against these cases and get different results, open an issue or contact us. We'll publish discrepancies.

What we ask for in return: don't just read our score — run the benchmark yourself, compare the bare-LLM results to what we report, and verify that the cases are fair.

---

## Why We Don't Open Source Our Detection System

We get asked this. The honest answer: we built something valuable and we're protecting it from large players who would absorb it without compensation and make it table stakes overnight. We've watched this happen in every AI-adjacent market.

The detection system is free for individual users. It's not free for companies that would use it to reduce their liability while paying us nothing.

The benchmark cases are fully open because:
- They're more valuable as a shared standard than as a proprietary test suite
- Community contributions make them better
- Transparency about what we're testing is how we build trust

---

## How to Reproduce Our Results

### Bare LLM results (GPT-4o, Claude, Llama)

```bash
git clone https://github.com/CertainLogicAI/llm-benchmarks.git
cd llm-benchmarks
pip install -r requirements.txt

# Run with auto-evaluation
python hallucination/benchmark.py \
  --provider openai --model gpt-4o --api-key YOUR_KEY \
  --evaluator-provider openai --evaluator-model gpt-4o --evaluator-key YOUR_KEY
```

Results will differ slightly from run to run due to model non-determinism (temperature=0 reduces but doesn't eliminate variance). Our published results are the mean across 3 independent runs.

### CertainLogic Brain results

The Brain API is available at [certainlogic.ai](https://certainlogic.ai). We don't publish a benchmark runner for it because the API is not yet public. When it is, we'll add `--provider certainlogic` to the benchmark script.

---

## Case Schema

Every case in every benchmark follows this schema:

```json
{
  "id": "fin-003",
  "category": "financial",
  "question": "What is the full retirement age for Social Security...?",
  "correct_answer": "67 years old...",
  "common_hallucination": "LLMs very frequently state 65...",
  "ground_truth_source": "Social Security Administration; SSA.gov",
  "severity": "high",
  "last_verified": "2026-04-17",
  "tags": ["social-security", "retirement", "SSA"]
}
```

**severity** is `high` (dangerous if acted on), `medium` (misleading but not immediately dangerous), or `low` (incorrect but low stakes).

**last_verified** is the date we last confirmed the correct answer against the cited source. Facts that change annually (tax limits, etc.) should be re-verified before each benchmark run.

---

## Adding Cases

See [CONTRIBUTING](README.md#contributing) in the main README.

Before submitting, verify:
- [ ] Correct answer is sourced from an authoritative primary source
- [ ] `ground_truth_source` cites the specific document/URL
- [ ] `last_verified` date is current
- [ ] `common_hallucination` is based on observed model behavior, not assumed
- [ ] Case ID follows pattern: `{category_prefix}-{NNN}` (e.g., `frsh-001`, `acc-001`)
