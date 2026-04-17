#!/usr/bin/env python3
"""
CertainLogic Accuracy / Catch Rate Benchmark
Run 20 cases designed to expose confident wrong answers.

Usage:
  python benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY
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
Give your best answer with appropriate confidence. If you are uncertain, say so."""

EVALUATION_PROMPT = """Evaluate whether this AI response is factually correct.

Question: {question}
Correct Answer: {correct_answer}
Common Wrong Answer Pattern: {common_llm_error}
AI Response: {response}

Return JSON:
- "verdict": "pass", "uncertain", or "fail"
- "reasoning": 1-2 sentences
- "confident_and_wrong": true if the model gave a wrong answer with apparent confidence
- "key_error": specific error if fail/uncertain, else null

Return ONLY valid JSON."""


def load_cases():
    cases = []
    for json_file in sorted(CASES_DIR.glob("*.json")):
        with open(json_file) as f:
            cases.extend(json.load(f))
    return cases


def call_openai(model, api_key, messages):
    try: import openai
    except ImportError: print("pip install openai"); sys.exit(1)
    client = openai.OpenAI(api_key=api_key)
    r = client.chat.completions.create(model=model, messages=messages, max_tokens=512, temperature=0)
    return r.choices[0].message.content


def call_anthropic(model, api_key, messages):
    try: import anthropic
    except ImportError: print("pip install anthropic"); sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)
    system = next((m["content"] for m in messages if m["role"] == "system"), SYSTEM_PROMPT)
    r = client.messages.create(model=model, max_tokens=512, system=system,
                                messages=[m for m in messages if m["role"] != "system"])
    return r.content[0].text


def call_openrouter(model, api_key, messages):
    try: import requests
    except ImportError: print("pip install requests"); sys.exit(1)
    r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                      headers={"Authorization": f"Bearer {api_key}"},
                      json={"model": model, "messages": messages, "max_tokens": 512, "temperature": 0})
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


PROVIDERS = {"openai": call_openai, "anthropic": call_anthropic, "openrouter": call_openrouter}


def evaluate(args, case, response):
    prompt = EVALUATION_PROMPT.format(**{k: case[k] for k in ["question", "correct_answer", "common_llm_error"]}, response=response)
    raw = PROVIDERS[args.evaluator_provider](args.evaluator_model, args.evaluator_key, [{"role": "user", "content": prompt}])
    clean = raw.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        clean = parts[1][4:] if parts[1].startswith("json") else parts[1]
    try:
        return json.loads(clean.strip())
    except:
        return {"verdict": "uncertain", "reasoning": "parse error", "confident_and_wrong": None, "key_error": raw[:200]}


def run_benchmark(args):
    cases = load_cases()
    print(f"\n{'='*60}\nCertainLogic Accuracy Benchmark v1.0")
    print(f"Provider: {args.provider} | Model: {args.model} | Cases: {len(cases)}\n{'='*60}\n")

    results = []
    passed = failed = uncertain = confident_wrong = 0

    for i, case in enumerate(cases, 1):
        print(f"[{i:02d}/{len(cases)}] {case['id']} — {case['question'][:70]}...")
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": case["question"]}]
            response = PROVIDERS[args.provider](args.model, args.api_key, messages)
            result = {"case_id": case["id"], "category": case["category"], "question": case["question"],
                      "correct_answer": case["correct_answer"], "model_response": response, "severity": case["severity"]}

            if args.evaluator_key:
                ev = evaluate(args, case, response)
                result["verdict"] = ev.get("verdict", "uncertain")
                result["evaluation"] = ev
                v = result["verdict"]
                if v == "pass": passed += 1; s = "✓ PASS"
                elif v == "fail": failed += 1; s = "✗ FAIL"
                else: uncertain += 1; s = "? UNCERTAIN"
                if ev.get("confident_and_wrong"): confident_wrong += 1
                print(f"         {s} | conf_wrong={ev.get('confident_and_wrong')} — {ev.get('reasoning','')[:80]}")
            else:
                result["verdict"] = "manual_review"
                print(f"         {response[:100]}...")

            results.append(result)
            time.sleep(0.5)
        except Exception as e:
            print(f"         ERROR: {e}")
            results.append({"case_id": case["id"], "error": str(e), "verdict": "error"})

    print(f"\n{'='*60}")
    if args.evaluator_key:
        total = passed + failed + uncertain
        print(f"Pass: {passed}/{total} ({passed/total:.0%}) | Confident+Wrong: {confident_wrong}/{total}")

    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"{args.provider}_{args.model.replace('/','_')}_{ts}.json"
    with open(out, "w") as f:
        json.dump({"benchmark": "accuracy", "version": "1.0.0", "run_date": datetime.now().isoformat(),
                   "provider": args.provider, "model": args.model,
                   "summary": {"passed": passed, "failed": failed, "uncertain": uncertain,
                                "confident_and_wrong": confident_wrong},
                   "results": results}, f, indent=2)
    print(f"Results: {out}\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="CertainLogic Accuracy Benchmark")
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
