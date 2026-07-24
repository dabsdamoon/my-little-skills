#!/usr/bin/env python3
"""Verify Markdown work reports against their canonical Git evidence bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "https://dabsdamoon.github.io/schemas/git-work-report-evidence-v1.json"
FINGERPRINT_RE = re.compile(r"<!--\s*evidence-sha256:([0-9a-f]{64})\s*-->")
METRIC_RE = re.compile(r"<!--\s*metric:([a-z_]+)=([^\s]+)\s*-->")
COMMIT_RE = re.compile(r"<!--\s*commit:([0-9a-f]{40})\s*-->")
PLACEHOLDER_RE = re.compile(
    r"(?:\bTODO\b|\bTBD\b|Lorem ipsum|\[\s*PLACEHOLDER[^\]]*\])",
    re.IGNORECASE,
)
REQUIRED_METRICS = (
    "commit_count",
    "merge_commit_count",
    "numbered_merge_commit_count",
    "activity_day_count",
    "tag_count",
    "contributor_count",
    "insertions",
    "deletions",
    "unique_path_count",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify external and internal work-report Markdown files."
    )
    parser.add_argument("--evidence", required=True, help="git-evidence.json path.")
    parser.add_argument("--external", required=True, help="External Markdown report.")
    parser.add_argument("--internal", required=True, help="Internal Markdown work log.")
    parser.add_argument("--output", required=True, help="Verification JSON output path.")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Warn instead of failing for shallow or truncated evidence.",
    )
    return parser.parse_args()


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def metric_markers(text: str) -> dict[str, str]:
    markers: dict[str, str] = {}
    for key, value in METRIC_RE.findall(text):
        if key in markers and markers[key] != value:
            markers[key] = "__CONFLICT__"
        else:
            markers[key] = value
    return markers


def verify() -> tuple[dict[str, object], int]:
    args = parse_args()
    evidence_path = Path(args.evidence).expanduser().resolve()
    external_path = Path(args.external).expanduser().resolve()
    internal_path = Path(args.internal).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        evidence_raw = evidence_path.read_bytes()
        evidence = json.loads(evidence_raw)
        external = external_path.read_text(encoding="utf-8")
        internal = internal_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        result = {
            "status": "fail",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "errors": [str(error)],
            "warnings": [],
        }
        atomic_write_json(output_path, result)
        return result, 1

    evidence_sha256 = hashlib.sha256(evidence_raw).hexdigest()
    if evidence.get("schema") != SCHEMA:
        errors.append(f"unsupported evidence schema: {evidence.get('schema')!r}")

    summary = evidence.get("summary")
    commits = evidence.get("commits")
    completeness = evidence.get("completeness")
    if not isinstance(summary, dict):
        errors.append("evidence summary is missing or invalid")
        summary = {}
    if not isinstance(commits, list):
        errors.append("evidence commits are missing or invalid")
        commits = []
    if not isinstance(completeness, dict):
        errors.append("evidence completeness is missing or invalid")
        completeness = {}

    for label, text in (("external", external), ("internal", internal)):
        fingerprints = FINGERPRINT_RE.findall(text)
        if fingerprints != [evidence_sha256]:
            errors.append(
                f"{label}: expected one evidence fingerprint {evidence_sha256}, "
                f"found {fingerprints}"
            )
        if PLACEHOLDER_RE.search(text):
            errors.append(f"{label}: unresolved placeholder")
        markers = metric_markers(text)
        for key in REQUIRED_METRICS:
            expected = str(summary.get(key))
            actual = markers.get(key)
            if actual != expected:
                errors.append(
                    f"{label}: metric {key} expected {expected!r}, found {actual!r}"
                )

    expected_hashes = {
        str(commit.get("hash"))
        for commit in commits
        if isinstance(commit, dict) and re.fullmatch(r"[0-9a-f]{40}", str(commit.get("hash")))
    }
    internal_markers = COMMIT_RE.findall(internal)
    actual_hashes = set(internal_markers)
    missing = sorted(expected_hashes - actual_hashes)
    unknown = sorted(actual_hashes - expected_hashes)
    duplicates = sorted(
        object_id for object_id in actual_hashes if internal_markers.count(object_id) != 1
    )
    if missing:
        errors.append(f"internal: missing {len(missing)} commit markers")
    if unknown:
        errors.append(f"internal: contains {len(unknown)} unknown commit markers")
    if duplicates:
        errors.append(f"internal: contains {len(duplicates)} duplicate commit markers")
    if len(expected_hashes) != len(commits):
        errors.append("evidence contains missing, duplicate, or malformed commit hashes")

    incomplete_reasons = []
    if completeness.get("is_shallow"):
        incomplete_reasons.append("repository is shallow")
    if completeness.get("truncated"):
        incomplete_reasons.append("collection is truncated")
    if incomplete_reasons:
        message = "; ".join(incomplete_reasons)
        if args.allow_incomplete:
            warnings.append(message)
        else:
            errors.append(message)

    repository = evidence.get("repository")
    if isinstance(repository, dict) and repository.get("dirty"):
        warnings.append(
            "working tree was dirty at collection time; uncommitted changes are outside scope"
        )

    status = "pass" if not errors else "fail"
    result: dict[str, object] = {
        "status": status,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "evidence": str(evidence_path),
        "evidence_sha256": evidence_sha256,
        "external": str(external_path),
        "internal": str(internal_path),
        "commit_coverage": {
            "expected": len(expected_hashes),
            "found": len(actual_hashes & expected_hashes),
            "missing": missing,
            "unknown": unknown,
            "duplicates": duplicates,
        },
        "metric_count": len(REQUIRED_METRICS),
        "errors": errors,
        "warnings": warnings,
    }
    atomic_write_json(output_path, result)
    return result, 0 if status == "pass" else 1


def main() -> int:
    result, exit_code = verify()
    coverage = result.get("commit_coverage", {})
    print(
        str(result["status"]).upper(),
        f"commits={coverage.get('found', 0)}/{coverage.get('expected', 0)}",
        f"metrics={result.get('metric_count', 0)}",
        f"errors={len(result.get('errors', []))}",
        f"warnings={len(result.get('warnings', []))}",
    )
    if result.get("errors"):
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
