import os
#!/usr/bin/env python3
"""
CertainLogic LLM Benchmarks — freshness + accuracy
4 models: GPT-4o, Claude Opus 4, Claude Sonnet 4.5, Llama 3.3 70B
Saves checkpoint after each model to /tmp/ckpt_{benchmark}_{model_slug}.json
"""

import json, time, os, requests

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "https://certainlogic.ai",
    "X-Title": "CertainLogic Benchmark",
    "Content-Type": "application/json"
}

MODELS = [
    "openai/gpt-4o",
    "anthropic/claude-opus-4",
    "anthropic/claude-sonnet-4.5",
    "meta-llama/llama-3.3-70b-instruct",
]

def slug(model): return model.replace("/", "__").replace(".", "_")

def ckpt_path(benchmark, model):
    return f"/tmp/ckpt_{benchmark}_{slug(model)}.json"

def ask_model(model, question):
    payload = {"model": model, "messages": [{"role": "user", "content": question}],
               "max_tokens": 500, "temperature": 0}
    resp = requests.post(ENDPOINT, headers=HEADERS, json=payload, timeout=90)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def run_model_on_benchmark(benchmark_name, cases, model):
    path = ckpt_path(benchmark_name, model)
    if os.path.exists(path):
        existing = json.load(open(path))
        done_ids = {c["id"] for c in existing}
        remaining = [c for c in cases if c["id"] not in done_ids]
        results = existing
        print(f"    Resuming ({len(done_ids)} already done)")
    else:
        remaining = cases
        results = []

    for case in remaining:
        cid = case["id"]
        print(f"    {cid}...", end="", flush=True)
        try:
            response = ask_model(model, case["question"])
            results.append({"id": cid, "question": case["question"],
                             "correct_answer": case["correct_answer"],
                             "response": response, "response_excerpt": response[:200]})
            print(" OK")
        except Exception as e:
            err = str(e)[:120]
            results.append({"id": cid, "question": case["question"],
                             "correct_answer": case["correct_answer"],
                             "response": f"ERROR: {err}", "response_excerpt": f"ERROR: {err}"})
            print(f" ERROR: {err}")
        json.dump(results, open(path, "w"), indent=2)
        time.sleep(0.5)
    return results

def run_benchmark(benchmark_name, cases):
    all_results = {}
    for model in MODELS:
        print(f"\n  [{model}]")
        all_results[model] = run_model_on_benchmark(benchmark_name, cases, model)
    return all_results

# Load cases
with open("/data/.openclaw/workspace/llm-benchmarks/freshness/cases/freshness.json") as f:
    freshness_cases = json.load(f)
with open("/data/.openclaw/workspace/llm-benchmarks/accuracy/cases/accuracy.json") as f:
    accuracy_cases = json.load(f)

print("=== FRESHNESS BENCHMARK ===")
freshness_raw = run_benchmark("freshness", freshness_cases)

print("\n=== ACCURACY BENCHMARK ===")
accuracy_raw = run_benchmark("accuracy", accuracy_cases)

# Final consolidated save
with open("/tmp/freshness_raw.json", "w") as f:
    json.dump(freshness_raw, f, indent=2)
with open("/tmp/accuracy_raw.json", "w") as f:
    json.dump(accuracy_raw, f, indent=2)

print("\nAll done. Results in /tmp/freshness_raw.json and /tmp/accuracy_raw.json")
