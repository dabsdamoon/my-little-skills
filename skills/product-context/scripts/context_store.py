"""Explicit local writes and immutable decision records."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile

from context_core import fail, parse_json, pattern, text, within


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def state_path(root: Path, name: str) -> Path:
    path = root / ".product-context" / name
    within(root, path)
    return path


def load(root: Path, name: str, product: str):
    path = state_path(root, name)
    if not path.exists():
        return None
    data = parse_json(path, "INVALID_STATE")
    if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("product") != product:
        fail("INVALID_STATE", f"Unsupported or different-product state: {name}")
    if name == "review.json":
        if (not isinstance(data.get("snapshot"), str) or len(data["snapshot"]) != 64
                or not isinstance(data.get("files"), dict)
                or not isinstance(data.get("questions"), list)
                or any(not isinstance(q, str) for q in data["questions"])):
            fail("INVALID_STATE", "Invalid review record.")
    elif name == "decisions.json":
        if not isinstance(data.get("records"), list):
            fail("INVALID_STATE", "Invalid decision history.")
        previous = set()
        for entry in data["records"]:
            validate_decision(entry, previous, stored=True)
            previous.add(entry["id"])
    return data


@contextmanager
def writer(root: Path):
    directory = state_path(root, "review.json").parent
    directory.mkdir(exist_ok=True)
    lock = state_path(root, ".lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        fail("LOCKED", "Another writer holds .product-context/.lock; inspect it before retrying.")
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()


def save(root: Path, name: str, value):
    path = state_path(root, name)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def validate_decision(entry, previous: set, stored: bool = False):
    code = "INVALID_STATE" if stored else "INVALID_DECISION"
    required = {"id", "title", "status", "reason", "actor", "evidence"}
    optional = {"scope", "supersedes", "reconsiders", "recorded_at"} if stored else {"scope", "supersedes", "reconsiders"}
    if not isinstance(entry, dict) or not required <= set(entry) or set(entry) - required - optional:
        fail(code, "A decision needs id, title, status, reason, actor, evidence and supported fields only.")
    for field in ["id", "title", "reason", "actor"]:
        text(entry[field], field, code)
    if entry["id"] in previous:
        fail(code, "Decision ids are immutable and cannot be reused.")
    if not isinstance(entry["status"], str) or entry["status"] not in {"proposed", "accepted", "reconsideration"}:
        fail(code, "Decision status must be proposed, accepted, or reconsideration.")
    if "scope" in entry:
        text(entry["scope"], "scope", code)
    for relationship in ["supersedes", "reconsiders"]:
        targets = entry.get(relationship, [])
        if not isinstance(targets, list) or any(not isinstance(t, str) or t not in previous for t in targets):
            fail(code, f"{relationship} must reference existing decision ids.")
    if entry["status"] == "reconsideration" and not entry.get("reconsiders"):
        fail(code, "A reconsideration must identify the decision being reconsidered.")
    evidence = entry["evidence"]
    if not isinstance(evidence, list) or not evidence:
        fail(code, "A decision needs at least one source of evidence.")
    for item in evidence:
        if stored:
            if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
                fail(code, "Invalid stored decision evidence.")
            pattern(item["path"])
            if not isinstance(item["sha256"], str) or len(item["sha256"]) != 64:
                fail(code, "Invalid evidence digest.")
        else:
            pattern(item)


def effective_decisions(records: list, files: dict):
    superseded, reconsidered = {}, {}
    for entry in records:
        if entry["status"] == "accepted":
            for target in entry.get("supersedes", []):
                superseded.setdefault(target, []).append(entry["id"])
        if entry["status"] == "reconsideration":
            for target in entry["reconsiders"]:
                reconsidered.setdefault(target, []).append(entry["id"])
    result = []
    for entry in records:
        status = entry["status"]
        if entry["id"] in superseded:
            status = "superseded"
        elif entry["id"] in reconsidered:
            status = "under-review"
        elif status == "reconsideration" and all(t in superseded for t in entry["reconsiders"]):
            status = "resolved"
        result.append({**entry, "effective_status": status,
                       "superseded_by": superseded.get(entry["id"], []),
                       "evidence_changed": any(files.get(e["path"]) != e["sha256"] for e in entry["evidence"])})
    return result
