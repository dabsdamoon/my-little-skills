#!/usr/bin/env python3
"""Collect a deterministic, privacy-conscious Git work-report evidence bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone, tzinfo
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SCHEMA = "https://dabsdamoon.github.io/schemas/git-work-report-evidence-v1.json"
RECORD_SEPARATOR = "\x1e"
FIELD_SEPARATOR = "\x1f"
LOG_FORMAT = FIELD_SEPARATOR.join(
    [
        "%H",
        "%h",
        "%P",
        "%an",
        "%ae",
        "%aI",
        "%cn",
        "%ce",
        "%cI",
        "%D",
        "%s",
    ]
)
CATEGORY_LABELS = {
    "feat": "feature",
    "feature": "feature",
    "fix": "fix",
    "bugfix": "fix",
    "docs": "documentation",
    "doc": "documentation",
    "test": "test",
    "tests": "test",
    "refactor": "refactor",
    "perf": "performance",
    "performance": "performance",
    "ci": "ci",
    "build": "build",
    "style": "style",
    "chore": "maintenance",
    "release": "release",
    "revert": "revert",
}


class CollectionError(RuntimeError):
    """Raised when a Git evidence snapshot cannot be collected safely."""


def run_git(repo: Path, args: list[str], *, allow_failure: bool = False) -> str:
    command = ["git", "-C", str(repo), "-c", "core.quotepath=false", *args]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode and not allow_failure:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown Git error"
        raise CollectionError(f"{' '.join(command[:4] + args)}: {detail}")
    return result.stdout


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Git history evidence for external and internal work reports."
    )
    parser.add_argument("--repo", default=".", help="Path inside the Git repository.")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--ref", default="HEAD", help="Revision to report (default: HEAD).")
    scope.add_argument(
        "--all-refs",
        action="store_true",
        help="Include commits reachable from every ref, including unmerged work.",
    )
    parser.add_argument("--since", help="Git-compatible inclusive lower date boundary.")
    parser.add_argument("--until", help="Git-compatible inclusive upper date boundary.")
    parser.add_argument("--author", help="Git author pattern used to filter commits.")
    parser.add_argument(
        "--timezone",
        default="UTC",
        help="IANA timezone or fixed UTC offset used for day grouping (default: UTC).",
    )
    parser.add_argument(
        "--max-commits",
        type=int,
        default=0,
        help="Maximum commits to collect; 0 means unlimited and is recommended.",
    )
    parser.add_argument(
        "--include-author-email",
        action="store_true",
        help="Retain clear author and committer emails. Default stores only hashes.",
    )
    parser.add_argument("--output", required=True, help="Output JSON path.")
    args = parser.parse_args()
    if args.max_commits < 0:
        parser.error("--max-commits must be zero or greater")
    return args


def resolve_repository(path: str) -> Path:
    candidate = Path(path).expanduser().resolve()
    root = run_git(candidate, ["rev-parse", "--show-toplevel"]).strip()
    if not root:
        raise CollectionError(f"not a Git worktree: {candidate}")
    return Path(root).resolve()


def email_identity(email: str, include_clear: bool) -> dict[str, str]:
    payload = {"email_sha256": hashlib.sha256(email.encode("utf-8")).hexdigest()}
    if include_clear:
        payload["email"] = email
    return payload


def sanitize_remote_url(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    if "://" not in value:
        scp_match = re.match(r"^[^/@]+@([^:]+):(.+)$", value)
        if scp_match:
            return f"{scp_match.group(1)}:{scp_match.group(2)}"
        return value
    parsed = urlsplit(value)
    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    return urlunsplit(
        (parsed.scheme, f"{hostname}{port}", parsed.path, parsed.query, parsed.fragment)
    )


def classify_subject(subject: str, is_merge: bool) -> str:
    if is_merge:
        return "merge"
    match = re.match(r"^([A-Za-z]+)(?:\([^)]*\))?!?:", subject.strip())
    if not match:
        return "other"
    return CATEGORY_LABELS.get(match.group(1).lower(), "other")


def resolve_timezone(value: str) -> tzinfo:
    if value.upper() in {"UTC", "Z"}:
        return timezone.utc
    fixed_offset = re.fullmatch(r"([+-])(\d{2}):(\d{2})", value)
    if fixed_offset:
        hours = int(fixed_offset.group(2))
        minutes = int(fixed_offset.group(3))
        if hours > 23 or minutes > 59:
            raise CollectionError(f"invalid fixed UTC offset: {value}")
        delta = timedelta(hours=hours, minutes=minutes)
        if fixed_offset.group(1) == "-":
            delta = -delta
        return timezone(delta, name=value)
    try:
        return ZoneInfo(value)
    except ZoneInfoNotFoundError as error:
        raise CollectionError(
            f"unknown IANA timezone {value!r}; install Python tzdata or use a "
            "fixed offset such as +09:00"
        ) from error


def iso_in_zone(value: str, reporting_zone: tzinfo) -> tuple[str, str]:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise CollectionError(f"invalid Git ISO timestamp: {value}") from error
    localized = parsed.astimezone(reporting_zone)
    return localized.isoformat(), localized.date().isoformat()


def build_revision_args(args: argparse.Namespace) -> list[str]:
    revision = ["--all"] if args.all_refs else [args.ref]
    if args.since:
        revision.append(f"--since={args.since}")
    if args.until:
        revision.append(f"--until={args.until}")
    if args.author:
        revision.append(f"--author={args.author}")
    return revision


def matching_commit_count(repo: Path, revision_args: list[str]) -> int:
    raw = run_git(repo, ["rev-list", "--count", *revision_args]).strip()
    try:
        return int(raw)
    except ValueError as error:
        raise CollectionError(f"unexpected rev-list count: {raw!r}") from error


def parse_numstat_line(line: str) -> tuple[str, int | None, int | None] | None:
    fields = line.split("\t", 2)
    if len(fields) != 3:
        return None
    added_raw, deleted_raw, path = fields
    if added_raw == "-" or deleted_raw == "-":
        return path, None, None
    try:
        return path, int(added_raw), int(deleted_raw)
    except ValueError:
        return None


def collect_commits(
    repo: Path,
    args: argparse.Namespace,
    revision_args: list[str],
    reporting_zone: tzinfo,
) -> list[dict[str, object]]:
    log_args = [
        "log",
        "--topo-order",
        "--no-renames",
        "--numstat",
        f"--format={RECORD_SEPARATOR}{LOG_FORMAT}",
    ]
    if args.max_commits:
        log_args.append(f"--max-count={args.max_commits}")
    raw = run_git(repo, [*log_args, *revision_args])
    commits: list[dict[str, object]] = []

    for raw_record in raw.split(RECORD_SEPARATOR):
        record = raw_record.lstrip("\r\n")
        if not record:
            continue
        header, _, numstat_text = record.partition("\n")
        fields = header.split(FIELD_SEPARATOR, 10)
        if len(fields) != 11:
            raise CollectionError(f"unexpected Git log record with {len(fields)} fields")
        (
            full_hash,
            short_hash,
            parents_raw,
            author_name,
            author_email,
            author_iso,
            committer_name,
            committer_email,
            committer_iso,
            decorations,
            subject,
        ) = fields
        parents = [value for value in parents_raw.split() if value]
        is_merge = len(parents) > 1
        localized_iso, activity_date = iso_in_zone(committer_iso, reporting_zone)

        changes: list[dict[str, object]] = []
        insertions = 0
        deletions = 0
        binary_files = 0
        for line in numstat_text.splitlines():
            parsed = parse_numstat_line(line)
            if not parsed:
                continue
            path, added, deleted = parsed
            if added is None or deleted is None:
                binary_files += 1
                changes.append({"path": path, "binary": True})
                continue
            insertions += added
            deletions += deleted
            changes.append(
                {
                    "path": path,
                    "binary": False,
                    "insertions": added,
                    "deletions": deleted,
                }
            )

        author = {"name": author_name}
        author.update(email_identity(author_email, args.include_author_email))
        committer = {"name": committer_name}
        committer.update(email_identity(committer_email, args.include_author_email))
        commits.append(
            {
                "hash": full_hash,
                "short_hash": short_hash,
                "parents": parents,
                "is_merge": is_merge,
                "author": author,
                "author_time": author_iso,
                "committer": committer,
                "committer_time": committer_iso,
                "reporting_time": localized_iso,
                "activity_date": activity_date,
                "subject": subject,
                "decorations": decorations,
                "category": classify_subject(subject, is_merge),
                "stats": {
                    "file_count": len(changes),
                    "insertions": insertions,
                    "deletions": deletions,
                    "binary_file_count": binary_files,
                },
                "changes": changes,
            }
        )
    return commits


def collect_tags(
    repo: Path,
    args: argparse.Namespace,
    resolved_tip: str | None,
    commit_hashes: set[str],
) -> list[dict[str, str]]:
    if args.all_refs:
        names = run_git(repo, ["tag", "--list"]).splitlines()
    else:
        names = run_git(repo, ["tag", "--merged", resolved_tip or args.ref]).splitlines()
    tags = []
    for name in sorted(filter(None, names)):
        commit = run_git(repo, ["rev-list", "-n", "1", name]).strip()
        if commit not in commit_hashes:
            continue
        created = run_git(
            repo,
            ["for-each-ref", f"refs/tags/{name}", "--format=%(creatordate:iso-strict)"],
        ).strip()
        tags.append({"name": name, "commit": commit, "created_at": created})
    return tags


def collect_refs(repo: Path) -> list[dict[str, str]]:
    raw = run_git(
        repo,
        [
            "for-each-ref",
            "refs/heads",
            "refs/remotes",
            "--format=%(refname)\t%(objectname)",
        ],
    )
    refs = []
    for line in raw.splitlines():
        name, separator, object_id = line.partition("\t")
        if separator:
            refs.append({"name": name, "object": object_id})
    return refs


def collect_remotes(repo: Path) -> list[dict[str, str]]:
    raw = run_git(repo, ["remote", "-v"], allow_failure=True)
    seen: set[tuple[str, str, str]] = set()
    remotes = []
    for line in raw.splitlines():
        match = re.match(r"^(\S+)\s+(\S+)\s+\((fetch|push)\)$", line)
        if not match:
            continue
        item = (match.group(1), sanitize_remote_url(match.group(2)), match.group(3))
        if item in seen:
            continue
        seen.add(item)
        remotes.append({"name": item[0], "url": item[1], "direction": item[2]})
    return remotes


def summarize(
    commits: list[dict[str, object]], tags: list[dict[str, str]]
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    categories: Counter[str] = Counter()
    activity: Counter[str] = Counter()
    contributors: dict[tuple[str, str], dict[str, object]] = {}
    paths: set[str] = set()
    insertions = 0
    deletions = 0
    binary_files = 0
    merge_count = 0
    numbered_merge_count = 0

    for commit in commits:
        categories[str(commit["category"])] += 1
        activity[str(commit["activity_date"])] += 1
        if commit["is_merge"]:
            merge_count += 1
            if re.search(r"(?:#|PR\s*#?)\d+", str(commit["subject"]), re.IGNORECASE):
                numbered_merge_count += 1
        stats = commit["stats"]
        assert isinstance(stats, dict)
        insertions += int(stats["insertions"])
        deletions += int(stats["deletions"])
        binary_files += int(stats["binary_file_count"])
        changes = commit["changes"]
        assert isinstance(changes, list)
        for change in changes:
            assert isinstance(change, dict)
            paths.add(str(change["path"]))

        author = commit["author"]
        assert isinstance(author, dict)
        key = (str(author["name"]), str(author["email_sha256"]))
        entry = contributors.setdefault(
            key,
            {
                "name": author["name"],
                "email_sha256": author["email_sha256"],
                "commit_count": 0,
            },
        )
        if "email" in author:
            entry["email"] = author["email"]
        entry["commit_count"] = int(entry["commit_count"]) + 1

    dates = sorted(activity)
    summary = {
        "commit_count": len(commits),
        "merge_commit_count": merge_count,
        "numbered_merge_commit_count": numbered_merge_count,
        "activity_day_count": len(activity),
        "period_start": dates[0] if dates else None,
        "period_end": dates[-1] if dates else None,
        "tag_count": len(tags),
        "contributor_count": len(contributors),
        "insertions": insertions,
        "deletions": deletions,
        "binary_file_change_count": binary_files,
        "unique_path_count": len(paths),
        "category_counts": dict(sorted(categories.items())),
    }
    contributor_rows = sorted(
        contributors.values(),
        key=lambda item: (-int(item["commit_count"]), str(item["name"])),
    )
    activity_rows = [
        {"date": date, "commit_count": activity[date]} for date in sorted(activity)
    ]
    return summary, contributor_rows, activity_rows


def main() -> int:
    args = parse_args()
    try:
        reporting_zone = resolve_timezone(args.timezone)
        repo = resolve_repository(args.repo)
        resolved_tip = None
        if not args.all_refs:
            resolved_tip = run_git(
                repo, ["rev-parse", "--verify", f"{args.ref}^{{commit}}"]
            ).strip()
        revision_args = build_revision_args(args)
        total_matching = matching_commit_count(repo, revision_args)
        commits = collect_commits(repo, args, revision_args, reporting_zone)
        if not commits:
            raise CollectionError("the selected revision and filters contain no commits")

        tags = collect_tags(
            repo,
            args,
            resolved_tip,
            {str(commit["hash"]) for commit in commits},
        )
        summary, contributors, activity = summarize(commits, tags)
        shallow = run_git(repo, ["rev-parse", "--is-shallow-repository"]).strip() == "true"
        truncated = len(commits) < total_matching
        warnings = []
        if shallow:
            warnings.append("Repository is shallow; earlier reachable history may be absent.")
        if truncated:
            warnings.append(
                f"Collection was truncated at {len(commits)} of {total_matching} matching commits."
            )

        status_lines = [
            line
            for line in run_git(repo, ["status", "--porcelain=v1"]).splitlines()
            if line
        ]
        current_branch = run_git(
            repo, ["symbolic-ref", "--quiet", "--short", "HEAD"], allow_failure=True
        ).strip()
        git_version = run_git(repo, ["--version"]).strip()
        roots = run_git(
            repo,
            [
                "rev-list",
                "--max-parents=0",
                *(["--all"] if args.all_refs else [resolved_tip or args.ref]),
            ],
        ).splitlines()

        payload: dict[str, object] = {
            "schema": SCHEMA,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repository": {
                "name": repo.name,
                "root": str(repo),
                "git_version": git_version,
                "current_branch": current_branch or None,
                "dirty": bool(status_lines),
                "dirty_entry_count": len(status_lines),
                "remotes": collect_remotes(repo),
            },
            "scope": {
                "mode": "all-refs" if args.all_refs else "ref",
                "revision": "--all" if args.all_refs else args.ref,
                "resolved_tip": resolved_tip,
                "root_commits": sorted(filter(None, roots)),
                "since": args.since,
                "until": args.until,
                "author_filter": args.author,
                "timezone": args.timezone,
                "author_emails_included": args.include_author_email,
            },
            "completeness": {
                "is_shallow": shallow,
                "truncated": truncated,
                "matching_commit_count": total_matching,
                "collected_commit_count": len(commits),
                "warnings": warnings,
            },
            "summary": summary,
            "contributors": contributors,
            "activity": activity,
            "tags": tags,
            "refs": collect_refs(repo),
            "commits": commits,
        }
        atomic_write_json(Path(args.output).expanduser().resolve(), payload)
    except (CollectionError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        "PASS",
        f"commits={summary['commit_count']}",
        f"merges={summary['merge_commit_count']}",
        f"activity_days={summary['activity_day_count']}",
        f"tags={summary['tag_count']}",
        f"shallow={str(shallow).lower()}",
        f"truncated={str(truncated).lower()}",
        f"output={Path(args.output).expanduser().resolve()}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
