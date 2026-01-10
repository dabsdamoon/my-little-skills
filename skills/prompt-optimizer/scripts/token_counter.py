#!/usr/bin/env python3
"""
Token counter for multiple LLM providers.

Usage:
    python token_counter.py "<prompt_text>" --provider claude
    python token_counter.py --file prompt.txt --provider openai
    python token_counter.py "<prompt_text>" --provider all

Requirements:
    - Claude: pip install anthropic
    - OpenAI/Gemini: pip install tiktoken
"""

import argparse
import sys
from pathlib import Path


# Pricing per 1M tokens (as of Dec 2024)
PRICING = {
    "claude": {
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30},
        "claude-3-5-haiku": {"input": 1.00, "output": 5.00, "cache_write": 1.25, "cache_read": 0.10},
        "claude-3-opus": {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    },
    "openai": {
        "gpt-4o": {"input": 2.50, "output": 10.00, "cached": 1.25},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60, "cached": 0.075},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    },
    "gemini": {
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00, "cached": 0.3125},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30, "cached": 0.01875},
    },
}

# Cache minimums (tokens)
CACHE_MINIMUMS = {
    "claude": {"sonnet": 1024, "haiku": 1024, "opus": 2048},
    "openai": {"default": 0},  # Automatic caching
    "gemini": {"default": 32768},  # 32K minimum for context caching
}


def count_tokens_claude(text: str) -> dict:
    """Count tokens using Anthropic's tokenizer."""
    try:
        from anthropic import Anthropic
        client = Anthropic()
        count = client.count_tokens(text)
        return {
            "provider": "claude",
            "tokens": count,
            "model": "claude-3-5-sonnet",
            "pricing": PRICING["claude"]["claude-3-5-sonnet"],
            "cache_minimum": CACHE_MINIMUMS["claude"]["sonnet"],
        }
    except ImportError:
        return {"error": "anthropic package not installed. Run: pip install anthropic"}
    except Exception as e:
        return {"error": str(e)}


def count_tokens_openai(text: str) -> dict:
    """Count tokens using tiktoken (OpenAI's tokenizer)."""
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model("gpt-4o")
        tokens = enc.encode(text)
        return {
            "provider": "openai",
            "tokens": len(tokens),
            "model": "gpt-4o",
            "pricing": PRICING["openai"]["gpt-4o"],
            "cache_minimum": CACHE_MINIMUMS["openai"]["default"],
        }
    except ImportError:
        return {"error": "tiktoken package not installed. Run: pip install tiktoken"}
    except Exception as e:
        return {"error": str(e)}


def count_tokens_gemini(text: str) -> dict:
    """Estimate tokens for Gemini (uses similar tokenization to GPT-4)."""
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model("gpt-4")
        tokens = enc.encode(text)
        return {
            "provider": "gemini",
            "tokens": len(tokens),
            "model": "gemini-1.5-pro",
            "pricing": PRICING["gemini"]["gemini-1.5-pro"],
            "cache_minimum": CACHE_MINIMUMS["gemini"]["default"],
            "note": "Token count estimated using tiktoken (approximate)",
        }
    except ImportError:
        return {"error": "tiktoken package not installed. Run: pip install tiktoken"}
    except Exception as e:
        return {"error": str(e)}


def find_dynamic_boundary(text: str) -> int:
    """Find where dynamic content begins in the prompt."""
    markers = [
        "{user", "{context", "{query", "{input", "{message",
        "{{", "[USER", "[CONTEXT", "[QUERY", "[INPUT",
        "<user>", "<context>", "<query>", "<input>",
    ]
    first_pos = len(text)
    for marker in markers:
        pos = text.lower().find(marker.lower())
        if pos != -1 and pos < first_pos:
            first_pos = pos
    return first_pos


def analyze_cache_potential(text: str, tokens: int, cache_minimum: int) -> dict:
    """Analyze caching potential of the prompt."""
    boundary = find_dynamic_boundary(text)
    static_ratio = boundary / len(text) if len(text) > 0 else 0
    estimated_static_tokens = int(tokens * static_ratio)

    cache_eligible = estimated_static_tokens >= cache_minimum

    return {
        "static_prefix_chars": boundary,
        "estimated_static_tokens": estimated_static_tokens,
        "static_ratio": round(static_ratio * 100, 1),
        "cache_eligible": cache_eligible,
        "cache_minimum": cache_minimum,
    }


