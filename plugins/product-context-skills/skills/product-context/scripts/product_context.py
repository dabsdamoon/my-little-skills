#!/usr/bin/env python3
"""Offline product evidence and decision CLI. Python 3.10+, standard library only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from context_core import (ContextError, collect, fail, git_head, json_digest, links,
                          load_config, parse_json, text, within)
from context_store import (effective_decisions, load, save, timestamp,
                           validate_decision, writer)


def inspect(root: Path, config: dict):
    files, contents, missing, total = collect(root, config)
    review = load(root, "review.json", config["product"])
    history = load(root, "decisions.json", config["product"])
    records = history["records"] if history else []
    snapshot = json_digest({"config": config, "files": files, "decisions": records})
    status = "unreviewed" if review is None else "current" if review["snapshot"] == snapshot else "stale"
    previous = review["files"] if review else {}
    changes = [{"path": p, "kind": "added" if p not in previous else "deleted" if p not in files else "modified"}
               for p in sorted(set(files) | set(previous)) if files.get(p) != previous.get(p)]
    broken, external = links(root, contents)
    return {"schema_version": 1, "product": config["product"], "snapshot": snapshot,
            "git_head": git_head(root), "model_calls": 0, "provider_execution": False,
            "review": {"status": status, "questions": review["questions"] if review else [],
                       "actor": review.get("actor") if review else None,
                       "note": review.get("note") if review else None},
            "files": files, "source_bytes": total, "changes": changes,
            "missing_sources": missing, "broken_links": broken, "external_references": external,
            "topics": config["topics"], "decisions": effective_decisions(records, files)}


def packet(report: dict) -> str:
    lines = [f"# Product context: {report['product']}", "",
             "Offline inspection only. No model or provider was started.",
             "This packet is not permission to run OpenWiki or a paid generation job.",
             "A current review means these evidence versions were inspected; it is not product acceptance.", "",
             f"Snapshot: `{report['snapshot']}`", f"Review: {report['review']['status']}", "",
             "## Evidence changes", ""]
    lines += [f"- {c['kind']}: `{c['path']}`" for c in report["changes"]] or ["- No source-file changes."]
    lines += ["", "## Review questions", ""]
    lines += [f"- {q}" for q in report["review"]["questions"]]
    for topic in report["topics"]:
        lines += [f"- {topic['id']}: {topic['question']}", "  Sources: " + ", ".join(f"`{p}`" for p in topic["sources"])]
    lines += ["", "## Decision history", ""]
    if not report["decisions"]:
        lines.append("- No decisions recorded by this harness.")
    for decision in report["decisions"]:
        lines += [f"- {decision['id']} ({decision['effective_status']}): {decision['title']} — {decision['reason']}",
                  "  Scope: " + decision.get("scope", "unspecified; do not assume global applicability"),
                  f"  Recorded status: {decision['status']}; actor: {decision['actor']}"]
        for field, label in [("supersedes", "Supersedes"), ("reconsiders", "Reconsiders")]:
            if decision.get(field):
                lines.append(f"  {label}: " + ", ".join(decision[field]))
        lines.append("  Evidence changed: " + ("yes" if decision["evidence_changed"] else "no"))
        for evidence in decision["evidence"]:
            lines.append(f"  Evidence: `{evidence['path']}` at recorded SHA-256 `{evidence['sha256']}`")
    lines += ["", "## Structural findings", ""]
    lines += [f"- Missing source: `{p}`" for p in report["missing_sources"]]
    lines += [f"- Missing target: `{b['source']}:{b['line']}` → `{b['target']}`" for b in report["broken_links"]]
    lines += [f"- Outside-product reference (unverified): `{e['source']}:{e['line']}` → `{e['target']}`"
              for e in report["external_references"]]
    lines += ["", "## Evidence versions", ""]
    lines += [f"- `{p}`: `{sha}`" for p, sha in report["files"].items()]
    lines += ["", "Read the relevant sources selectively. Preserve previous decisions and unresolved questions.",
              "Separate observed implementation, intended behavior, proposals, and environment-specific verification.",
              "Semantic contradictions need review; file hashes alone cannot resolve them."]
    return "\n".join(lines) + "\n"


def initialize(root: Path, args):
    destination = root / ".product-context.json"
    within(root, destination)
    product = text(args.product, "product")
    if args.profile:
        config = parse_json(Path(args.profile), "INVALID_CONFIG")
        if not isinstance(config, dict):
            fail("INVALID_CONFIG", "A profile must contain a JSON object.")
        config["product"] = product
    else:
        sources = [name for name in ["README.md", "AGENTS.md", "PRD.md", "RECIPE.md"] if (root / name).is_file()]
        if (root / "docs").is_dir():
            sources.append("docs/**/*.md")
        config = {"schema_version": 1, "product": product, "sources": sources, "exclude": [], "topics": []}
    # Validate without writing to the product before success.
    import tempfile
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        config = load_config(root, path)
    try:
        with destination.open("x", encoding="utf-8") as handle:
            json.dump(config, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except FileExistsError:
        fail("CONFIG_EXISTS", "Existing .product-context.json was left unchanged.")
    return {"product": product, "config": ".product-context.json", "model_calls": 0}


def record_review(root: Path, config: dict, args):
    text(args.actor, "actor", "INVALID_REVIEW")
    text(args.note, "note", "INVALID_REVIEW")
    with writer(root):
        report = inspect(root, config)
        if report["snapshot"] != args.snapshot:
            fail("SNAPSHOT_CHANGED", "Evidence changed after inspection. Run check/prepare again.")
        questions = list(report["review"]["questions"])
        for question in args.resolve_question:
            if question not in questions:
                fail("INVALID_REVIEW", "Cannot resolve an unknown question.")
            questions.remove(question)
        for question in args.question:
            text(question, "question", "INVALID_REVIEW")
            if question not in questions:
                questions.append(question)
        review = {"schema_version": 1, "product": config["product"], "snapshot": args.snapshot,
                  "files": report["files"], "questions": questions, "actor": args.actor,
                  "note": args.note, "recorded_at": timestamp(), "git_head": report["git_head"]}
        save(root, "review.json", review)
    return {"product": config["product"], "snapshot": args.snapshot, "review": "recorded", "questions": questions,
            "model_calls": 0}


def add_decision(root: Path, config: dict, args):
    entry = parse_json(Path(args.file), "INVALID_DECISION")
    with writer(root):
        history = load(root, "decisions.json", config["product"]) or {
            "schema_version": 1, "product": config["product"], "records": []}
        previous = {record["id"] for record in history["records"]}
        validate_decision(entry, previous)
        report = inspect(root, config)
        for source in entry["evidence"]:
            if source not in report["files"]:
                fail("INVALID_DECISION", "Decision evidence must be a currently selected source file.")
        entry = {**entry, "recorded_at": timestamp(),
                 "evidence": [{"path": p, "sha256": report["files"][p]} for p in entry["evidence"]]}
        history["records"].append(entry)
        save(root, "decisions.json", history)
    return {"product": config["product"], "decision": entry["id"], "model_calls": 0}


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    subs = result.add_subparsers(dest="command", required=True)
    for name in ["init", "check", "prepare", "record", "decision"]:
        command = subs.add_parser(name)
        command.add_argument("--repo", default=".", help="Explicit product root (default: current directory).")
        command.add_argument("--config", help="An external profile or product configuration; read-only.")
        if name == "init":
            command.add_argument("--product", required=True)
            command.add_argument("--profile", help="Optional configuration template to install locally.")
        if name == "check":
            command.add_argument("--json", action="store_true")
            command.add_argument("--require-reviewed", action="store_true", help="Opt in to a freshness failure.")
        if name == "record":
            command.add_argument("--snapshot", required=True)
            command.add_argument("--actor", required=True, help="Attribution, not authenticated approval.")
            command.add_argument("--note", required=True)
            command.add_argument("--question", action="append", default=[])
            command.add_argument("--resolve-question", action="append", default=[])
        if name == "decision":
            command.add_argument("--file", required=True, help="JSON decision record; never executed.")
    return result


def main():
    args = parser().parse_args()
    root = Path(args.repo).resolve()
    try:
        if not root.is_dir():
            fail("INVALID_ROOT", "--repo must identify an existing product directory.")
        if args.command == "init":
            result = initialize(root, args)
        else:
            config = load_config(root, Path(args.config).resolve() if args.config else None)
            if args.command in {"check", "prepare"}:
                result = inspect(root, config)
                if args.command == "prepare" or not args.json:
                    print(packet(result), end="")
                else:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                return int(bool(result["broken_links"] or result["missing_sources"] or
                                (getattr(args, "require_reviewed", False) and result["review"]["status"] != "current")))
            result = record_review(root, config, args) if args.command == "record" else add_decision(root, config, args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except ContextError as error:
        print(json.dumps({"error": error.code, "message": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except OSError:
        print(json.dumps({"error": "IO_ERROR", "message": "Local filesystem operation failed; no provider was started."}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
