#!/usr/bin/env python3
"""
Count prompt tokens and estimate input cost with and without prompt caching.

Usage:
    python3 token_counter.py --provider estimate --file prompt.txt
    python3 token_counter.py --provider claude --model MODEL --file prompt.txt \
        --input-price IN --cache-write-price WRITE --cache-read-price READ --min-cache-tokens MIN

Providers:
    estimate  ~4 characters per token, no dependencies, no network
    claude    exact, Anthropic token counting endpoint (needs `anthropic`, ANTHROPIC_API_KEY)
    openai    exact, Responses input-token count endpoint (needs `openai`, OPENAI_API_KEY)
    gemini    exact, Gemini count_tokens (needs `google-genai`, GEMINI_API_KEY or GOOGLE_API_KEY)

The API providers call a token-counting endpoint, not the model. Prices, cache
minimums, and model IDs are passed in (per million tokens) - take them from
references/provider-facts.md and re-check the provider's pricing page.
"""

import argparse
import json
import sys
from pathlib import Path

DYNAMIC_MARKERS = [
    "{user", "{context", "{query", "{input", "{message",
    "{{", "[user", "[context", "[query", "[input",
    "<user>", "<context>", "<query>", "<input>", "<question>",
]


def find_dynamic_boundary(text: str) -> int:
    """Return the index where the first dynamic placeholder starts (len(text) if none)."""
    lowered = text.lower()
    positions = [lowered.find(marker) for marker in DYNAMIC_MARKERS]
    return min([p for p in positions if p != -1], default=len(text))


def count_estimate(text: str, model: str | None) -> int:
    return len(text) // 4


def count_claude(text: str, model: str | None) -> int:
    from anthropic import Anthropic

    client = Anthropic()
    response = client.messages.count_tokens(
        model=model,
        messages=[{"role": "user", "content": text}],
    )
    return response.input_tokens


def count_openai(text: str, model: str | None) -> int:
    from openai import OpenAI

    client = OpenAI()
    response = client.responses.input_tokens.count(model=model, input=text)
    return response.input_tokens


def count_gemini(text: str, model: str | None) -> int:
    from google import genai

    client = genai.Client()
    response = client.models.count_tokens(model=model, contents=text)
    return response.total_tokens


COUNTERS = {
    "estimate": (count_estimate, None),
    "claude": (count_claude, "anthropic"),
    "openai": (count_openai, "openai"),
    "gemini": (count_gemini, "google-genai"),
}


def per_mtok(tokens: int, price: float) -> float:
    return tokens / 1_000_000 * price


def calculate_costs(total: int, static: int, args: argparse.Namespace) -> dict | None:
    if args.input_price is None:
        return None
    dynamic = total - static
    costs = {"per_request_no_cache": per_mtok(total, args.input_price)}
    if args.cache_read_price is None:
        return costs

    write_price = args.cache_write_price if args.cache_write_price is not None else args.input_price
    miss = per_mtok(static, write_price) + per_mtok(dynamic, args.input_price)
    hit = per_mtok(static, args.cache_read_price) + per_mtok(dynamic, args.input_price)
    costs["cache_miss_write"] = miss
    costs["cache_hit"] = hit
    costs["monthly_no_cache"] = costs["per_request_no_cache"] * args.requests_per_month
    costs["monthly_with_cache"] = (
        args.hit_rate * hit + (1 - args.hit_rate) * miss
    ) * args.requests_per_month
    return costs


