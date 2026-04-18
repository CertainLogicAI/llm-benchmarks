#!/usr/bin/env python3
"""Run raw GPT-4o against freshness + accuracy benchmarks via OpenRouter."""
import json, time, requests
from pathlib import Path

OR_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "openai/gpt-4o"
BASE = Path(__file__).parent

def ask(question):
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": [{"role": "user", "content": question}],
              "max_tokens": 500, "temperature": 0},
        timeout=60
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

for benchmark in ["freshness", "accuracy"]:
    cases = json.load(open(BASE / f"{benchmark}/cases/{benchmark}.json"))
    results = []
    print(f"\n=== Raw {MODEL} — {benchmark.title()} ===")
    for case in cases:
        try:
            answer = ask(case["question"])
            excerpt = answer[:150].replace('\n', ' ')
        except Exception as e:
            answer = excerpt = f"[ERROR: {e}]"
        print(f"  {case['id']}... {excerpt[:80]}")
        results.append({"id": case["id"], "question": case["question"],
                        "correct_answer": case["correct_answer"],
                        "response": answer, "excerpt": excerpt})
        time.sleep(0.5)
    out = BASE / f"{benchmark}/results/gpt4o_raw_responses.json"
    json.dump(results, open(out, "w"), indent=2)
    print(f"Saved to {out}")
print("\nDone. Ready for scoring.")
