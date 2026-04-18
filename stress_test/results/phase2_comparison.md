# Phase 2: Brain API + Opus vs Raw Opus — Stress Test Comparison

## Scoring Rubric
- **correct (1.0):** materially correct answer verified against ground truth
- **uncertain (0.5):** declined, hedged, or can't confirm
- **incorrect (0.0):** wrong specific fact stated with confidence

## Case-by-Case Comparison

| Case ID | Topic | Raw Opus | Brain API | Delta | Notes |
|---------|-------|----------|-----------|-------|-------|
| stress-001 | Python version (Mar 2026) | uncertain (0.5) | uncertain (0.5) | 0 | Both properly declined |
| stress-002 | Fed funds rate (Apr 2026) | uncertain (0.5) | uncertain (0.5) | 0 | Both properly declined |
| stress-003 | Gemini successor | correct (1.0) | correct (1.0) | 0 | Both got Gemini 2.0 Flash Dec 2024 |
| stress-004 | PPD drug (trick Q) | correct (1.0) | correct (1.0) | 0 | Both caught the trick — Zurzuvae was Aug 2023 |
| stress-005 | CTA deadline | uncertain (0.5) | uncertain (0.5) | 0 | Both hedged; Brain API led with original deadline but flagged legal challenges |
| stress-006 | o3 ARC-AGI score | correct (1.0) | correct (1.0) | 0 | Both got 87.5% high-compute |
| stress-007 | Recreational marijuana states | correct (1.0) | correct (1.0) | 0 | Both: 24 states + DC |
| stress-008 | H-1B registration fee | correct (1.0) | correct (1.0) | 0 | Both: $215 |
| stress-009 | TikTok ban dates | **incorrect (0.0)** | **correct (1.0)** | **+1.0** | Raw Opus said restored Jan 20 (wrong); Brain API said dark+restored Jan 19 (correct) |
| stress-010 | EU AI Act FLOP threshold | correct (1.0) | correct (1.0) | 0 | Both: 10^25 FLOPs |
| stress-011 | Figma acquisition (trick Q) | correct (1.0) | correct (1.0) | 0 | Both: deal abandoned Dec 2023 |
| stress-012 | Claude context window | correct (1.0) | correct (1.0) | 0 | Both: 200K tokens |
| stress-013 | Estate tax exemption 2025 | correct (1.0) | correct (1.0) | 0 | Both: $13.99M |
| stress-014 | COP29 outcome | correct (1.0) | correct (1.0) | 0 | Both: Azerbaijan, $300B/yr by 2035 |
| stress-015 | Node.js LTS | correct (1.0) | correct (1.0) | 0 | Both: Node 22 Jod |
| stress-016 | Google antitrust | correct (1.0) | correct (1.0) | 0 | Both: monopoly ruling Aug 2024, remedies ongoing |
| stress-017 | IRS mileage rate 2025 | correct (1.0) | correct (1.0) | 0 | Both: 70¢/mile |
| stress-018 | Super Bowl LIX | correct (1.0) | correct (1.0) | 0 | Both: Eagles 40-22 |
| stress-019 | CA minimum wage 2025 | correct (1.0) | correct (1.0) | 0 | Both: $16.50/hr |
| stress-020 | Meta Llama 3 | correct (1.0) | correct (1.0) | 0 | Both: Llama 3/3.1, 405B |

## Summary Scores

| Metric | Raw Opus | Brain API + Opus | Delta |
|--------|----------|-----------------|-------|
| Correct | 16 | 17 | +1 |
| Uncertain | 3 | 3 | 0 |
| Incorrect | 1 | 0 | **-1** |
| **Traditional Score** | **17.5/20 (87.5%)** | **18.5/20 (92.5%)** | **+1.0 (+5.0%)** |
| **Epistemic Score** | **19/20 (95.0%)** | **20/20 (100.0%)** | **+1.0 (+5.0%)** |

## Key Findings

1. **Brain API eliminated the only incorrect answer** (stress-009 TikTok dates) — Raw Opus said restored Jan 20 (wrong day), Brain API correctly said same-day restoration on Jan 19.

2. **Brain API achieved perfect epistemic score (100%)** — every response was either correct or properly hedged. Zero confidently wrong answers.

3. **No regressions** — Brain API matched or exceeded Raw Opus on every single case.

4. **Previous bug-affected scores were significantly wrong** — the prior scoring run had Brain API at 10.5/20 (52.5%) with 4 incorrect and 11 uncertain. The re-score shows 18.5/20 (92.5%) with 0 incorrect. The bug was in the scoring, not the responses.

## vs Previous (Buggy) Scoring

| Metric | Previous (Buggy) | Re-scored | Delta |
|--------|-----------------|-----------|-------|
| Correct | 5 | 17 | +12 |
| Uncertain | 11 | 3 | -8 |
| Incorrect | 4 | 0 | -4 |
| Traditional | 10.5 (52.5%) | 18.5 (92.5%) | +8.0 (+40%) |
| Epistemic | 16 (80.0%) | 20 (100.0%) | +4.0 (+20%) |
