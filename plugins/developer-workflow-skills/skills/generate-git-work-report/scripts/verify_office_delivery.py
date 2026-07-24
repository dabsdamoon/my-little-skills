#!/usr/bin/env python3
"""Preflight DOCX/PDF work-report pairs after full-page visual inspection."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile


PLACEHOLDER_RE = re.compile(
    r"(?:\bTODO\b|\bTBD\b|Lorem ipsum|"
    r"\[\s*(?:PLACEHOLDER|[^\]\n]{0,40}(?:입력|작성 필요))\s*\])",
    re.IGNORECASE,
)
REQUIRED_DOCX_PARTS = {
    "[Content_Types].xml",
    "_rels/.rels",
    "word/document.xml",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify DOCX/PDF work-report delivery pairs."
    )
    parser.add_argument(
        "--pair",
        action="append",
        required=True,
        metavar="LABEL=DOCX,PDF",
        help="Named DOCX/PDF pair. Repeat for external and internal reports.",
    )
    parser.add_argument(
        "--reference-mode",
        action="store_true",
        help="Require a retained-template audit.",
    )
    parser.add_argument(
        "--template-audit",
        help="Task-local artifact.md created from the retained reference.",
    )
    parser.add_argument(
        "--visual-qa-confirmed",
        action="store_true",
        help="Confirm every final page was inspected at 100%% zoom.",
    )
    parser.add_argument("--output", required=True, help="Verification JSON output.")
    return parser.parse_args()


def parse_pair(value: str) -> tuple[str, Path, Path]:
    try:
        label, paths = value.split("=", 1)
        docx_value, pdf_value = paths.split(",", 1)
    except ValueError as error:
        raise ValueError(
            f"invalid --pair {value!r}; expected LABEL=DOCX,PDF"
        ) from error
    label = label.strip()
    if not label:
        raise ValueError(f"invalid --pair {value!r}; label is empty")
    return (
        label,
        Path(docx_value).expanduser().resolve(),
        Path(pdf_value).expanduser().resolve(),
    )


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def run_command(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
    return completed.stdout


def docx_text(path: Path) -> tuple[str, dict[str, object]]:
    try:
        with ZipFile(path) as archive:
            corrupt = archive.testzip()
            names = set(archive.namelist())
            if corrupt:
                raise ValueError(f"corrupt DOCX member: {corrupt}")
            missing = sorted(REQUIRED_DOCX_PARTS - names)
            if missing:
                raise ValueError(f"missing DOCX parts: {', '.join(missing)}")
            root = ElementTree.fromstring(archive.read("word/document.xml"))
    except (BadZipFile, OSError, ElementTree.ParseError) as error:
        raise ValueError(f"invalid DOCX package: {error}") from error

    text = " ".join(
        element.text or ""
        for element in root.iter()
        if element.tag.endswith("}t")
    )
    details = {
        "characters": len(re.sub(r"\s+", "", text)),
        "has_header": any(name.startswith("word/header") for name in names),
        "has_footer": any(name.startswith("word/footer") for name in names),
    }
    return text, details


def pdf_page_count(path: Path) -> int:
    output = run_command(["pdfinfo", str(path)])
    match = re.search(r"^Pages:\s+(\d+)\s*$", output, re.MULTILINE)
    if not match:
        raise ValueError("pdfinfo did not report a page count")
    return int(match.group(1))


def pdf_page_text(path: Path, page: int) -> str:
    return run_command(
        [
            "pdftotext",
            "-f",
            str(page),
            "-l",
            str(page),
            "-layout",
            str(path),
            "-",
        ]
    )


def inspect_pair(
    label: str,
    docx_path: Path,
    pdf_path: Path,
) -> tuple[dict[str, object], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    result: dict[str, object] = {
        "label": label,
        "docx": str(docx_path),
        "pdf": str(pdf_path),
    }

    if docx_path.suffix.lower() != ".docx":
        errors.append(f"{label}: DOCX path must end with .docx")
    if pdf_path.suffix.lower() != ".pdf":
        errors.append(f"{label}: PDF path must end with .pdf")
    if docx_path.stem != pdf_path.stem:
        errors.append(f"{label}: DOCX/PDF basenames do not match")
    if not docx_path.is_file():
        errors.append(f"{label}: DOCX not found: {docx_path}")
    if not pdf_path.is_file():
        errors.append(f"{label}: PDF not found: {pdf_path}")
    if errors:
        return result, errors, warnings

    try:
        text, docx_details = docx_text(docx_path)
        result["docx_package"] = docx_details
        if docx_details["characters"] < 80:
            errors.append(f"{label}: DOCX contains too little text")
        if PLACEHOLDER_RE.search(text):
            errors.append(f"{label}: DOCX contains an unresolved placeholder")
    except ValueError as error:
        errors.append(f"{label}: {error}")

    try:
        pages = pdf_page_count(pdf_path)
        page_metrics: list[dict[str, int]] = []
        if pages < 1:
            errors.append(f"{label}: PDF has no pages")
        for page in range(1, pages + 1):
            page_text = pdf_page_text(pdf_path, page)
            characters = len(re.sub(r"\s+", "", page_text))
            page_metrics.append({"page": page, "characters": characters})
            if characters < 20:
                errors.append(
                    f"{label}: PDF page {page} is blank or unreadable "
                    f"({characters} text characters)"
                )
            elif characters < 80:
                warnings.append(
                    f"{label}: PDF page {page} is sparse "
                    f"({characters} text characters); verify intent"
                )
            if PLACEHOLDER_RE.search(page_text):
                errors.append(
                    f"{label}: PDF page {page} contains an unresolved placeholder"
                )
        result["pdf_pages"] = pages
        result["page_text_metrics"] = page_metrics
    except (RuntimeError, ValueError) as error:
        errors.append(f"{label}: PDF inspection failed: {error}")

    return result, errors, warnings


def main() -> int:
    args = parse_args()
    output_path = Path(args.output).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    documents: list[dict[str, object]] = []

    if shutil.which("pdfinfo") is None or shutil.which("pdftotext") is None:
        errors.append("pdfinfo and pdftotext are required for office preflight")

    if not args.visual_qa_confirmed:
        errors.append("full-page visual QA was not confirmed")

    audit_path: Path | None = None
    if args.reference_mode:
        if not args.template_audit:
            errors.append("reference mode requires --template-audit")
        else:
            audit_path = Path(args.template_audit).expanduser().resolve()
            if not audit_path.is_file() or audit_path.stat().st_size < 80:
                errors.append(f"template audit is missing or empty: {audit_path}")
    elif args.template_audit:
        warnings.append("--template-audit supplied without --reference-mode")

    labels: set[str] = set()
    for pair_value in args.pair:
        try:
            label, docx_path, pdf_path = parse_pair(pair_value)
        except ValueError as error:
            errors.append(str(error))
            continue
        if label in labels:
            errors.append(f"duplicate pair label: {label}")
            continue
        labels.add(label)
        result, pair_errors, pair_warnings = inspect_pair(
            label, docx_path, pdf_path
        )
        documents.append(result)
        errors.extend(pair_errors)
        warnings.extend(pair_warnings)

    status = "pass" if not errors else "fail"
    payload: dict[str, object] = {
        "status": status,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "mode": "reference-first" if args.reference_mode else "neutral-fallback",
        "template_audit": str(audit_path) if audit_path else None,
        "visual_qa_confirmed": bool(args.visual_qa_confirmed),
        "documents": documents,
        "errors": errors,
        "warnings": warnings,
    }
    atomic_write_json(output_path, payload)

    print(
        status.upper(),
        f"pairs={len(documents)}",
        f"errors={len(errors)}",
        f"warnings={len(warnings)}",
    )
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
