#!/usr/bin/env python3
"""
Validate cache-friendly prompt structure.

Usage:
    python cache_structure_validator.py --prompt prompt.txt
    python cache_structure_validator.py --prompt prompt.txt --provider claude
    python cache_structure_validator.py "<prompt_text>" --provider openai
"""

import argparse
import re
import sys
from pathlib import Path


# Cache requirements by provider
CACHE_REQUIREMENTS = {
    "claude": {
        "minimum_tokens": 1024,
        "ttl_minutes": 5,
        "max_breakpoints": 4,
        "description": "Explicit caching with cache_control parameter",
    },
    "openai": {
        "minimum_tokens": 0,
        "ttl_minutes": None,  # Automatic
        "max_breakpoints": None,
        "description": "Automatic caching (no explicit control)",
    },
    "gemini": {
        "minimum_tokens": 32768,
        "ttl_minutes": 60,
        "max_breakpoints": 1,
        "description": "Context caching API with storage costs",
    },
}

# Dynamic content markers
DYNAMIC_PATTERNS = [
    (r"\{([a-z_]+)\}", "Template variable: {%s}"),
    (r"\{\{([a-z_]+)\}\}", "Double-brace variable: {{%s}}"),
    (r"\[USER[^\]]*\]", "User placeholder"),
    (r"\[CONTEXT[^\]]*\]", "Context placeholder"),
    (r"\[QUERY[^\]]*\]", "Query placeholder"),
    (r"\[INPUT[^\]]*\]", "Input placeholder"),
    (r"<user>.*?</user>", "XML user tag"),
    (r"<context>.*?</context>", "XML context tag"),
    (r"<query>.*?</query>", "XML query tag"),
    (r"\$\{([^}]+)\}", "Shell-style variable: ${%s}"),
    (r"__([A-Z_]+)__", "Dunder placeholder: __%s__"),
]

# Anti-patterns that break caching
CACHE_BREAKERS = [
    (r"\d{4}-\d{2}-\d{2}", "Hardcoded date (YYYY-MM-DD)"),
    (r"\d{1,2}/\d{1,2}/\d{2,4}", "Hardcoded date (MM/DD/YYYY)"),
    (r"(today|now|current date)", "Temporal reference"),
    (r"user[_-]?id:\s*\S+", "User ID"),
    (r"session[_-]?id:\s*\S+", "Session ID"),
    (r"request[_-]?id:\s*\S+", "Request ID"),
    (r"uuid:\s*[a-f0-9-]+", "UUID"),
    (r"timestamp:\s*\d+", "Timestamp"),
]


def estimate_tokens(text: str) -> int:
    """Rough token estimate (4 chars = 1 token)."""
    return len(text) // 4


def find_dynamic_boundary(text: str) -> tuple[int, list]:
    """Find where dynamic content begins and list all dynamic markers."""
    markers_found = []
    first_position = len(text)

    for pattern, description in DYNAMIC_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL):
            if match.groups():
                desc = description % match.group(1) if "%s" in description else description
            else:
                desc = description
            markers_found.append({
                "position": match.start(),
                "text": match.group()[:50],
                "type": desc,
            })
            if match.start() < first_position:
                first_position = match.start()

    return first_position, sorted(markers_found, key=lambda x: x["position"])


def find_cache_breakers(text: str) -> list:
    """Find patterns that may break caching."""
    breakers = []

    for pattern, description in CACHE_BREAKERS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            breakers.append({
                "position": match.start(),
                "text": match.group()[:50],
                "issue": description,
            })

    return sorted(breakers, key=lambda x: x["position"])


def suggest_breakpoints(text: str, provider: str) -> list:
    """Suggest optimal cache breakpoints."""
    suggestions = []
    lines = text.split('\n')

    # Find section boundaries
    section_patterns = [
        (r'^\s*#', "Markdown header"),
        (r'^\s*\[.+\]\s*$', "Section marker"),
        (r'^-{3,}$', "Horizontal rule"),
        (r'^={3,}$', "Double horizontal rule"),
        (r'^\s*<[a-z]+>\s*$', "XML opening tag"),
    ]

    current_pos = 0
    for i, line in enumerate(lines):
        for pattern, desc in section_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                tokens_so_far = estimate_tokens(text[:current_pos])
                if tokens_so_far >= CACHE_REQUIREMENTS[provider]["minimum_tokens"]:
                    suggestions.append({
                        "line": i + 1,
                        "position": current_pos,
                        "tokens_before": tokens_so_far,
                        "reason": f"After {desc}",
                        "text_preview": line[:40],
                    })
        current_pos += len(line) + 1  # +1 for newline

    # Limit to max breakpoints
    max_bp = CACHE_REQUIREMENTS[provider].get("max_breakpoints")
    if max_bp and len(suggestions) > max_bp:
        # Keep evenly distributed breakpoints
        step = len(suggestions) // max_bp
        suggestions = [suggestions[i * step] for i in range(max_bp)]

    return suggestions


