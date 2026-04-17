#!/usr/bin/env python3
"""
CertainLogic Hallucination Benchmark
Run 30 real hallucination test cases against any LLM provider.

Usage:
  python benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY
  python benchmark.py --provider anthropic --model claude-3-5-sonnet-20241022 --api-key YOUR_KEY
  python benchmark.py --provider openrouter --model meta-llama/llama-3.3-70b-instruct:free --api-key YOUR_KEY

Results are saved to results/<provider>_<model>_<timestamp>.json
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path


CASES_DIR = Path(__file__).parent / "cases"
RESULTS_DIR = Path(__file__).parent / "results"

SYSTEM_PROMPT = """You are a knowledgeable assistant. Answer questions factually and precisely. 
If you are uncertain or if information may be outdated, say so clearly. 
Do not hedge unnecessarily — give your best answer with appropriate confidence."""

EVALUATION_PROMPT = """You are evaluating whether an AI assistant's answer to a factual question is correct.

Question: {question}
Correct Answer (ground truth): {correct_answer}
Common Hallucination Pattern: {common_hallucination}
AI's Response: {response}

Evaluate the AI's response and return a JSON object with:
- "verdict": one of "pass", "uncertain", or "fail"
- "reasoning": brief explanation (1-2 sentences)
- "contains_hallucination": true/false
- "key_error": the specific error if verdict is fail or uncertain, else null

A "pass" means the response contains the correct material facts without dangerous omissions.
A "fail" means the response contains a material factual error or dangerous omission.
An "uncertain" means the response is incomplete or ambiguous in a way that could mislead.

Return ONLY valid JSON, no other text."""


def load_cases():
    """Load all benchmark cases from the cases/ directory."""
    cases = []
    for json_file in sorted(CASES_DIR.glob("*.json")):
        with open(json_file) as f:
            category_cases = json.load(f)
            cases.extend(category_cases)
    return cases


def call_openai(model, api_key, messages):
    """Call OpenAI API."""
    try:
        import openai
    except ImportError:
        print("ERROR: openai package not installed. Run: pip install openai")
        sys.exit(1)

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=512,
        temperature=0
    )
    return response.choices[0].message.content


def call_anthropic(model, api_key, messages):
    """Call Anthropic API."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    system = messages[0]["content"] if messages[0]["role"] == "system" else SYSTEM_PROMPT
    user_messages = [m for m in messages if m["role"] != "system"]

    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=system,
        messages=user_messages
    )
    return response.content[0].text


def call_openrouter(model, api_key, messages):
    """Call OpenRouter API (OpenAI-compatible)."""
    try:
        import requests
    except ImportError:
        print("ERROR: requests package not installed. Run: pip install requests")
        sys.exit(1)

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/CertainLogicAI/hallucination-benchmark",
            "X-Title": "CertainLogic Hallucination Benchmark"
        },
        json={
            "model": model,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0
        }
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


PROVIDERS = {
    "openai": call_openai,
    "anthropic": call_anthropic,
    "openrouter": call_openrouter
}