def analyze(text: str, args: argparse.Namespace) -> dict:
    counter, package = COUNTERS[args.provider]
    if args.provider != "estimate" and not args.model:
        return {"provider": args.provider, "error": "--model is required for API token counting"}

    boundary = find_dynamic_boundary(text)
    try:
        total = counter(text, args.model)
        if boundary == len(text):
            static = total
        elif boundary == 0:
            static = 0
        else:
            static = counter(text[:boundary], args.model)
    except ImportError:
        return {
            "provider": args.provider,
            "error": f"the `{package}` package is not installed in this Python environment; "
                     "use --provider estimate, or install a pinned, vetted version",
        }
    except Exception as e:
        return {"provider": args.provider, "error": f"{type(e).__name__}: {e}"}

    if args.min_cache_tokens is None:
        eligible = None
    else:
        eligible = static >= args.min_cache_tokens

    return {
        "provider": args.provider,
        "model": args.model,
        "method": "approximate (chars/4)" if args.provider == "estimate" else "provider token-count endpoint",
        "total_tokens": total,
        "static_prefix_tokens": static,
        "static_prefix_chars": boundary,
        "static_ratio_percent": round(static / total * 100, 1) if total else 0.0,
        "min_cache_tokens": args.min_cache_tokens,
        "cache_eligible": eligible,
        "costs": calculate_costs(total, static, args),
        "requests_per_month": args.requests_per_month,
        "hit_rate": args.hit_rate,
    }


def format_result(result: dict) -> str:
    if "error" in result:
        return f"Error ({result['provider']}): {result['error']}"

    label = result["provider"].upper() + (f" ({result['model']})" if result["model"] else "")
    lines = [
        "=" * 60,
        label,
        f"Method: {result['method']}",
        "=" * 60,
        f"Total input tokens: {result['total_tokens']:,}",
        f"Static prefix: {result['static_prefix_tokens']:,} tokens ({result['static_ratio_percent']}%)",
    ]

    if result["cache_eligible"] is None:
        lines.append("Cache eligible: unknown - pass --min-cache-tokens for the target model")
    else:
        verdict = "yes" if result["cache_eligible"] else "no - prefix is below the minimum and will not cache"
        lines.append(f"Cache eligible (minimum {result['min_cache_tokens']:,}): {verdict}")

    costs = result["costs"]
    if costs is None:
        lines.append("\nCost: pass --input-price (and cache prices) per million tokens to estimate")
        return "\n".join(lines)

    lines.extend([
        "\nInput cost per request (output tokens not included):",
        f"  Without caching: ${costs['per_request_no_cache']:.6f}",
    ])
    if "cache_hit" in costs:
        lines.extend([
            f"  Cache miss (writes prefix): ${costs['cache_miss_write']:.6f}",
            f"  Cache hit: ${costs['cache_hit']:.6f}",
            f"\nMonthly input cost ({result['requests_per_month']:,} requests, "
            f"{result['hit_rate']:.0%} hit rate):",
            f"  Without caching: ${costs['monthly_no_cache']:.2f}",
            f"  With caching: ${costs['monthly_with_cache']:.2f}",
        ])
        if result["cache_eligible"] is False:
            lines.append("  (Caching figures assume the prefix caches; it currently does not.)")
    else:
        lines.append("  Pass --cache-read-price to estimate caching savings")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Count prompt tokens and estimate input cost with prompt caching",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("text", nargs="?", help="Prompt text to analyze")
    parser.add_argument("--file", "-f", help="Read prompt from file")
    parser.add_argument("--provider", "-p", choices=list(COUNTERS), default="estimate")
    parser.add_argument("--model", "-m", help="Model ID (required for claude, openai, gemini)")
    parser.add_argument("--min-cache-tokens", type=int, help="Model's minimum cacheable prefix")
    parser.add_argument("--input-price", type=float, help="Uncached input price per million tokens")
    parser.add_argument("--cache-write-price", type=float,
                        help="Cache write price per million tokens (default: same as input)")
    parser.add_argument("--cache-read-price", type=float, help="Cache read price per million tokens")
    parser.add_argument("--requests-per-month", type=int, default=10_000)
    parser.add_argument("--hit-rate", type=float, default=0.95, help="Expected cache hit rate, 0-1")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.file:
        try:
            text = Path(args.file).read_text()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        print("Error: Provide prompt text or --file argument", file=sys.stderr)
        sys.exit(1)

    result = analyze(text, args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_result(result))
    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