def validate(text: str, provider: str) -> dict:
    """Validate cache structure for given provider."""
    requirements = CACHE_REQUIREMENTS[provider]
    total_tokens = estimate_tokens(text)

    # Find dynamic boundary
    boundary, dynamic_markers = find_dynamic_boundary(text)
    static_tokens = estimate_tokens(text[:boundary])

    # Find cache breakers
    breakers = find_cache_breakers(text)
    early_breakers = [b for b in breakers if b["position"] < boundary]

    # Validation checks
    checks = []

    # Check 1: Minimum tokens
    min_tokens = requirements["minimum_tokens"]
    if min_tokens > 0:
        if static_tokens >= min_tokens:
            checks.append({
                "check": "Minimum token threshold",
                "status": "PASS",
                "detail": f"Static prefix ({static_tokens} tokens) >= minimum ({min_tokens})",
            })
        else:
            checks.append({
                "check": "Minimum token threshold",
                "status": "FAIL",
                "detail": f"Static prefix ({static_tokens} tokens) < minimum ({min_tokens})",
            })

    # Check 2: Static ratio
    static_ratio = static_tokens / total_tokens if total_tokens > 0 else 0
    if static_ratio >= 0.5:
        checks.append({
            "check": "Static content ratio",
            "status": "PASS",
            "detail": f"{static_ratio*100:.1f}% of prompt is cacheable",
        })
    else:
        checks.append({
            "check": "Static content ratio",
            "status": "WARN",
            "detail": f"Only {static_ratio*100:.1f}% cacheable (aim for >50%)",
        })

    # Check 3: Cache breakers in static section
    if early_breakers:
        checks.append({
            "check": "Cache-breaking patterns",
            "status": "FAIL",
            "detail": f"Found {len(early_breakers)} cache-breaking patterns in static section",
        })
    else:
        checks.append({
            "check": "Cache-breaking patterns",
            "status": "PASS",
            "detail": "No cache-breaking patterns in static section",
        })

    # Check 4: Dynamic content position
    if boundary > len(text) * 0.3:
        checks.append({
            "check": "Dynamic content position",
            "status": "PASS",
            "detail": "Dynamic content appears after 30% of prompt",
        })
    else:
        checks.append({
            "check": "Dynamic content position",
            "status": "WARN",
            "detail": f"Dynamic content starts early (position {boundary}/{len(text)})",
        })

    # Overall validity
    failures = [c for c in checks if c["status"] == "FAIL"]
    warnings = [c for c in checks if c["status"] == "WARN"]

    if failures:
        overall = "INVALID"
    elif warnings:
        overall = "VALID_WITH_WARNINGS"
    else:
        overall = "VALID"

    # Get breakpoint suggestions
    breakpoints = suggest_breakpoints(text, provider)

    return {
        "provider": provider,
        "provider_description": requirements["description"],
        "overall_status": overall,
        "checks": checks,
        "metrics": {
            "total_tokens": total_tokens,
            "static_tokens": static_tokens,
            "static_ratio_percent": round(static_ratio * 100, 1),
            "minimum_required": min_tokens,
            "dynamic_markers_count": len(dynamic_markers),
            "cache_breakers_count": len(breakers),
        },
        "dynamic_markers": dynamic_markers[:10],
        "cache_breakers": early_breakers[:5],
        "suggested_breakpoints": breakpoints[:4],
    }


def format_result(result: dict) -> str:
    """Format validation result for display."""
    lines = [
        "=" * 60,
        f"CACHE STRUCTURE VALIDATION - {result['provider'].upper()}",
        f"({result['provider_description']})",
        "=" * 60,
        "",
        f"Overall Status: {result['overall_status']}",
        "",
        "VALIDATION CHECKS:",
    ]

    for check in result["checks"]:
        status_icon = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN"}[check["status"]]
        lines.append(f"  [{status_icon}] {check['check']}")
        lines.append(f"        {check['detail']}")

    lines.extend([
        "",
        "METRICS:",
        f"  Total tokens: ~{result['metrics']['total_tokens']:,}",
        f"  Static prefix: ~{result['metrics']['static_tokens']:,} tokens ({result['metrics']['static_ratio_percent']}%)",
        f"  Minimum required: {result['metrics']['minimum_required']:,} tokens",
    ])

    if result["cache_breakers"]:
        lines.extend(["", "CACHE BREAKERS FOUND:"])
        for breaker in result["cache_breakers"]:
            lines.append(f"  - {breaker['issue']}: '{breaker['text']}'")

    if result["dynamic_markers"]:
        lines.extend(["", "DYNAMIC MARKERS:"])
        for marker in result["dynamic_markers"][:5]:
            lines.append(f"  - {marker['type']} at position {marker['position']}")

    if result["suggested_breakpoints"]:
        lines.extend(["", "SUGGESTED CACHE BREAKPOINTS:"])
        for bp in result["suggested_breakpoints"]:
            lines.append(f"  - Line {bp['line']} (~{bp['tokens_before']} tokens): {bp['reason']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate cache-friendly prompt structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python cache_structure_validator.py --prompt prompt.txt
    python cache_structure_validator.py --prompt prompt.txt --provider openai
    python cache_structure_validator.py "Your prompt" --provider gemini
        """
    )
    parser.add_argument("text", nargs="?", help="Prompt text to validate")
    parser.add_argument("--prompt", "-p", help="Read prompt from file")
    parser.add_argument(
        "--provider",
        choices=["claude", "openai", "gemini"],
        default="claude",
        help="Target provider (default: claude)"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Get text
    if args.prompt:
        try:
            text = Path(args.prompt).read_text()
        except FileNotFoundError:
            print(f"Error: File not found: {args.prompt}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        print("Error: Provide prompt text or --prompt argument", file=sys.stderr)
        sys.exit(1)

    # Validate
    result = validate(text, args.provider)

    # Output
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print(format_result(result))

    # Exit code based on status
    if result["overall_status"] == "INVALID":
        sys.exit(1)
    elif result["overall_status"] == "VALID_WITH_WARNINGS":
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