def get_model_response(provider, model, api_key, question):
    """Get a response from the specified LLM."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    call_fn = PROVIDERS[provider]
    return call_fn(model, api_key, messages)


def evaluate_response(evaluator_provider, evaluator_model, evaluator_key, case, response):
    """Use an LLM to evaluate whether the response is correct."""
    prompt = EVALUATION_PROMPT.format(
        question=case["question"],
        correct_answer=case["correct_answer"],
        common_hallucination=case["common_hallucination"],
        response=response
    )
    messages = [
        {"role": "user", "content": prompt}
    ]
    call_fn = PROVIDERS[evaluator_provider]
    eval_response = call_fn(evaluator_model, evaluator_key, messages)

    # Strip markdown code blocks if present
    clean = eval_response.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {
            "verdict": "uncertain",
            "reasoning": "Could not parse evaluator response",
            "contains_hallucination": None,
            "key_error": eval_response[:200]
        }


def run_benchmark(args):
    """Main benchmark runner."""
    cases = load_cases()
    print(f"\n{'='*60}")
    print(f"CertainLogic Hallucination Benchmark v1.0")
    print(f"{'='*60}")
    print(f"Provider: {args.provider} | Model: {args.model}")
    print(f"Cases: {len(cases)} total")

    if args.evaluator_key:
        print(f"Auto-evaluator: {args.evaluator_provider} / {args.evaluator_model}")
    else:
        print("Mode: Manual review (no evaluator key provided)")

    print(f"{'='*60}\n")

    results = []
    passed = 0
    failed = 0
    uncertain = 0

    for i, case in enumerate(cases, 1):
        print(f"[{i:02d}/{len(cases)}] {case['id']} — {case['question'][:70]}...")

        try:
            response = get_model_response(args.provider, args.model, args.api_key, case["question"])

            result = {
                "case_id": case["id"],
                "category": case["category"],
                "question": case["question"],
                "correct_answer": case["correct_answer"],
                "model_response": response,
                "severity": case["severity"],
                "tags": case["tags"]
            }

            if args.evaluator_key:
                evaluation = evaluate_response(
                    args.evaluator_provider, args.evaluator_model, args.evaluator_key,
                    case, response
                )
                result["verdict"] = evaluation.get("verdict", "uncertain")
                result["evaluation"] = evaluation

                verdict = result["verdict"]
                if verdict == "pass":
                    passed += 1
                    status = "✓ PASS"
                elif verdict == "fail":
                    failed += 1
                    status = "✗ FAIL"
                else:
                    uncertain += 1
                    status = "? UNCERTAIN"

                print(f"         {status} — {evaluation.get('reasoning', '')[:80]}")
            else:
                result["verdict"] = "manual_review"
                print(f"         Response captured (manual review required)")
                print(f"         Model said: {response[:100]}...")

            results.append(result)

            # Rate limit courtesy pause
            time.sleep(0.5)

        except Exception as e:
            print(f"         ERROR: {e}")
            results.append({
                "case_id": case["id"],
                "category": case["category"],
                "error": str(e),
                "verdict": "error"
            })

    # Summary
    print(f"\n{'='*60}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*60}")

    if args.evaluator_key:
        total_scored = passed + failed + uncertain
        pass_rate = passed / total_scored if total_scored > 0 else 0
        print(f"Pass:      {passed:3d} / {total_scored} ({pass_rate:.0%})")
        print(f"Fail:      {failed:3d} / {total_scored}")
        print(f"Uncertain: {uncertain:3d} / {total_scored}")

        # By category
        print(f"\nBy category:")
        categories = {}
        for r in results:
            cat = r.get("category", "unknown")
            if cat not in categories:
                categories[cat] = {"pass": 0, "fail": 0, "uncertain": 0, "total": 0}
            categories[cat]["total"] += 1
            v = r.get("verdict", "uncertain")
            if v in categories[cat]:
                categories[cat][v] += 1

        for cat, stats in sorted(categories.items()):
            rate = stats["pass"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  {cat:<12} {stats['pass']}/{stats['total']} ({rate:.0%})")

    # Save results
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_safe = args.model.replace("/", "_").replace(":", "_")
    output_file = RESULTS_DIR / f"{args.provider}_{model_safe}_{timestamp}.json"

    output = {
        "benchmark_version": "1.0.0",
        "run_date": datetime.now().isoformat(),
        "provider": args.provider,
        "model": args.model,
        "cases_total": len(cases),
        "summary": {
            "passed": passed,
            "failed": failed,
            "uncertain": uncertain,
            "pass_rate": passed / (passed + failed + uncertain) if (passed + failed + uncertain) > 0 else None
        },
        "results": results
    }

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print(f"\nLearn more: https://certainlogic.ai")
    print(f"{'='*60}\n")

    return output


def main():
    parser = argparse.ArgumentParser(
        description="CertainLogic Hallucination Benchmark — test any LLM against 30 real hallucination cases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmark.py --provider openai --model gpt-4o --api-key sk-...
  python benchmark.py --provider anthropic --model claude-3-5-sonnet-20241022 --api-key sk-ant-...
  python benchmark.py --provider openrouter --model meta-llama/llama-3.3-70b-instruct:free --api-key sk-or-...

Auto-evaluation (uses a second LLM to score responses automatically):
  python benchmark.py --provider openai --model gpt-4o --api-key sk-... \\
    --evaluator-provider openai --evaluator-model gpt-4o --evaluator-key sk-...

Without --evaluator-key, responses are captured for manual review.
        """
    )
    parser.add_argument("--provider", required=True, choices=["openai", "anthropic", "openrouter"],
                        help="LLM provider to test")
    parser.add_argument("--model", required=True, help="Model name/ID to test")
    parser.add_argument("--api-key", required=True, help="API key for the provider")

    parser.add_argument("--evaluator-provider", default="openai",
                        choices=["openai", "anthropic", "openrouter"],
                        help="Provider for auto-evaluation (default: openai)")
    parser.add_argument("--evaluator-model", default="gpt-4o",
                        help="Model for auto-evaluation (default: gpt-4o)")
    parser.add_argument("--evaluator-key", default=None,
                        help="API key for evaluator (enables auto-scoring; omit for manual review)")

    parser.add_argument("--category", default=None,
                        choices=["medical", "legal", "financial", "technical", "general"],
                        help="Run only cases from a specific category")

    args = parser.parse_args()
    run_benchmark(args)


if __name__ == "__main__":
    main()
