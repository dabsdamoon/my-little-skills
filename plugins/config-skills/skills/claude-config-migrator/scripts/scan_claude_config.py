#!/usr/bin/env python3
"""Scan a repository for Claude Code configuration elements.

Traverses known Claude Code config paths and outputs a structured JSON
inventory to stdout. Uses only Python 3 stdlib.

Usage:
    python scan_claude_config.py <repo-path>
"""

import argparse
import json
import sys
from pathlib import Path


# Maximum bytes of file content to include as preview
PREVIEW_MAX_BYTES = 500


def read_preview(path: Path) -> str:
    """Read the first PREVIEW_MAX_BYTES of a file as a text preview."""
    try:
        raw = path.read_bytes()[:PREVIEW_MAX_BYTES]
        text = raw.decode("utf-8", errors="replace")
        if path.stat().st_size > PREVIEW_MAX_BYTES:
            text += "\n... (truncated)"
        return text
    except Exception:
        return ""


def scan_file(repo: Path, rel: Path, element_type: str, **extra) -> dict:
    """Build an element dict for a single file."""
    full = repo / rel
    if not full.is_file():
        return None
    entry = {
        "type": element_type,
        "path": str(rel),
        "size_bytes": full.stat().st_size,
        "preview": read_preview(full),
    }
    entry.update(extra)
    return entry


def scan_glob(repo: Path, pattern: str, element_type: str, **extra) -> list[dict]:
    """Scan a glob pattern under repo, returning element dicts."""
    results = []
    for full in sorted(repo.glob(pattern)):
        if not full.is_file():
            continue
        rel = full.relative_to(repo)
        entry = scan_file(repo, rel, element_type, **extra)
        if entry:
            results.append(entry)
    return results


def is_local_file(path: str) -> bool:
    """Return True if the path refers to a .local variant (private/personal)."""
    name = Path(path).name
    return ".local" in name


def scan_repo(repo_path: str) -> dict:
    """Scan a repository and return the full inventory."""
    repo = Path(repo_path).resolve()
    if not repo.is_dir():
        print(f"Error: '{repo_path}' is not a directory", file=sys.stderr)
        sys.exit(1)

    elements: list[dict] = []

    # --- Settings ---
    e = scan_file(repo, Path(".claude/settings.json"), "settings")
    if e:
        elements.append(e)

    # --- CLAUDE.md files ---
    for rel in [
        Path("CLAUDE.md"),
        Path(".claude/CLAUDE.md"),
    ]:
        e = scan_file(repo, rel, "claude_md")
        if e:
            elements.append(e)

    # --- Rules ---
    elements.extend(scan_glob(repo, ".claude/rules/*.md", "rule"))

    # --- Skills ---
    # Each skill is a directory under .claude/skills/ containing SKILL.md
    skills_dir = repo / ".claude" / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                continue
            # Collect all files in the skill directory
            skill_files = []
            for f in sorted(skill_dir.rglob("*")):
                if f.is_file():
                    skill_files.append(str(f.relative_to(repo)))
            rel = skill_dir.relative_to(repo)
            entry = {
                "type": "skill",
                "path": str(rel),
                "size_bytes": sum(
                    f.stat().st_size
                    for f in skill_dir.rglob("*")
                    if f.is_file()
                ),
                "preview": read_preview(skill_md),
                "files": skill_files,
                "file_count": len(skill_files),
            }
            elements.append(entry)

    # --- Commands ---
    elements.extend(scan_glob(repo, ".claude/commands/*.md", "command"))

    # --- Agents ---
    elements.extend(scan_glob(repo, ".claude/agents/*.md", "agent"))

    # --- Hooks ---
    hooks_dir = repo / ".claude" / "hooks"
    if hooks_dir.is_dir():
        for f in sorted(hooks_dir.rglob("*")):
            if f.is_file():
                rel = f.relative_to(repo)
                e = scan_file(repo, rel, "hook")
                if e:
                    elements.append(e)

    # --- MCP config ---
    e = scan_file(repo, Path(".mcp.json"), "mcp_config")
    if e:
        elements.append(e)

    # --- Filter out .local files ---
    elements = [e for e in elements if not is_local_file(e["path"])]

    # --- Build summary ---
    summary: dict[str, int] = {}
    for e in elements:
        t = e["type"]
        summary[t] = summary.get(t, 0) + 1

    return {
        "repo_path": str(repo),
        "summary": summary,
        "total_elements": len(elements),
        "elements": elements,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Scan a repository for Claude Code configuration elements."
    )
    parser.add_argument(
        "repo_path",
        help="Path to the repository to scan",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    result = scan_repo(args.repo_path)
    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent, ensure_ascii=False))


if __name__ == "__main__":
    main()
