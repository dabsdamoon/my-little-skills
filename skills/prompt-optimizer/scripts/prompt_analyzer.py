#!/usr/bin/env python3
"""
Comprehensive prompt analyzer for optimization opportunities.

Usage:
    python prompt_analyzer.py --input prompt.txt
    python prompt_analyzer.py --input prompt.txt --output analysis.json
    python prompt_analyzer.py "<prompt_text>"

Note: This script uses basic analysis. For entropy-based analysis,
install transformers (large dependency: ~2GB).
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


# Verbose phrases that can be condensed
VERBOSE_PATTERNS = {
    r"i would like you to": "",
    r"please make sure to": "",
    r"you must always": "always",
    r"you should remember to": "",
    r"it is important that": "",
    r"make sure that you": "",
    r"could you please": "",
    r"in order to": "to",
    r"at this point in time": "now",
    r"due to the fact that": "because",
    r"in the event that": "if",
    r"for the purpose of": "to",
    r"with regard to": "about",
    r"in spite of the fact that": "although",
    r"at the present time": "now",
    r"until such time as": "until",
    r"in a manner that": "so that",
    r"on a regular basis": "regularly",
    r"in close proximity to": "near",
}

# Dynamic content markers
DYNAMIC_MARKERS = [
    r"\{[a-z_]+\}",  # {variable}
    r"\{\{[a-z_]+\}\}",  # {{variable}}
    r"\[USER[^\]]*\]",  # [USER...]
    r"\[CONTEXT[^\]]*\]",  # [CONTEXT...]
    r"\[QUERY[^\]]*\]",  # [QUERY...]
    r"\[INPUT[^\]]*\]",  # [INPUT...]
    r"<user>",  # <user>
    r"<context>",  # <context>
    r"<query>",  # <query>
    r"<input>",  # <input>
    r"\$\{[^}]+\}",  # ${variable}
    r"__[A-Z_]+__",  # __PLACEHOLDER__
]


def analyze_redundancy(text: str) -> dict:
    """Detect redundant phrases and repeated concepts."""
    words = text.lower().split()

    # Find repeated bigrams
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
    bigram_counts = Counter(bigrams)
    repeated_bigrams = {bg: count for bg, count in bigram_counts.items()
                        if count > 1 and len(bg) > 5}

    # Find repeated trigrams
    trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}"
                for i in range(len(words)-2)]
    trigram_counts = Counter(trigrams)
    repeated_trigrams = {tg: count for tg, count in trigram_counts.items()
                         if count > 1 and len(tg) > 10}

    # Find duplicate sentences
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    sentence_counts = Counter(sentences)
    duplicate_sentences = [s for s, c in sentence_counts.items() if c > 1]

    return {
        "repeated_bigrams": dict(sorted(repeated_bigrams.items(),
                                        key=lambda x: -x[1])[:10]),
        "repeated_trigrams": dict(sorted(repeated_trigrams.items(),
                                         key=lambda x: -x[1])[:5]),
        "duplicate_sentences": duplicate_sentences[:5],
        "redundancy_score": min(100, len(repeated_bigrams) * 5 +
                                len(repeated_trigrams) * 10 +
                                len(duplicate_sentences) * 20),
    }


def analyze_verbosity(text: str) -> dict:
    """Identify verbose phrases that can be condensed."""
    findings = []
    total_savings = 0

    for pattern, replacement in VERBOSE_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Estimate token savings (rough: 1 word = 1.3 tokens)
            original_tokens = len(pattern.split()) * 1.3
            replacement_tokens = len(replacement.split()) * 1.3 if replacement else 0
            savings = int((original_tokens - replacement_tokens) * len(matches))

            findings.append({
                "pattern": pattern,
                "replacement": replacement if replacement else "(remove)",
                "occurrences": len(matches),
                "estimated_savings": savings,
            })
            total_savings += savings

    return {
        "verbose_phrases": sorted(findings, key=lambda x: -x["estimated_savings"]),
        "total_estimated_savings": total_savings,
        "verbosity_score": min(100, total_savings * 2),
    }


def analyze_cache_structure(text: str) -> dict:
    """Analyze cache-friendliness of prompt structure."""
    # Find first dynamic marker
    first_dynamic = len(text)
    first_marker = None

    for marker in DYNAMIC_MARKERS:
        match = re.search(marker, text, re.IGNORECASE)
        if match and match.start() < first_dynamic:
            first_dynamic = match.start()
            first_marker = match.group()

    # Calculate ratios
    static_chars = first_dynamic
    total_chars = len(text)
    static_ratio = static_chars / total_chars if total_chars > 0 else 0

    # Estimate tokens (rough: 4 chars = 1 token)
    static_tokens = static_chars // 4
    total_tokens = total_chars // 4

    # Check for anti-patterns
    anti_patterns = []

    # Dynamic content at start
    if first_dynamic < 100 and first_dynamic < len(text) * 0.1:
        anti_patterns.append("Dynamic content appears very early in prompt")

    # Timestamps or dates in text
    if re.search(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}', text):
        anti_patterns.append("Hardcoded dates may break cache")

    # User IDs or session IDs early
    if re.search(r'^.*?(user[_-]?id|session[_-]?id).*?:', text[:500], re.IGNORECASE):
        anti_patterns.append("User/session ID near start may break cache")

    return {
        "static_prefix_chars": static_chars,
        "total_chars": total_chars,
        "static_ratio_percent": round(static_ratio * 100, 1),
        "estimated_static_tokens": static_tokens,
        "estimated_total_tokens": total_tokens,
        "first_dynamic_marker": first_marker,
        "cache_friendly": static_ratio > 0.5 and static_tokens >= 1024,
        "anti_patterns": anti_patterns,
        "cache_score": int(static_ratio * 100) - len(anti_patterns) * 10,
    }


def analyze_structure(text: str) -> dict:
    """Analyze prompt structure and organization."""
    lines = text.split('\n')

    # Count sections (headers)
    headers = [l for l in lines if l.strip().startswith('#') or
               l.strip().startswith('[') and l.strip().endswith(']')]

    # Check for XML-style tags
    xml_tags = re.findall(r'<([a-z_]+)>', text, re.IGNORECASE)

    # Check for common sections
    has_system = bool(re.search(r'(system|role|you are)', text[:500], re.IGNORECASE))
    has_examples = bool(re.search(r'(example|e\.g\.|for instance)', text, re.IGNORECASE))
    has_format = bool(re.search(r'(format|output|respond)', text, re.IGNORECASE))
    has_rules = bool(re.search(r'(rule|constraint|must|never|always)', text, re.IGNORECASE))

    return {
        "total_lines": len(lines),
        "non_empty_lines": len([l for l in lines if l.strip()]),
        "sections_found": len(headers),
        "section_headers": headers[:10],
        "uses_xml_tags": len(xml_tags) > 0,
        "xml_tags": list(set(xml_tags))[:10],
        "has_role_definition": has_system,
        "has_examples": has_examples,
        "has_format_spec": has_format,
        "has_rules": has_rules,
        "structure_score": sum([
            has_system * 25,
            has_examples * 25,
            has_format * 25,
            has_rules * 25,
        ]),
    }


def estimate_optimization_potential(analyses: dict) -> dict:
    """Estimate overall optimization potential."""
    redundancy = analyses["redundancy"]["redundancy_score"]
    verbosity = analyses["verbosity"]["verbosity_score"]
    cache = analyses["cache"]["cache_score"]

    # Calculate potential savings
    token_reduction = min(50, verbosity // 2 + redundancy // 4)

    # Overall score (higher = more optimization potential)
    optimization_potential = (redundancy + verbosity + (100 - cache)) // 3

    recommendations = []

    if redundancy > 30:
        recommendations.append("High redundancy detected - consolidate repeated concepts")

    if verbosity > 30:
        recommendations.append("Verbose phrasing found - use concise alternatives")

    if cache < 50:
        recommendations.append("Poor cache structure - restructure static/dynamic content")

    if analyses["structure"]["structure_score"] < 75:
        recommendations.append("Missing prompt sections - add role/examples/format specs")

    return {
        "optimization_potential_score": optimization_potential,
        "estimated_token_reduction_percent": token_reduction,
        "recommendations": recommendations,
        "priority": "high" if optimization_potential > 60 else
                   "medium" if optimization_potential > 30 else "low",
    }


def full_analysis(text: str) -> dict:
    """Run comprehensive analysis."""
    analyses = {
        "redundancy": analyze_redundancy(text),
        "verbosity": analyze_verbosity(text),
        "cache": analyze_cache_structure(text),
        "structure": analyze_structure(text),
    }

    analyses["summary"] = estimate_optimization_potential(analyses)

    return analyses


def format_report(analysis: dict) -> str:
    """Format analysis as human-readable report."""
    lines = [
        "=" * 60,
        "PROMPT OPTIMIZATION ANALYSIS",
        "=" * 60,
        "",
        f"Overall Optimization Potential: {analysis['summary']['optimization_potential_score']}/100 ({analysis['summary']['priority'].upper()})",
        f"Estimated Token Reduction: {analysis['summary']['estimated_token_reduction_percent']}%",
        "",
    ]

    # Recommendations
    if analysis["summary"]["recommendations"]:
        lines.append("RECOMMENDATIONS:")
        for rec in analysis["summary"]["recommendations"]:
            lines.append(f"  - {rec}")
        lines.append("")

    # Redundancy
    lines.extend([
        "-" * 40,
        f"REDUNDANCY (Score: {analysis['redundancy']['redundancy_score']}/100)",
        "-" * 40,
    ])
    if analysis["redundancy"]["repeated_trigrams"]:
        lines.append("Repeated phrases:")
        for phrase, count in list(analysis["redundancy"]["repeated_trigrams"].items())[:3]:
            lines.append(f"  '{phrase}' appears {count}x")
    if analysis["redundancy"]["duplicate_sentences"]:
        lines.append("Duplicate sentences found")
    lines.append("")

    # Verbosity
    lines.extend([
        "-" * 40,
        f"VERBOSITY (Score: {analysis['verbosity']['verbosity_score']}/100)",
        "-" * 40,
        f"Estimated token savings: {analysis['verbosity']['total_estimated_savings']}",
    ])
    if analysis["verbosity"]["verbose_phrases"]:
        lines.append("Verbose patterns found:")
        for finding in analysis["verbosity"]["verbose_phrases"][:5]:
            lines.append(f"  '{finding['pattern']}' -> '{finding['replacement']}' ({finding['occurrences']}x)")
    lines.append("")

    # Cache structure
    lines.extend([
        "-" * 40,
        f"CACHE STRUCTURE (Score: {analysis['cache']['cache_score']}/100)",
        "-" * 40,
        f"Static prefix: ~{analysis['cache']['estimated_static_tokens']} tokens ({analysis['cache']['static_ratio_percent']}%)",
        f"Cache friendly: {'Yes' if analysis['cache']['cache_friendly'] else 'No'}",
    ])
    if analysis["cache"]["anti_patterns"]:
        lines.append("Issues found:")
        for pattern in analysis["cache"]["anti_patterns"]:
            lines.append(f"  - {pattern}")
    lines.append("")

    # Structure
    lines.extend([
        "-" * 40,
        f"STRUCTURE (Score: {analysis['structure']['structure_score']}/100)",
        "-" * 40,
        f"Has role definition: {'Yes' if analysis['structure']['has_role_definition'] else 'No'}",
        f"Has examples: {'Yes' if analysis['structure']['has_examples'] else 'No'}",
        f"Has format spec: {'Yes' if analysis['structure']['has_format_spec'] else 'No'}",
        f"Has rules: {'Yes' if analysis['structure']['has_rules'] else 'No'}",
        f"Uses XML tags: {'Yes' if analysis['structure']['uses_xml_tags'] else 'No'}",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze prompts for optimization opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python prompt_analyzer.py --input prompt.txt
    python prompt_analyzer.py --input prompt.txt --output analysis.json
    python prompt_analyzer.py "Your prompt text here"
        """
    )
    parser.add_argument("text", nargs="?", help="Prompt text to analyze")
    parser.add_argument("--input", "-i", help="Read prompt from file")
    parser.add_argument("--output", "-o", help="Write JSON analysis to file")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Get text
    if args.input:
        try:
            text = Path(args.input).read_text()
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        print("Error: Provide prompt text or --input argument", file=sys.stderr)
        sys.exit(1)

    # Run analysis
    analysis = full_analysis(text)

    # Output
    if args.output:
        Path(args.output).write_text(json.dumps(analysis, indent=2))
        print(f"Analysis written to: {args.output}")
    elif args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
