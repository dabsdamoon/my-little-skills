#!/usr/bin/env python3
"""Deterministically + idempotently update a PR body's checklist and QA section.

Editing GitHub task-list checkboxes by hand is error-prone: it's easy to flip
the wrong line, break the `- [ ]` markup, or stack duplicate "## QA Verification"
sections on a re-run. This helper does the mechanical part reliably so the
calling skill can focus on judgment (which items actually passed).

What it does:
  * Flips `- [ ]` -> `- [x]` only on lines whose text contains one of the
    --check substrings. Already-checked lines and non-matching lines are left
    byte-for-byte unchanged.
  * Optionally replaces (never appends a duplicate of) a "## QA Verification"
    section with fresh content. If the section already exists it is swapped in
    place; otherwise it is inserted right after the testing-checklist block, or
    appended at the end as a fallback.

Idempotency: running twice with the same inputs yields the same output. Flipping
an already-checked box is a no-op; the QA section is replaced, not stacked.

Usage:
  python update_pr_checklist.py --body-file BODY [--check TEXT ...] \
      [--qa-section-file QA.md] [--out OUT | --in-place]

  --body-file       Path to the current PR body markdown.
  --check TEXT      Substring identifying a checklist item to tick. Repeatable.
                    Matched against the item's text (the part after `- [ ]`).
  --qa-section-file Path to markdown for the QA Verification section body
                    (without the "## QA Verification" heading; it's added).
  --out             Write result here. Defaults to stdout.
  --in-place        Overwrite --body-file.
  --strict          Exit non-zero if any --check string matched no unchecked item.

Exit codes: 0 ok; 2 a --check matched nothing (only with --strict); 1 usage/IO.
"""
from __future__ import annotations

import argparse
import re
import sys

QA_HEADING = "## QA Verification"
# A task-list line: indentation, bullet, unchecked box, then the item text.
UNCHECKED_RE = re.compile(r"^(?P<prefix>\s*[-*]\s+)\[ \](?P<rest>\s+.*)$")
ANY_TASK_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s+")
# Headings that typically introduce the checklist, used to place a new section.
CHECKLIST_HEADING_RE = re.compile(r"^#{1,6}\s+.*(test|checklist|qa)\b", re.IGNORECASE)
# A Markdown thematic break (---, ***, ___). These divide sections, so they
# bound the QA section rather than belonging to it — important for idempotency
# when a PR template puts `---` separators between sections.
THEMATIC_BREAK_RE = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")


def _is_section_boundary(line: str) -> bool:
    """True if `line` ends the QA section: a ##/# heading or a thematic break."""
    return bool(re.match(r"^#{1,2}\s+\S", line)) or bool(THEMATIC_BREAK_RE.match(line.strip()))


def tick_items(body: str, checks: list[str]) -> tuple[str, dict[str, bool]]:
    """Flip unchecked lines whose text contains any check substring.

    Returns the new body and a map of check-string -> whether it matched.
    """
    matched = {c: False for c in checks}
    out_lines = []
    for line in body.splitlines():
        m = UNCHECKED_RE.match(line)
        if m:
            text = m.group("rest")
            hit = next((c for c in checks if c and c in text), None)
            if hit is not None:
                matched[hit] = True
                line = f"{m.group('prefix')}[x]{m.group('rest')}"
        out_lines.append(line)
    # Preserve trailing newline state of the original.
    result = "\n".join(out_lines)
    if body.endswith("\n"):
        result += "\n"
    return result, matched


def _remove_existing_section(lines: list[str]) -> list[str]:
    """Strip an existing QA section (and one separator blank on each side).

    Returns the body lines with no QA section present. No-op if absent. This
    is what makes the upsert idempotent: replace == remove-then-insert, so the
    insert path below is the single source of truth for spacing.
    """
    start = next((i for i, l in enumerate(lines) if l.strip() == QA_HEADING), -1)
    if start == -1:
        return lines
    # Section runs until the next structural boundary (heading or thematic break).
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if _is_section_boundary(lines[j]):
            end = j
            break
    # Absorb a single separator blank line immediately before the heading.
    pre = start - 1 if start > 0 and lines[start - 1].strip() == "" else start
    return lines[:pre] + lines[end:]


def _insertion_index(lines: list[str]) -> int:
    """Where a fresh QA section should go: after the checklist block, else EOF."""
    heading_idx = next(
        (i for i, ln in enumerate(lines) if CHECKLIST_HEADING_RE.match(ln)), None
    )
    if heading_idx is None:
        return len(lines)
    last_task = heading_idx
    for k in range(heading_idx + 1, len(lines)):
        if ANY_TASK_RE.match(lines[k]):
            last_task = k
        elif re.match(r"^#{1,6}\s+\S", lines[k]) or THEMATIC_BREAK_RE.match(lines[k].strip()):
            break
    return last_task + 1


def upsert_qa_section(body: str, section_md: str) -> str:
    """Insert or replace the QA Verification section idempotently.

    Always removes any existing section first, then inserts via one code path
    with exactly one blank-line separator on each side, so running twice with
    the same inputs is a fixed point.
    """
    block_lines = [QA_HEADING, ""] + section_md.strip().splitlines()
    lines = _remove_existing_section(body.splitlines())
    at = _insertion_index(lines)

    before, after = lines[:at], lines[at:]
    chunk: list[str] = []
    if before and before[-1].strip() != "":
        chunk.append("")
    chunk += block_lines
    if after and after[0].strip() != "":
        chunk.append("")

    result = "\n".join(before + chunk + after)
    return result + "\n" if body.endswith("\n") else result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--check", action="append", default=[], help="Substring of an item to tick. Repeatable.")
    ap.add_argument("--qa-section-file")
    ap.add_argument("--out")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    try:
        with open(args.body_file, encoding="utf-8") as f:
            body = f.read()
    except OSError as e:
        print(f"error: cannot read --body-file: {e}", file=sys.stderr)
        return 1

    body, matched = tick_items(body, args.check)

    if args.qa_section_file:
        try:
            with open(args.qa_section_file, encoding="utf-8") as f:
                section_md = f.read()
        except OSError as e:
            print(f"error: cannot read --qa-section-file: {e}", file=sys.stderr)
            return 1
        body = upsert_qa_section(body, section_md)

    unmatched = [c for c, ok in matched.items() if not ok]
    for c in unmatched:
        print(f"warning: no unchecked item matched: {c!r}", file=sys.stderr)

    if args.in_place:
        with open(args.body_file, "w", encoding="utf-8") as f:
            f.write(body)
    elif args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(body)
    else:
        sys.stdout.write(body)

    if args.strict and unmatched:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
