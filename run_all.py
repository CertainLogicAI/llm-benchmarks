#!/usr/bin/env python3
"""
CertainLogic LLM Benchmarks — Run All
Runs hallucination, freshness, and accuracy benchmarks sequentially
and outputs a combined summary report.

Usage:
  python run_all.py --provider openai --model gpt-4o --api-key YOUR_KEY
  python run_all.py --provider openai --model gpt-4o --api-key YOUR_KEY \
    --evaluator-key YOUR_EVAL_KEY
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BENCHMARKS = [
    ("hallucination", "hallucination/benchmark.py"),
    ("freshness", "freshness/benchmark.py"),
    ("accuracy", "accuracy/benchmark.py"),
]


def run_benchmark(script, args):
    """Run a benchmark script and return its latest results file."""
    cmd = [
        sys.executable, script,
        "--provider", args.provider,
        "--model", args.model,
        "--api-key", args.api_key,
    ]
    if args.evaluator_key:
        cmd += [
            "--evaluator-provider", args.evaluator_provider,
            "--evaluator-model", args.evaluator_model,
            "--evaluator-key", args.evaluator_key,
        ]

    print(f"\n{'#'*60}")
    print(f"# Running: {script}")
    print(f"{'#'*60}")

    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"WARNING: {script} exited with code {result.returncode}")

    # Find latest results file
    results_dir = Path(script).parent / "results"
    result_files = sorted(results_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if result_files:
        with open(result_files[0]) as f:
            return json.load(f)
    return None


def print_combined_report(all_results):
    print(f"\n{'='*70}")
    print("COMBINED BENCHMARK REPORT")
    print(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    print(f"{'Benchmark':<20} {'Cases':<8} {'Pass':<8} {'Fail':<8} {'Pass Rate':<12}")
    print("-" * 60)

    for name, data in all_results.items():
        if data is None:
            print(f"{name:<20} {'ERROR'}")
            continue
        s = data.get("summary", {})
        passed = s.get("passed", 0)
        failed = s.get("failed", 0)
        uncertain = s.get("uncertain", 0)
        total = passed + failed + uncertain
        rate = f"{passed/total:.0%}" if total else "n/a"
        print(f"{name:<20} {total:<8} {passed:<8} {failed:<8} {rate:<12}")

    print(f"\n{'='*70}")
    print("Full results in each benchmark's results/ directory.")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Run all CertainLogic benchmarks")
    parser.add_argument("--provider", required=True, choices=["openai", "anthropic", "openrouter"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--evaluator-provider", default="openai", choices=["openai", "anthropic", "openrouter"])
    parser.add_argument("--evaluator-model", default="gpt-4o")
    parser.add_argument("--evaluator-key", default=None)
    parser.add_argument("--skip", nargs="*", default=[], choices=["hallucination", "freshness", "accuracy"],
                        help="Skip specific benchmarks")
    args = parser.parse_args()

    all_results = {}
    for name, script in BENCHMARKS:
        if name in args.skip:
            print(f"Skipping: {name}")
            continue
        data = run_benchmark(script, args)
        all_results[name] = data

    print_combined_report(all_results)

    # Save combined report
    out = Path("results") if Path("results").exists() else Path(".")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_file = Path(f"combined_report_{ts}.json")
    with open(combined_file, "w") as f:
        json.dump({
            "run_date": datetime.now().isoformat(),
            "provider": args.provider,
            "model": args.model,
            "benchmarks": {k: v.get("summary") if v else None for k, v in all_results.items()}
        }, f, indent=2)
    print(f"Combined report: {combined_file}")


if __name__ == "__main__":
    main()
