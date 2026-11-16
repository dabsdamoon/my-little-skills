"""Bounded, offline evidence collection. No provider or shell execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess
from urllib.parse import unquote, urlsplit


RESERVED = {".git", ".product-context", "node_modules", ".venv", "venv", "__pycache__"}
CONFIG_KEYS = {"schema_version", "product", "sources", "exclude", "topics", "max_file_bytes"}


class ContextError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def fail(code: str, message: str):
    raise ContextError(code, message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def json_digest(value) -> str:
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode())


def text(value, name: str, code: str = "INVALID_CONFIG") -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 10000:
        fail(code, f"{name} must be a nonempty string (at most 10000 characters).")
    return value


def pattern(value) -> str:
    value = text(value, "source path")
    if PurePosixPath(value).is_absolute() or PureWindowsPath(value).drive or "\\" in value:
        fail("UNSAFE_PATH", "Use relative, forward-slash product paths.")
    if ".." in PurePosixPath(value).parts:
        fail("UNSAFE_PATH", "Product paths cannot traverse parent directories.")
    return value


def within(root: Path, path: Path) -> Path:
    try:
        result = path.resolve()
        result.relative_to(root.resolve())
        return result
    except (ValueError, RuntimeError, OSError):
        fail("UNSAFE_PATH", "A configured path or symlink leaves the product root.")


def reserved(path: Path) -> bool:
    return any(part in RESERVED or part == ".env" or part.startswith(".env.") for part in path.parts)


def parse_json(path: Path, code: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        fail(code, f"Cannot read valid JSON: {path.name}")


def load_config(root: Path, path: Path | None = None):
    path = path or root / ".product-context.json"
    if path == root / ".product-context.json":
        within(root, path)
    data = parse_json(path, "INVALID_CONFIG")
    if not isinstance(data, dict) or set(data) - CONFIG_KEYS or data.get("schema_version") != 1:
        fail("INVALID_CONFIG", "Expected schema_version 1 and supported configuration fields only.")
    text(data.get("product"), "product")
    for name in ["sources", "exclude"]:
        values = data.get(name, [] if name == "exclude" else None)
        if not isinstance(values, list) or (name == "sources" and not values):
            fail("INVALID_CONFIG", f"{name} must be a list; sources cannot be empty.")
        for value in values:
            pattern(value)
        data[name] = values
    limit = data.get("max_file_bytes", 1048576)
    if type(limit) is not int or not 1 <= limit <= 10485760:
        fail("INVALID_CONFIG", "max_file_bytes must be an integer from 1 to 10485760.")
    data["max_file_bytes"] = limit
    topics = data.get("topics", [])
    if not isinstance(topics, list):
        fail("INVALID_CONFIG", "topics must be a list.")
    ids = set()
    for topic in topics:
        if not isinstance(topic, dict) or set(topic) != {"id", "question", "sources"}:
            fail("INVALID_CONFIG", "Each topic needs exactly id, question, sources.")
        if text(topic["id"], "topic id") in ids:
            fail("INVALID_CONFIG", "Topic ids must be unique.")
        ids.add(topic["id"])
        text(topic["question"], "topic question")
        if not isinstance(topic["sources"], list) or not topic["sources"]:
            fail("INVALID_CONFIG", "Topic sources must be a nonempty list.")
        for value in topic["sources"]:
            pattern(value)
    data["topics"] = topics
    return data


def collect(root: Path, config: dict):
    files, contents, missing = {}, {}, []
    total = 0
    excluded = {path.relative_to(root) for selector in config["exclude"] for path in root.glob(selector)}
    for selector in config["sources"]:
        matched = False
        for path in sorted(root.glob(selector)):
            relative = path.relative_to(root)
            if reserved(relative):
                continue
            if relative in excluded or any(parent in excluded for parent in relative.parents):
                continue
            resolved = within(root, path)
            if reserved(resolved.relative_to(root)) or not resolved.is_file():
                continue
            matched = True
            name = relative.as_posix()
            if name in files:
                continue
            if len(files) >= 1000:
                fail("SCOPE_TOO_LARGE", "Select at most 1000 evidence files.")
            try:
                size = resolved.stat().st_size
                if size > config["max_file_bytes"]:
                    fail("SOURCE_TOO_LARGE", f"Evidence exceeds max_file_bytes: {name}")
                raw = resolved.read_bytes()
                if len(raw) > config["max_file_bytes"]:
                    fail("SOURCE_TOO_LARGE", f"Evidence exceeds max_file_bytes: {name}")
                total += len(raw)
                if total > 8388608:
                    fail("SCOPE_TOO_LARGE", "Select at most 8 MiB of source evidence.")
            except OSError:
                fail("SOURCE_UNREADABLE", f"Cannot read selected evidence: {name}")
            files[name] = digest(raw)
            if path.suffix.lower() in {".md", ".mdx"}:
                try:
                    contents[name] = raw.decode("utf-8")
                except UnicodeError:
                    fail("SOURCE_UNREADABLE", f"Markdown must use UTF-8: {name}")
        if not matched and not any(c in selector for c in "*?["):
            missing.append(selector)
    if not files:
        fail("EMPTY_SCOPE", "No evidence files were selected; review the product configuration.")
    return dict(sorted(files.items())), contents, sorted(set(missing)), total


def links(root: Path, contents: dict):
    broken, external = [], []
    for source, content in contents.items():
        fence = None
        for line_number, line in enumerate(content.splitlines(), 1):
            stripped = line.lstrip()
            start = re.match(r"(`{3,}|~{3,})", stripped)
            if start:
                token = start.group(1)
                if fence is None:
                    fence = token[0]
                elif token[0] == fence:
                    fence = None
                continue
            if fence:
                continue
            for match in re.finditer(r"(?<!!)\[[^\]]*\]\((<[^>]+>|[^)\n]+)\)", line):
                target = match.group(1).strip()
                if target.startswith("<"):
                    target = target[1:target.index(">")]
                else:
                    target = re.split(r'\s+[\"\']', target, maxsplit=1)[0]
                if not target or target.startswith("#"):
                    continue
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("//"):
                    continue  # External URLs are outside this offline local-link contract.
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc:
                    continue  # No network lookups, including file:// URLs.
                name = unquote(parsed.path)
                if not name:
                    continue
                evidence = {"source": source, "line": line_number, "target": target}
                if name.startswith("/") or PureWindowsPath(name).drive:
                    external.append(evidence)
                    continue
                try:
                    destination = (root / source).parent.joinpath(name).resolve()
                    destination.relative_to(root)
                except (ValueError, RuntimeError, OSError):
                    external.append(evidence)
                    continue
                if reserved(destination.relative_to(root)):
                    external.append(evidence)
                elif not destination.exists():
                    broken.append(evidence)
    return broken, external


def git_head(root: Path):
    try:
        process = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(root), "rev-parse", "--verify", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return process.stdout.strip() if process.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None