def calculate_costs(tokens: int, pricing: dict, cache_info: dict) -> dict:
    """Calculate costs with and without caching."""
    input_cost = (tokens / 1_000_000) * pricing["input"]

    costs = {
        "per_request_no_cache": round(input_cost, 6),
    }

    if cache_info["cache_eligible"]:
        static_tokens = cache_info["estimated_static_tokens"]
        dynamic_tokens = tokens - static_tokens

        # First request (cache write)
        if "cache_write" in pricing:
            cache_write_cost = (static_tokens / 1_000_000) * pricing["cache_write"]
            dynamic_cost = (dynamic_tokens / 1_000_000) * pricing["input"]
            costs["first_request_with_cache"] = round(cache_write_cost + dynamic_cost, 6)

        # Subsequent requests (cache read)
        cache_read_price = pricing.get("cache_read", pricing.get("cached", pricing["input"] * 0.5))
        cache_read_cost = (static_tokens / 1_000_000) * cache_read_price
        dynamic_cost = (dynamic_tokens / 1_000_000) * pricing["input"]
        costs["subsequent_with_cache"] = round(cache_read_cost + dynamic_cost, 6)

        # Savings
        if costs["per_request_no_cache"] > 0:
            savings_pct = ((costs["per_request_no_cache"] - costs["subsequent_with_cache"])
                          / costs["per_request_no_cache"] * 100)
            costs["cache_savings_percent"] = round(savings_pct, 1)

    return costs


def format_result(result: dict, text: str) -> str:
    """Format the result for display."""
    if "error" in result:
        return f"Error ({result.get('provider', 'unknown')}): {result['error']}"

    lines = [
        f"\n{'='*60}",
        f"Provider: {result['provider'].upper()} ({result['model']})",
        f"{'='*60}",
        f"Total tokens: {result['tokens']:,}",
    ]

    # Cache analysis
    cache_info = analyze_cache_potential(text, result["tokens"], result["cache_minimum"])
    lines.extend([
        f"\nCache Analysis:",
        f"  Static prefix: ~{cache_info['estimated_static_tokens']:,} tokens ({cache_info['static_ratio']}%)",
        f"  Minimum for caching: {cache_info['cache_minimum']:,} tokens",
        f"  Cache eligible: {'Yes' if cache_info['cache_eligible'] else 'No'}",
    ])

    # Cost analysis
    costs = calculate_costs(result["tokens"], result["pricing"], cache_info)
    lines.extend([
        f"\nCost Analysis (per request):",
        f"  Without caching: ${costs['per_request_no_cache']:.6f}",
    ])

    if cache_info["cache_eligible"]:
        if "first_request_with_cache" in costs:
            lines.append(f"  First request (cache write): ${costs['first_request_with_cache']:.6f}")
        lines.extend([
            f"  Subsequent (cache hit): ${costs['subsequent_with_cache']:.6f}",
            f"  Savings with cache: {costs.get('cache_savings_percent', 0):.1f}%",
        ])

    # Monthly estimate
    lines.extend([
        f"\nMonthly Estimates (10,000 requests):",
        f"  Without caching: ${costs['per_request_no_cache'] * 10000:.2f}",
    ])
    if cache_info["cache_eligible"] and "subsequent_with_cache" in costs:
        monthly_cached = costs["subsequent_with_cache"] * 10000
        lines.append(f"  With caching (95% hit rate): ${monthly_cached * 0.95 + costs['per_request_no_cache'] * 0.05 * 10000:.2f}")

    if "note" in result:
        lines.append(f"\nNote: {result['note']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Count tokens and analyze caching potential for LLM prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python token_counter.py "Your prompt text here" --provider claude
    python token_counter.py --file prompt.txt --provider openai
    python token_counter.py "Your prompt" --provider all
        """
    )
    parser.add_argument("text", nargs="?", help="Prompt text to analyze")
    parser.add_argument("--file", "-f", help="Read prompt from file")
    parser.add_argument(
        "--provider", "-p",
        choices=["claude", "openai", "gemini", "all"],
        default="all",
        help="LLM provider (default: all)"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Get text
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

    # Count tokens
    providers = [args.provider] if args.provider != "all" else ["claude", "openai", "gemini"]
    results = []

    for provider in providers:
        if provider == "claude":
            result = count_tokens_claude(text)
        elif provider == "openai":
            result = count_tokens_openai(text)
        elif provider == "gemini":
            result = count_tokens_gemini(text)
        results.append(result)

    # Output
    if args.json:
        import json
        output = []
        for result in results:
            if "error" not in result:
                cache_info = analyze_cache_potential(text, result["tokens"], result["cache_minimum"])
                costs = calculate_costs(result["tokens"], result["pricing"], cache_info)
                result["cache_analysis"] = cache_info
                result["cost_analysis"] = costs
            output.append(result)
        print(json.dumps(output, indent=2))
    else:
        for result in results:
            print(format_result(result, text))


if __name__ == "__main__":
    main()
