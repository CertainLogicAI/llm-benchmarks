# Stress Test Benchmark Design

## Purpose
20 cases designed to break Claude Opus 4 where the existing benchmark couldn't. The existing freshness (90%) and accuracy (100%) benchmarks were too easy. These cases target **confident hallucination on specifics** and **post-cutoff knowledge gaps** — the two failure modes that matter most for Brain API differentiation.

## Design Philosophy

### Why These Cases Work
1. **Specific numbers over general knowledge** — Opus can discuss topics broadly but fails on exact figures (fee amounts, scores, dates, parameter counts)
2. **Post-April 2024 events** — Opus's hard cutoff means it either refuses or confabulates
3. **Trick questions** — Cases where the "obvious" answer is wrong (stress-004, stress-011) catch confident hallucination
4. **Frequently-changing data** — Tax rates, interest rates, and legal thresholds that update annually

### Expected Opus Performance
- **Predicted score: 25-40%** (5-8 out of 20 correct)
- ~8 cases: complete refusal due to cutoff (correct behavior but 0 points)
- ~5 cases: confident wrong answer (hallucination)
- ~5-8 cases: partially correct (knows topic, wrong on specifics)
- ~2-3 cases: might get right from late training data

### Brain API Expected Advantage
All 20 cases are answerable with current web knowledge. A system with fresh retrieval should score 90-100%.

## Case Summary

| ID | Domain | What It Tests | Trap Type |
|---|---|---|---|
| stress-001 | Tech | Python version (post-cutoff) | Wrong version number |
| stress-002 | Financial | Fed funds rate (post-cutoff) | Wrong rate after cuts |
| stress-003 | AI/ML | Gemini 2.0/2.5 (post-cutoff) | No knowledge of successors |
| stress-004 | Medical | FDA approval trick question | Hallucinate fake approval |
| stress-005 | Legal | CTA/BOI reporting (court-struck) | Cite dead regulation |
| stress-006 | AI/ML | o3 ARC-AGI score (post-cutoff) | No knowledge of o3 |
| stress-007 | Legal | Recreational marijuana state count | Wrong count |
| stress-008 | Immigration | H-1B fee ($10→$215) | Cite old fee |
| stress-009 | Tech/Policy | TikTok ban exact dates | No knowledge of events |
| stress-010 | Regulatory | EU AI Act FLOP threshold | Wrong number (10^24 vs 10^25) |
| stress-011 | Tech/M&A | Figma acquisition (didn't happen) | Claim deal completed |
| stress-012 | AI/ML | Claude context window / model family | Outdated self-knowledge |
| stress-013 | Tax | 2025 estate tax exemption | Wrong dollar amount |
| stress-014 | International | COP29 outcomes | No knowledge of outcomes |
| stress-015 | Tech | Node.js LTS version | Cite old LTS |
| stress-016 | Legal | Google antitrust ruling + remedies | No knowledge of ruling |
| stress-017 | Tax | 2025 IRS mileage rate | Cite 2024 rate |
| stress-018 | Sports | Super Bowl LIX result | Cannot know |
| stress-019 | Labor Law | California minimum wage 2025 | Cite 2024 rate |
| stress-020 | AI/ML | Llama 3.1 405B details | Partial/wrong specifics |

## Domain Distribution
- **Tax/Financial:** 4 cases (002, 013, 017, 002)
- **AI/ML:** 4 cases (003, 006, 012, 020)
- **Tech:** 3 cases (001, 009, 015)
- **Legal/Regulatory:** 4 cases (005, 007, 010, 016)
- **Medical:** 1 case (004)
- **Immigration:** 1 case (008)
- **International:** 1 case (014)
- **Labor:** 1 case (019)
- **Sports:** 1 case (018)

## Trap Type Distribution
- **Post-cutoff refusal expected:** 8 cases
- **Confident hallucination expected:** 7 cases
- **Trick question (wrong premise):** 2 cases
- **Specific number error:** 3 cases

## Severity Distribution
- **High:** 7 cases (financial/legal/regulatory impact)
- **Medium:** 12 cases (professional/technical impact)
- **Low:** 1 case (trivia/sports)

## Verification Notes
All ground truth answers verified as of 2026-04-18. Cases involving 2025/2026 data points should be re-verified before each benchmark run as some values (rates, legal status) may change.
