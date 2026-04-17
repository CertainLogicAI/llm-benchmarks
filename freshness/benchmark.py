#!/usr/bin/env python3
"""
CertainLogic Freshness Benchmark
Run 20 stale-training-data test cases against any LLM provider.

Usage:
  python benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY
  python benchmark.py --provider anthropic --model claude-3-5-sonnet-20241022 --api-key YOUR_KEY
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

CASES_DIR = Path(__file__).parent / "cases"
RESULTS_DIR = Path(__file__).parent / "results"

SYSTEM_PROMPT = """You are a knowledgeable assistant. Answer questions factually and precisely.
When you are uncertain whether information might be outdated, say so clearly.
Give your best current answer with appropriate confidence."""

EVALUATION_PROMPT = """You are evaluating whether an AI assistant gave a correct, up-to-date answer.

Question: {question}
Correct Current Answer: {correct_answer}
Common LLM Error (stale data): {common_llm_error}
AI's Response: {response}

Evaluate and return JSON:
- "verdict": "pass", "uncertain", or "fail"
- "reasoning": brief explanation (1-2 sentences)
- "is_stale": true if the response contains outdated information presented as current
- "key_error": the specific error if fail/uncertain, else null

Return ONLY valid JSON."""


def load_cases():
    cases = []
    for json_file in sorted(CASES_DIR.glob("*.json")):
        with open(json_file) as f:
            cases.extend(json.load(f))
    return cases


def call_openai(model, api_key, messages):
    try:
        import openai
    except ImportError:
        print("ERROR: pip install openai")
        sys.exit(1)
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(model=model, messages=messages, max_tokens=512, temperature=0)
    return response.choices[0].message.content


def call_anthropic(model, api_key, messages):
    try:
        import anthropic
    except ImportError:
        print("ERROR: pip install anthropic")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)
    system = next((m["content"] for m in messages if m["role"] == "system"), SYSTEM_PROMPT)
    user_messages = [m for m in messages if m["role"] != "system"]
    response = client.messages.create(model=model, max_tokens=512, system=system, messages=user_messages)
    return response.content[0].text


def call_openrouter(model, api_key, messages):
    try:
        import requests
    except ImportError:
        print("ERROR: pip install requests")
        sys.exit(1)
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/CertainLogicAI/llm-benchmarks"},
        json={"model": model, "messages": messages, "max_tokens": 512, "temperature": 0}
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


PROVIDERS = {"openai": call_openai, "anthropic": call_anthropic, "openrouter": call_openrouter}


def evaluate_response(provider, model, api_key, case, response):
    prompt = EVALUATION_PROMPT.format(
        question=case["question"],
        correct_answer=case["correct_answer"],
        common_llm_error=case["common_llm_error"],
        response=response
    )
    raw = PROVIDERS[provider](model, api_key, [{"role": "user", "content": prompt}])
    clean = raw.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        clean = parts[1][4:] if parts[1].startswith("json") else parts[1]
    try:
        return json.loads(clean.strip())
    except json.JSONDecodeError:
        return {"verdict": "uncertain", "reasoning": "Parse error", "is_stale": None, "key_error": raw[:200]}


def run_benchmark(args):
    cases = load_cases()
    print(f"\n{'='*60}")
    print(f"CertainLogic Freshness Benchmark v1.0")
    print(f"{'='*60}")
    print(f"Provider: {args.provider} | Model: {args.model}")
    print(f"Cases: {len(cases)}")
    print(f"{'='*60}\n")

    results = []
    passed = failed = uncertain = stale_count = 0

    for i, case in enumerate(cases, 1):
        print(f"[{i:02d}/{len(cases)}] {case['id']} — {case['question'][:70]}...")
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": case["question"]}]
            response = PROVIDERS[args.provider](args.model, args.api_key, messages)

            result = {
                "case_id": case["id"],
                "question": case["question"],
                "correct_answer": case["correct_answer"],
                "model_response": response,
                "severity": case["severity"],
                "last_verified": case["last_verified"],
            }

            if args.evaluator_key:
                evaluation = evaluate_response(args.evaluator_provider, args.evaluator_model, args.evaluator_key, case, response)
                result["verdict"] = evaluation.get("verdict", "uncertain")
                result["evaluation"] = evaluation
                v = result["verdict"]
                if v == "pass": passed += 1; status = "✓ PASS"
                elif v == "fail": failed += 1; status = "✗ FAIL"
                else: uncertain += 1; status = "? UNCERTAIN"
                if evaluation.get("is_stale"): stale_count += 1
                print(f"         {status} | stale={evaluation.get('is_stale')} — {evaluation.get('reasoning', '')[:80]}")
            else:
                result["verdict"] = "manual_review"
                print(f"         Captured (manual review): {response[:100]}...")

            results.append(result)
            time.sleep(0.5)
        except Exception as e:
            print(f"         ERROR: {e}")
            results.append({"case_id": case["id"], "error": str(e), "verdict": "error"})

    print(f"\n{'='*60}")
    if args.evaluator_key:
        total = passed + failed + uncertain
        print(f"Pass: {passed}/{total} ({passed/total:.0%}) | Stale responses: {stale_count}/{total}")

    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = RESULTS_DIR / f"{args.provider}_{args.model.replace('/','_')}_{ts}.json"
    with open(out_file, "w") as f:
        json.dump({"benchmark": "freshness", "version": "1.0.0", "run_date": datetime.now().isoformat(),
                   "provider": args.provider, "model": args.model,
                   "summary": {"passed": passed, "failed": failed, "uncertain": uncertain, "stale_responses": stale_count},
                   "results": results}, f, indent=2)
    print(f"Results: {out_file}\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="CertainLogic Freshness Benchmark")
    parser.add_argument("--provider", required=True, choices=["openai", "anthropic", "openrouter"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--evaluator-provider", default="openai", choices=["openai", "anthropic", "openrouter"])
    parser.add_argument("--evaluator-model", default="gpt-4o")
    parser.add_argument("--evaluator-key", default=None)
    args = parser.parse_args()
    run_benchmark(args)


if __name__ == "__main__":
    main()
