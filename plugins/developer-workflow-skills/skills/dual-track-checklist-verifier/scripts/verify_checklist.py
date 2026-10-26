#!/usr/bin/env python3
"""Deterministically + idempotently update a PR body's checklist and evidence section.

Works on any PR test plan (`## Test plan`, `## Testing Checklist`, ...) and on
bodies produced by dual-track-pr-creator (`## Verification` plus an
acceptance-traceability table). It does the mechanical part; deciding what
passed stays with the caller.

  * `--check TEXT` ticks the one unchecked item TEXT selects: the item whose
    full text equals TEXT, else the only item containing TEXT. A substring
    that hits several items ticks none of them and is reported, because
    flipping every line containing "deploy" ticks items nobody verified.
  * `--reword OLD::NEW` rewrites one unchecked item in the same pass as the
    flip, under the same selection rule. An item that describes its own
    unverified state ("not yet observed at the time of writing") contradicts
    itself once ticked. Already-checked items are never rewritten.
  * The evidence section is replaced, never stacked, and re-running is a
    fixed point. It goes immediately before `--before-heading`, else after
    the last task line under `--anchor-heading`, else after the first
    `##`..`######` heading that looks like a checklist, else at EOF. H1 is
    never an anchor: it is the PR title, and titles of testing PRs routinely
    contain "test", which once put the section above the body's header block.
  * `--audit-table` warns when a ticked item's text also appears in an
    acceptance-traceability row marked FAIL or MISSING. dual-track bodies
    record status in two places; they must not disagree.

Usage:
  python3 verify_checklist.py --body-file BODY [--check TEXT ...]
      [--reword 'OLD::NEW' ...] [--section-file S.md]
      [--section-title '## QA Verification'] [--anchor-heading '## Verification']
      [--before-heading '## Not included'] [--audit-table]
      [--out OUT | --in-place] [--strict]

Exit codes: 0 ok; 1 usage/IO; 2 a --check/--reword matched no unchecked item
or more than one (only with --strict); 3 a ticked item contradicts a
FAIL/MISSING audit row (only with --strict).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_SECTION_TITLE = "## QA Verification"

# A task-list line: indentation, bullet, unchecked box, then the item text.
UNCHECKED_RE = re.compile(r"^(?P<prefix>\s*[-*]\s+)\[ \](?P<rest>\s+.*)$")
ANY_TASK_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s+")
CHECKED_RE = re.compile(r"^\s*[-*]\s+\[[xX]\]\s+(?P<rest>.*)$")

# Headings that introduce a checklist. `##` and deeper only: an H1 is the PR
# title, and titles about testing are common enough that matching them was the
# original bug. "verification" is included so dual-track-pr-creator bodies work.
ANCHOR_HEADING_RE = re.compile(
    r"^#{2,6}\s+.*(test|checklist|qa|verification)\b", re.IGNORECASE
)

# A Markdown thematic break (---, ***, ___). These divide sections, so they
# bound a section rather than belonging to it.
THEMATIC_BREAK_RE = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")

# An acceptance-traceability row: `| criterion | source | verification | PASS |`
AUDIT_VERDICT_RE = re.compile(r"\b(PASS|FAIL|MISSING)\b")


def _is_section_boundary(line: str) -> bool:
    """True if `line` ends a section: an h1/h2 heading or a thematic break."""
    return bool(re.match(r"^#{1,2}\s+\S", line)) or bool(
        THEMATIC_BREAK_RE.match(line.strip())
    )


def _select(lines: list[str], needle: str) -> list[int]:
    """Indices of the unchecked items `needle` selects.

    An item whose full text equals `needle` wins; otherwise every item that
    contains it. More than one index means the selection is ambiguous and the
    caller must not act on it.
    """
    if not needle:
        return []
    items = [
        (i, m.group("rest").strip())
        for i, ln in enumerate(lines)
        if (m := UNCHECKED_RE.match(ln))
    ]
    exact = [i for i, text in items if text == needle.strip()]
    return exact or [i for i, text in items if needle in text]


def reword_items(
    body: str, rewords: list[tuple[str, str]]
) -> tuple[str, dict[str, int]]:
    """Rewrite text in the one unchecked item each OLD selects.

    Ticking an item whose text says "not yet observed" produces a line that
    contradicts itself, so the rewrite happens alongside the flip. Checked
    items are left byte-for-byte: nobody re-verified them in this run. A phrase
    like "not yet observed" often sits on several items, and rewording all of
    them would make unverified items read as verified, so an OLD that selects
    more than one item changes nothing.

    Returns the new body and, per OLD, how many unchecked items it selected.
    """
    lines = body.splitlines()
    counts: dict[str, int] = {}
    for old, new in rewords:
        hits = _select(lines, old)
        counts[old] = len(hits)
        if len(hits) == 1:
            m = UNCHECKED_RE.match(lines[hits[0]])
            lines[hits[0]] = f"{m.group('prefix')}[ ]{m.group('rest').replace(old, new)}"
    result = "\n".join(lines)
    return (result + "\n" if body.endswith("\n") else result), counts


def tick_items(body: str, checks: list[str]) -> tuple[str, dict[str, int]]:
    """Flip the one unchecked item each check selects.

    Every check is resolved against the body as given, so the outcome does not
    depend on the order of --check flags. A check that selects several items
    flips none of them.

    Returns the new body and, per check, how many unchecked items it selected:
    0 no match, 1 ticked, more than 1 ambiguous and left alone.
    """
    lines = body.splitlines()
    hits = {c: _select(lines, c) for c in checks}
    out = list(lines)
    for idx in hits.values():
        if len(idx) == 1:
            m = UNCHECKED_RE.match(lines[idx[0]])
            out[idx[0]] = f"{m.group('prefix')}[x]{m.group('rest')}"
    result = "\n".join(out)
    counts = {c: len(idx) for c, idx in hits.items()}
    return (result + "\n" if body.endswith("\n") else result), counts


def audit_conflicts(body: str) -> list[str]:
    """Ticked items whose text appears in a FAIL/MISSING traceability row.

    A dual-track body states status twice: once as a checkbox, once as a row in
    the acceptance table. Disagreement between them is the kind of thing a
    reviewer trusts and should not have to cross-check by eye.
    """
    checked_texts = [
        m.group("rest").strip()
        for m in (CHECKED_RE.match(ln) for ln in body.splitlines())
        if m
    ]
    bad_rows = [
        ln
        for ln in body.splitlines()
        if ln.lstrip().startswith("|")
        and (m := AUDIT_VERDICT_RE.search(ln))
        and m.group(1) in {"FAIL", "MISSING"}
    ]
    conflicts = []
    for text in checked_texts:
        # Compare on the item's leading words; full lines rarely match verbatim
        # across a checkbox and a table cell.
        stem = re.sub(r"[*`_]", "", text).strip()[:40]
        if len(stem) < 12:
            continue
        for row in bad_rows:
            if stem.lower() in re.sub(r"[*`_]", "", row).lower():
                conflicts.append(f"{stem!r} is ticked but a table row says FAIL/MISSING")
                break
    return conflicts


def _remove_existing_section(lines: list[str], title: str) -> list[str]:
    """Strip an existing section (and one separator blank before it).

    Replace == remove-then-insert, so the insert path stays the single source of
    truth for spacing.
    """
    start = next((i for i, l in enumerate(lines) if l.strip() == title), -1)
    if start == -1:
        return lines
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if _is_section_boundary(lines[j]):
            end = j
            break
    pre = start - 1 if start > 0 and lines[start - 1].strip() == "" else start
    return lines[:pre] + lines[end:]


def _insertion_index(
    lines: list[str],
    anchor_heading: str | None = None,
    before_heading: str | None = None,
) -> int:
    """Where a fresh section goes.

    Order of preference:
      1. immediately before `before_heading` — the caller pinning placement,
         which is how a dual-track body keeps the section between Verification
         and "Not included / out of scope";
      2. after the last task line under `anchor_heading` if given, else under
         the first `##`+ heading whose text looks like a checklist;
      3. end of file.
    """
    if before_heading:
        idx = next(
            (i for i, ln in enumerate(lines) if ln.strip().startswith(before_heading)),
            None,
        )
        if idx is not None:
            return idx

    if anchor_heading:
        heading_idx = next(
            (i for i, ln in enumerate(lines) if ln.strip() == anchor_heading.strip()),
            None,
        )
    else:
        heading_idx = next(
            (i for i, ln in enumerate(lines) if ANCHOR_HEADING_RE.match(ln)), None
        )
    if heading_idx is None:
        return len(lines)

    last_task = heading_idx
    for k in range(heading_idx + 1, len(lines)):
        if ANY_TASK_RE.match(lines[k]):
            last_task = k
        elif re.match(r"^#{1,6}\s+\S", lines[k]) or THEMATIC_BREAK_RE.match(
            lines[k].strip()
        ):
            break
    return last_task + 1


def upsert_section(
    body: str,
    section_md: str,
    title: str = DEFAULT_SECTION_TITLE,
    anchor_heading: str | None = None,
    before_heading: str | None = None,
) -> str:
    """Insert or replace a section idempotently."""
    block_lines = [title, ""] + section_md.strip().splitlines()
    lines = _remove_existing_section(body.splitlines(), title)
    at = _insertion_index(lines, anchor_heading, before_heading)

    before, after = lines[:at], lines[at:]
    chunk: list[str] = []
    if before and before[-1].strip() != "":
        chunk.append("")
    chunk += block_lines
    if after and after[0].strip() != "":
        chunk.append("")

    result = "\n".join(before + chunk + after)
    return result + "\n" if body.endswith("\n") else result


def _parse_reword(spec: str) -> tuple[str, str]:
    if "::" not in spec:
        raise argparse.ArgumentTypeError(
            f"--reword needs 'OLD::NEW', got {spec!r}"
        )
    old, new = spec.split("::", 1)
    return old, new


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--body-file", required=True)
    ap.add_argument(
        "--check", action="append", default=[],
        help="Unchecked item to tick: its full text, or text found in exactly "
        "one unchecked item. Repeatable.",
    )
    ap.add_argument(
        "--reword", action="append", default=[], type=_parse_reword,
        help="'OLD::NEW' rewrite in the one unchecked item OLD selects. Repeatable.",
    )
    ap.add_argument("--section-file", help="Markdown body for the evidence section.")
    ap.add_argument("--section-title", default=DEFAULT_SECTION_TITLE)
    ap.add_argument("--anchor-heading", help="Exact heading whose checklist to follow.")
    ap.add_argument(
        "--before-heading",
        help="Insert immediately before this heading (prefix match).",
    )
    ap.add_argument(
        "--audit-table", action="store_true",
        help="Warn when a ticked item conflicts with a FAIL/MISSING table row.",
    )
    ap.add_argument("--out")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    try:
        body = Path(args.body_file).read_text(encoding="utf-8")
    except OSError as e:
        print(f"error: cannot read --body-file: {e}", file=sys.stderr)
        return 1

    # Reword before ticking: the caller's --check may target the new wording.
    body, reworded = reword_items(body, args.reword)
    body, matched = tick_items(body, args.check)

    if args.section_file:
        try:
            section_md = Path(args.section_file).read_text(encoding="utf-8")
        except OSError as e:
            print(f"error: cannot read --section-file: {e}", file=sys.stderr)
            return 1
        body = upsert_section(
            body, section_md, args.section_title,
            args.anchor_heading, args.before_heading,
        )

    unresolved = []
    for flag, counts in (("--check", matched), ("--reword", reworded)):
        for text, n in counts.items():
            if n == 0:
                unresolved.append(f"{flag} {text!r}: no unchecked item matched")
            elif n > 1:
                unresolved.append(
                    f"{flag} {text!r}: matched {n} unchecked items, changed none; "
                    "pass the item's full text"
                )
    for msg in unresolved:
        print(f"warning: {msg}", file=sys.stderr)

    conflicts = audit_conflicts(body) if args.audit_table else []
    for c in conflicts:
        print(f"warning: {c}", file=sys.stderr)

    if args.in_place:
        Path(args.body_file).write_text(body, encoding="utf-8")
    elif args.out:
        Path(args.out).write_text(body, encoding="utf-8")
    else:
        sys.stdout.write(body)

    if args.strict and conflicts:
        return 3
    if args.strict and unresolved:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
