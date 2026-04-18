#!/usr/bin/env python3
"""
Latency Benchmark — CertainLogic Brain API vs Bare LLM
=======================================================

Measures full round-trip response time for factual queries across:
  1. CertainLogic Brain API (with structured knowledge + verification layer)
  2. Bare LLM via OpenRouter (no verification, raw model output)

Usage:
  python latency/benchmark.py \
    --brain-api-url http://127.0.0.1:8000 \
    --brain-api-key YOUR_KEY \
    --openrouter-key YOUR_OR_KEY \
    --runs 3

  # Bare LLM only (no Brain API):
  python latency/benchmark.py --openrouter-key YOUR_OR_KEY --runs 3

  # Brain API only:
  python latency/benchmark.py \
    --brain-api-url http://127.0.0.1:8000 \
    --brain-api-key YOUR_KEY \
    --runs 3
"""

import argparse
import json
import statistics
import time
from datetime import date

try:
    import requests
except ImportError:
    raise SystemExit("Missing dependency: pip install requests")

# Default test queries — mix of facts-cache hits and LLM fallbacks
DEFAULT_QUERIES = [
    "What is the maximum daily dose of acetaminophen for adults?",
    "What is the 2024 401k contribution limit for employees under 50?",
    "What is the Social Security full retirement age for people born after 1960?",
    "What is the FDIC insurance limit per depositor?",
    "What is the federal minimum wage?",
    "What does HTTP status code 418 mean?",
    "What is the capital of Australia?",
    "What is the boiling point of water in Celsius?",
    "How many justices are on the US Supreme Court?",
    "What is the speed of light in meters per second?",
]


def query_brain_api(url: str, key: str, query: str, timeout: int = 30) -> dict:
    """Query Brain API and return timing + metadata."""
    start = time.time()
    r = requests.post(
        f"{url}/query",
        headers={"X-API-Key": key},
        json={"query": query},
        timeout=timeout,
    )
    elapsed_ms = (time.time() - start) * 1000
    data = r.json() if r.ok else {}
    return {
        "elapsed_ms": round(elapsed_ms, 1),
        "method": data.get("method", data.get("source", "unknown")),
        "confidence": data.get("confidence"),
        "status_code": r.status_code,
    }


def query_openrouter(key: str, query: str, model: str, timeout: int = 60) -> dict:
    """Query OpenRouter and return timing."""
    start = time.time()
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://certainlogic.ai",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": query}],
        },
        timeout=timeout,
    )
    elapsed_ms = (time.time() - start) * 1000
    return {
        "elapsed_ms": round(elapsed_ms, 1),
        "status_code": r.status_code,
    }


def run_benchmark(args) -> dict:
    results = []

    for query in DEFAULT_QUERIES:
        print(f"\nQuery: {query[:70]}...")
        row = {"query": query, "brain_api": None, "bare_llm": None}

        # --- Brain API ---
        if args.brain_api_url and args.brain_api_key:
            brain_runs = []
            brain_method = "unknown"
            for i in range(args.runs):
                try:
                    run = query_brain_api(args.brain_api_url, args.brain_api_key, query)
                    brain_runs.append(run["elapsed_ms"])
                    if i == 0:
                        brain_method = run["method"]
                    print(f"  Brain[{i}]: {run['elapsed_ms']:.0f}ms method={run['method']}")
                except Exception as e:
                    print(f"  Brain[{i}] ERROR: {e}")
            valid = [t for t in brain_runs if t is not None]
            row["brain_api"] = {
                "median_ms": round(statistics.median(valid), 1) if valid else None,
                "method": brain_method,
                "runs_ms": brain_runs,
            }

        # --- Bare LLM ---
        if args.openrouter_key:
            llm_runs = []
            for i in range(args.runs):
                try:
                    run = query_openrouter(args.openrouter_key, query, args.model)
                    llm_runs.append(run["elapsed_ms"])
                    print(f"  LLM[{i}]: {run['elapsed_ms']:.0f}ms")
                except Exception as e:
                    print(f"  LLM[{i}] ERROR: {e}")
            valid = [t for t in llm_runs if t is not None]
            row["bare_llm"] = {
                "median_ms": round(statistics.median(valid), 1) if valid else None,
                "runs_ms": llm_runs,
            }

        # Speedup (Brain vs LLM — positive means Brain is faster, negative means LLM is faster)
        if row["brain_api"] and row["bare_llm"]:
            b = row["brain_api"]["median_ms"]
            l = row["bare_llm"]["median_ms"]
            if b and l:
                row["speedup_llm_vs_brain"] = round(b / l, 1)
                print(f"  => Brain: {b:.0f}ms ({row['brain_api']['method']}), LLM: {l:.0f}ms, LLM is {b/l:.1f}x faster")

        results.append(row)

    return {
        "benchmark": "latency",
        "run_date": date.today().isoformat(),
        "methodology": f"{args.runs} runs per query, median reported. Brain API: {args.brain_api_url or 'not run'}. LLM model: {args.model}.",
        "results": results,
    }


def print_summary(data: dict):
    print("\n\n=== SUMMARY ===")
    print(f"{'Query':<55} {'Brain(ms)':>10} {'Method':<15} {'LLM(ms)':>8} {'LLM/Brain':>10}")
    print("-" * 100)
    cache_times, llm_times, bare_times = [], [], []
    for r in data["results"]:
        b_ms = r["brain_api"]["median_ms"] if r["brain_api"] else None
        b_method = r["brain_api"]["method"] if r["brain_api"] else ""
        l_ms = r["bare_llm"]["median_ms"] if r["bare_llm"] else None
        ratio = f"{b_ms/l_ms:.1f}x" if (b_ms and l_ms) else ""
        print(f"{r['query'][:54]:<55} {(str(round(b_ms)) if b_ms else 'N/A'):>10} {b_method:<15} {(str(round(l_ms)) if l_ms else 'N/A'):>8} {ratio:>10}")
        if b_ms:
            (cache_times if b_method == "facts_cache" else llm_times).append(b_ms)
        if l_ms:
            bare_times.append(l_ms)

    print("\n--- Averages ---")
    if cache_times:
        print(f"Brain API cache hits:    {statistics.median(cache_times):.0f}ms median ({len(cache_times)} queries)")
    if llm_times:
        print(f"Brain API LLM fallback:  {statistics.median(llm_times):.0f}ms median ({len(llm_times)} queries)")
    if bare_times:
        print(f"Bare LLM (OpenRouter):   {statistics.median(bare_times):.0f}ms median ({len(bare_times)} queries)")


def main():
    parser = argparse.ArgumentParser(description="Latency benchmark: Brain API vs bare LLM")
    parser.add_argument("--brain-api-url", default=None, help="Brain API base URL (e.g. http://127.0.0.1:8000)")
    parser.add_argument("--brain-api-key", default=None, help="Brain API key")
    parser.add_argument("--openrouter-key", default=None, help="OpenRouter API key")
    parser.add_argument("--model", default="meta-llama/llama-3.3-70b-instruct:free", help="OpenRouter model ID")
    parser.add_argument("--runs", type=int, default=3, help="Runs per query (default: 3, median taken)")
    parser.add_argument("--output", default=None, help="Save JSON results to file")
    args = parser.parse_args()

    if not args.brain_api_url and not args.openrouter_key:
        parser.error("Provide at least one of --brain-api-url or --openrouter-key")

    data = run_benchmark(args)
    print_summary(data)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nResults saved to {args.output}")
    else:
        print("\n\nFull JSON:")
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
