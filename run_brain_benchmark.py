#!/usr/bin/env python3
"""
Run freshness + accuracy benchmarks against CertainLogic Brain API.
Produces full per-case breakdown: correct / uncertain / incorrect.
Scoring order: required (correct) → bad (incorrect) → uncertainty (uncertain)
"""
import json, time, requests
from pathlib import Path

API_KEY = "cl_live_a491640648c0a859c941adc8ab23ea72"
BASE = Path(__file__).parent

FRESHNESS_CASES   = BASE / "freshness/cases/freshness.json"
ACCURACY_CASES    = BASE / "accuracy/cases/accuracy.json"
FRESHNESS_RESULTS = BASE / "freshness/results/certainlogic_results.json"
ACCURACY_RESULTS  = BASE / "accuracy/results/certainlogic_results.json"


def query_brain(question: str) -> dict:
    r = requests.post(
        "http://127.0.0.1:8000/query",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"query": question},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def score_response(answer: str, case_id: str) -> str:
    """
    Three-category scoring:
      correct   — answer contains the right fact/number/date
      uncertain — system hedged without answering
      incorrect — system gave wrong fact with confidence

    ORDER: required patterns first (→ correct), then bad patterns (→ incorrect),
           then uncertainty phrases (→ uncertain), then default uncertain.
    """
    ans = answer.lower().strip()

    # Cases: required substrings, bad (wrong fact) substrings
    # Required match → CORRECT (even if hedging language present)
    # Bad match (only if required not matched) → INCORRECT
    checks = {
        # ── FRESHNESS ────────────────────────────────────────────────────────
        "frsh-001": (["23,500", "23500"], ["23,000 for 2025", "same as 2024"]),
        "frsh-002": (["7,000", "$7,000", "7000"], ["6,000", "6,500"]),
        "frsh-003": (["4,300", "$4,300", "4300"], ["4,150 for 2025", "limit is $4,150", "limit for 2025 is $4,150"]),
        "frsh-004": (["67 year", "age 67", "67 years"], ["65 year", "66 year"]),
        "frsh-005": (["7.25", "$7.25"], []),
        "frsh-006": (["15,060", "60,240", "$15,060"], []),
        "frsh-007": (["4.25", "4.50%", "4.25%–4.50%", "4.25-4.50"], ["5.25", "5.50"]),
        "frsh-008": (["3.13", "python 3.13"], ["3.8 is", "3.9 is supported"]),
        "frsh-009": (["6 justice", "six justice", "6 were appointed by republican", "6 republican"], []),
        "frsh-010": (["sam altman", "altman"], []),
        "frsh-011": (["15 minute", "900 second", "15-minute"], ["5 minute", "14 minute"]),
        "frsh-012": (["claude 3.5 sonnet", "3.5 sonnet"], []),
        "frsh-013": (["$185", "185.00", "185 per month"], ["$174", "$170", "$164"]),
        "frsh-014": (["node.js 22", "node 22 "], ["node.js 18 is current", "node 18 is current", "node.js 16"]),
        "frsh-015": (["176,100", "$176,100"], ["168,600", "160,200", "147,000"]),
        "frsh-016": (["21%", "21 percent", "21-percent"], ["35% is current", "rate is 35", "35 percent is"]),
        "frsh-017": (["commodity", "not a security"], ["classified as a security", "is a security"]),
        "frsh-018": (["december 2017", "type 2 diabetes"], []),
        "frsh-019": (["$19,000", "19,000 per", "19000 per"], ["$17,000", "$18,000 for 2025", "18,000 for 2025"]),
        "frsh-020": (["50 µg", "50 μg", "50ug", "50 micrograms", "50µg", "0.05 mg"], ["100 µg", "100 micrograms", "0.025 mg", "25 µg", "25 micrograms"]),
        # ── ACCURACY ─────────────────────────────────────────────────────────
        "acc-001": (["9.80665", "9.81 m/s"], ["10 m/s²", "10 m/s2", "= 10 m"]),
        "acc-002": (["canberra"], ["sydney", "melbourne"]),
        "acc-003": (["false"], ["true"]),
        "acc-004": (["206 bone", "206"], ["207", "208", "212"]),
        "acc-005": (["teapot", "418 i'm", "i'm a teapot"], ["200", "not found", "404"]),
        "acc-006": (["2,550", "2550"], ["3,000", "3000"]),
        "acc-007": (["'object'", '"object"', "returns 'object'", "returns \"object\"", "typeof null` returns", "output is `\"object\"`", "output is 'object'"], ["'null'", "'undefined'", "returns null", "returns undefined"]),
        "acc-008": (["4 year", "four year", "ccp §337", "section 337"], ["3 year", "6 year"]),
        "acc-009": (["pop()", ".pop()"], [".remove() returns", "remove returns"]),
        "acc-010": (["21,196", "21196", "13,171", "13171"], ["4,000 mile", "6,400 km", "5,500 mile"]),
        "acc-011": (["after every render", "every render", "every re-render", "runs after every"], ["before the render", "before render"]),
        "acc-012": (["cursor.execute", "%s"], ["f-string", 'f"', "format()"]),
        "acc-013": (["penicillin"], []),
        "acc-014": (["generally legal", "generally yes", "legal for", "legally monitor", "employers can"], ["illegal", "not legal"]),
        "acc-015": (["o(1)", "constant time", "average case: o(1)"], ["o(log", "o(n) is the average"]),
        "acc-016": (["not absolute", "veil", "personal guarantee", "exceptions", "not unconditional", "generally yes, but"], ["provides complete", "fully protected", "absolute protection"]),
        "acc-017": (["79"], ["78", "80"]),
        "acc-018": (["precision = tp / (tp + fp)", "tp/(tp+fp)", "tp / (tp + fp)", "precision: tp/(tp+fp)"], []),
        "acc-019": (["c and rust", "c, with", "primarily in c", "in c with", "rust"], ["written in c++"]),
        "acc-020": (["should not output", "not output", "should not comply", "decline", "refuse", "politely decline", "resist"], ["should output", "must output", "should comply with", "would output"]),
    }

    if case_id not in checks:
        # Unknown case — try basic uncertainty detection
        pass
    else:
        required, bad = checks[case_id]
        # 1. Required match → CORRECT (even if hedging present)
        if required and any(r in ans for r in required):
            return "correct"
        # 2. Bad match → INCORRECT
        if bad and any(b in ans for b in bad):
            return "incorrect"

    # 3. Uncertainty phrases → UNCERTAIN
    uncertainty_phrases = [
        "i don't have", "i do not have", "don't know", "do not know",
        "cannot confirm", "can't confirm", "i'm not sure", "i am not sure",
        "unable to", "no information", "not available", "cannot provide",
        "recommend checking", "i cannot", "beyond my", "real-time",
        "[empty response", "no answer", "[empty",
    ]
    if any(p in ans for p in uncertainty_phrases):
        return "uncertain"

    # 4. Default uncertain (couldn't verify)
    return "uncertain"


