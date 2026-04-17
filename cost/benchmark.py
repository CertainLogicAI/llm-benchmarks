#!/usr/bin/env python3
"""
CertainLogic Cost Benchmark
Measures actual API cost per query under different caching conditions.

Usage:
  # Bare LLM (baseline)
  python benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY --queries queries.json

  # With simple semantic cache
  python benchmark.py --provider openai --model gpt-4o --api-key YOUR_KEY --queries queries.json \
    --enable-cache --cache-threshold 0.92
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"

# Approximate cost per 1M tokens (update as pricing changes)
PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-opus-4-6": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "default": {"input": 5.00, "output": 15.00},
}

DEFAULT_QUERIES = [
    "Write a FastAPI endpoint that creates a new user with email validation.",
    "Write a SQLAlchemy model for a Task with title, description, status, and created_at fields.",
    "How do I handle authentication with JWT tokens in FastAPI?",
    "Write a Pydantic v2 schema for creating a task with validation.",
    "How do I add pagination to a FastAPI list endpoint?",
    "Write a FastAPI endpoint that creates a new user with email validation.",  # duplicate
    "How do I handle authentication with JWT tokens in FastAPI?",               # duplicate
    "Write a SQLAlchemy model for a Task with title, description, status, and created_at fields.",  # dup
    "What is the correct way to configure CORS in FastAPI?",
    "How do I write async database queries with SQLAlchemy 2.0?",
]


def get_pricing(model):
    for key in PRICING:
        if key in model.lower():
            return PRICING[key]
    return PRICING["default"]


def call_openai(model, api_key, prompt):
    import openai
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0
    )
    usage = response.usage
    return {
        "response": response.choices[0].message.content,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
    }


def call_anthropic(model, api_key, prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model, max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "response": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


def call_openrouter(model, api_key, prompt):
    import requests
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}],
              "max_tokens": 1024, "temperature": 0, "usage": {"include": True}}
    )
    response.raise_for_status()
    data = response.json()
    usage = data.get("usage", {})
    return {
        "response": data["choices"][0]["message"]["content"],
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
    }


PROVIDERS = {"openai": call_openai, "anthropic": call_anthropic, "openrouter": call_openrouter}


def cosine_sim(a, b):
    """Simple cosine similarity for cache lookup."""
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x**2 for x in a))
    nb = math.sqrt(sum(x**2 for x in b))
    return dot / (na * nb) if na and nb else 0.0


def get_embedding(text, api_key):
    """Get embedding for cache lookup (OpenAI)."""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        r = client.embeddings.create(model="text-embedding-3-small", input=text)
        return r.data[0].embedding
    except Exception:
        return None


def run_benchmark(args):
    # Load queries
    if args.queries and Path(args.queries).exists():
        with open(args.queries) as f:
            queries = json.load(f)
    else:
        print("Using default query set (10 queries, 3 duplicates).")
        queries = DEFAULT_QUERIES

    pricing = get_pricing(args.model)
    provider_fn = PROVIDERS[args.provider]

    print(f"\n{'='*60}")
    print(f"CertainLogic Cost Benchmark v1.0")
    print(f"Provider: {args.provider} | Model: {args.model}")
    print(f"Queries: {len(queries)} | Cache: {'enabled' if args.enable_cache else 'disabled'}")
    print(f"{'='*60}\n")

    cache = []  # list of {embedding, response, query}
    results = []
    total_cost = 0.0
    cache_hits = 0

    for i, query in enumerate(queries, 1):
        print(f"[{i:02d}/{len(queries)}] {query[:70]}...")
        cache_hit = False
        response_text = None
        input_tokens = output_tokens = 0

        # Cache lookup
        if args.enable_cache and args.cache_key and cache:
            emb = get_embedding(query, args.cache_key)
            if emb:
                best_sim = 0
                best_cached = None
                for entry in cache:
                    sim = cosine_sim(emb, entry["embedding"])
                    if sim > best_sim:
                        best_sim = sim
                        best_cached = entry
                if best_sim >= args.cache_threshold:
                    cache_hit = True
                    cache_hits += 1
                    response_text = best_cached["response"]
                    print(f"         CACHE HIT (sim={best_sim:.3f}) — $0.00")

        if not cache_hit:
            try:
                result = provider_fn(args.model, args.api_key, query)
                response_text = result["response"]
                input_tokens = result.get("input_tokens", 0)
                output_tokens = result.get("output_tokens", 0)
                cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
                total_cost += cost
                print(f"         API call | in={input_tokens} out={output_tokens} | ${cost:.4f}")

                # Add to cache
                if args.enable_cache and args.cache_key:
                    emb = get_embedding(query, args.cache_key)
                    if emb:
                        cache.append({"query": query, "response": response_text, "embedding": emb})

                time.sleep(0.3)
            except Exception as e:
                print(f"         ERROR: {e}")
                response_text = f"ERROR: {e}"

        results.append({
            "query_index": i,
            "query": query,
            "cache_hit": cache_hit,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": 0.0 if cache_hit else (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000,
            "response_preview": (response_text or "")[:200],
        })

    total = len(queries)
    hit_rate = cache_hits / total if total else 0

    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"Total cost:    ${total_cost:.4f}")
    print(f"Cache hits:    {cache_hits}/{total} ({hit_rate:.0%})")
    print(f"Cost if no cache: ${sum(r['cost_usd'] for r in results if not r['cache_hit']) + (cache_hits * total_cost / max(total - cache_hits, 1)):.4f} (projected)")
    print(f"{'='*60}\n")

    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"cost_{args.provider}_{ts}.json"
    with open(out, "w") as f:
        json.dump({
            "benchmark": "cost", "version": "1.0.0", "run_date": datetime.now().isoformat(),
            "provider": args.provider, "model": args.model,
            "cache_enabled": args.enable_cache, "cache_threshold": args.cache_threshold,
            "summary": {"total_cost_usd": total_cost, "cache_hits": cache_hits,
                        "total_queries": total, "cache_hit_rate": hit_rate},
            "results": results
        }, f, indent=2)
    print(f"Results: {out}")


def main():
    parser = argparse.ArgumentParser(description="CertainLogic Cost Benchmark")
    parser.add_argument("--provider", required=True, choices=["openai", "anthropic", "openrouter"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--queries", default=None, help="JSON file with list of query strings")
    parser.add_argument("--enable-cache", action="store_true", help="Enable semantic cache simulation")
    parser.add_argument("--cache-key", default=None, help="OpenAI API key for embeddings (cache)")
    parser.add_argument("--cache-threshold", type=float, default=0.92, help="Cosine similarity threshold (default 0.92)")
    args = parser.parse_args()
    run_benchmark(args)


if __name__ == "__main__":
    main()