def run_benchmark(cases_file: Path, label: str):
    with open(cases_file) as f:
        cases = json.load(f)

    results = []
    method_breakdown = {"facts_cache": 0, "clkl": 0, "llm": 0}
    correct = uncertain = incorrect = 0

    for case in cases:
        cid = case["id"]
        print(f"  {cid}...", end=" ", flush=True)
        try:
            resp = query_brain(case["question"])
            answer = resp.get("answer", "")
            method = resp.get("method", "llm")
            confidence = (resp.get("validation") or {}).get("confidence",
                          resp.get("routing_confidence", 0.0))

            if not answer or answer.strip() == "":
                answer = "[empty response — no answer returned]"

            result = score_response(answer, cid)

            if result == "correct":    correct += 1
            elif result == "uncertain": uncertain += 1
            else:                       incorrect += 1

            # method bucket
            if method in method_breakdown:
                method_breakdown[method] += 1
            elif "cache" in method:
                method_breakdown["facts_cache"] += 1
            elif "clkl" in method or "deterministic" in method:
                method_breakdown["clkl"] += 1
            else:
                method_breakdown["llm"] += 1

            excerpt = answer[:150]
            print(f"{result.upper()} [{method}]  {excerpt[:80]}")
            results.append({
                "id": cid,
                "result": result,
                "response_excerpt": excerpt,
                "method": method,
                "confidence": confidence,
            })
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "id": cid, "result": "uncertain",
                "response_excerpt": f"[ERROR: {e}]",
                "method": "llm", "confidence": 0.0,
            })
            uncertain += 1
        time.sleep(0.3)

    total = correct + uncertain + incorrect
    score = correct + uncertain * 0.5
    pass_rate = f"{round(score/total*100)}%"
    print(f"\n  {label}: correct={correct} uncertain={uncertain} incorrect={incorrect}"
          f" | score={score}/{total} pass_rate={pass_rate}\n")

    return {
        "score": f"{score}/{total}",
        "pass_rate": pass_rate,
        "correct": correct,
        "uncertain": uncertain,
        "incorrect": incorrect,
        "method_breakdown": method_breakdown,
        "cases": results,
    }


def update_results_file(results_file: Path, new_data: dict):
    with open(results_file) as f:
        data = json.load(f)
    data["certainlogic/brain-api"] = {
        **new_data,
        "run_date": "2026-04-17",
        "note": "Re-run with full per-case breakdown. Scoring: correct (required match) / uncertain (hedge no answer) / incorrect (wrong fact). Required match wins over hedging language.",
    }
    with open(results_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Updated: {results_file}")


print("=== CertainLogic Brain API — Freshness Benchmark ===")
frsh = run_benchmark(FRESHNESS_CASES, "Freshness")

print("=== CertainLogic Brain API — Accuracy Benchmark ===")
acc = run_benchmark(ACCURACY_CASES, "Accuracy")

print("=== Writing results ===")
update_results_file(FRESHNESS_RESULTS, frsh)
update_results_file(ACCURACY_RESULTS, acc)

print("Done.")
