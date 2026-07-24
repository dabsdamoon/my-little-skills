#!/usr/bin/env python3
"""Render deterministic Markdown drafts from a Git work-report evidence bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from html import escape as html_escape
from pathlib import Path


SCHEMA = "https://dabsdamoon.github.io/schemas/git-work-report-evidence-v1.json"
EXTERNAL_NAME = "external-project-history.md"
INTERNAL_NAME = "internal-work-log.md"
CATEGORY_KO = {
    "feature": "기능 개발",
    "fix": "오류 수정",
    "documentation": "문서화",
    "test": "테스트",
    "refactor": "리팩터링",
    "performance": "성능 개선",
    "ci": "CI",
    "build": "빌드",
    "style": "스타일",
    "maintenance": "유지보수",
    "release": "릴리스",
    "revert": "되돌리기",
    "merge": "병합",
    "other": "기타",
}
CATEGORY_EN = {
    "feature": "Features",
    "fix": "Fixes",
    "documentation": "Documentation",
    "test": "Tests",
    "refactor": "Refactoring",
    "performance": "Performance",
    "ci": "CI",
    "build": "Build",
    "style": "Style",
    "maintenance": "Maintenance",
    "release": "Releases",
    "revert": "Reverts",
    "merge": "Merges",
    "other": "Other",
}
PLACEHOLDER_PATTERN = re.compile(r"\b(?:TODO|TBD|Lorem ipsum)\b", re.IGNORECASE)


class RenderError(RuntimeError):
    """Raised when evidence cannot be rendered without losing integrity."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render external and internal Markdown work reports."
    )
    parser.add_argument("--evidence", required=True, help="git-evidence.json path.")
    parser.add_argument("--output-dir", required=True, help="Directory for report drafts.")
    parser.add_argument("--project-name", help="Display name; defaults to repository name.")
    parser.add_argument(
        "--language",
        choices=("ko", "en"),
        default="ko",
        help="Report language (default: ko).",
    )
    parser.add_argument(
        "--external-name",
        default=EXTERNAL_NAME,
        help=f"External Markdown filename (default: {EXTERNAL_NAME}).",
    )
    parser.add_argument(
        "--internal-name",
        default=INTERNAL_NAME,
        help=f"Internal Markdown filename (default: {INTERNAL_NAME}).",
    )
    return parser.parse_args()


def load_evidence(path: Path) -> tuple[dict[str, object], str]:
    raw = path.read_bytes()
    try:
        evidence = json.loads(raw)
    except json.JSONDecodeError as error:
        raise RenderError(f"invalid evidence JSON: {error}") from error
    if evidence.get("schema") != SCHEMA:
        raise RenderError(f"unsupported evidence schema: {evidence.get('schema')!r}")
    commits = evidence.get("commits")
    if not isinstance(commits, list) or not commits:
        raise RenderError("evidence has no commits")
    return evidence, hashlib.sha256(raw).hexdigest()


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content.rstrip() + "\n", encoding="utf-8")
    temporary.replace(path)


def clean_cell(value: object) -> str:
    return (
        html_escape(str(value), quote=False)
        .replace("\\", "\\\\")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("|", "\\|")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def format_number(value: object) -> str:
    return f"{int(value):,}"


def evidence_markers(sha256: str, summary: dict[str, object]) -> list[str]:
    keys = (
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
    markers = [
        "<!-- git-work-report:generated -->",
        f"<!-- evidence-sha256:{sha256} -->",
    ]
    markers.extend(f"<!-- metric:{key}={summary[key]} -->" for key in keys)
    return markers


def scope_text(evidence: dict[str, object], language: str) -> str:
    scope = evidence["scope"]
    assert isinstance(scope, dict)
    revision = clean_cell(scope["revision"])
    resolved_tip = scope.get("resolved_tip")
    if resolved_tip:
        revision = f"{revision} ({str(resolved_tip)[:12]})"
    filters = []
    if scope.get("since"):
        filters.append(f"since={clean_cell(scope['since'])}")
    if scope.get("until"):
        filters.append(f"until={clean_cell(scope['until'])}")
    if scope.get("author_filter"):
        filters.append(f"author={clean_cell(scope['author_filter'])}")
    filter_text = ", ".join(filters) if filters else ("없음" if language == "ko" else "none")
    if language == "ko":
        return (
            f"리비전 `{revision}`, 시간대 `{clean_cell(scope['timezone'])}`, "
            f"추가 필터 `{filter_text}`"
        )
    return (
        f"Revision `{revision}`, timezone `{clean_cell(scope['timezone'])}`, "
        f"additional filters `{filter_text}`"
    )


def completeness_lines(evidence: dict[str, object], language: str) -> list[str]:
    completeness = evidence["completeness"]
    repository = evidence["repository"]
    assert isinstance(completeness, dict)
    assert isinstance(repository, dict)
    values = [
        (
            "Shallow 저장소" if language == "ko" else "Shallow repository",
            completeness["is_shallow"],
        ),
        (
            "수집 제한 발생" if language == "ko" else "Collection truncated",
            completeness["truncated"],
        ),
        (
            "작업 트리 변경 존재" if language == "ko" else "Dirty working tree",
            repository["dirty"],
        ),
    ]
    yes, no = (("예", "아니오") if language == "ko" else ("yes", "no"))
    return [f"- {label}: **{yes if value else no}**" for label, value in values]


def external_report(
    evidence: dict[str, object], sha256: str, project_name: str, language: str
) -> str:
    summary = evidence["summary"]
    assert isinstance(summary, dict)
    category_labels = CATEGORY_KO if language == "ko" else CATEGORY_EN
    category_counts = summary["category_counts"]
    assert isinstance(category_counts, dict)
    tags = evidence["tags"]
    assert isinstance(tags, list)
    display_tags = sorted(
        (tag for tag in tags if isinstance(tag, dict)),
        key=lambda tag: (str(tag.get("created_at", "")), str(tag.get("name", ""))),
    )
    generated_date = str(evidence["generated_at"])[:10]
    markers = evidence_markers(sha256, summary)

    if language == "ko":
        lines = [
            *markers,
            f"# {project_name} 프로젝트 수행이력",
            "",
            "- 문서 유형: 외부 제출용 Git 근거 요약",
            f"- 근거 생성일: {generated_date}",
            f"- 근거 식별자: `{sha256[:16]}`",
            f"- 분석 범위: {scope_text(evidence, language)}",
            "",
            "## 1. 보고서 목적",
            "",
            "이 문서는 지정한 Git 이력에서 확인되는 변경 활동과 릴리스 기록을 "
            "외부 검토용으로 요약한다. 제품 목적, 계약 범위, 운영 성과 등 Git이 "
            "직접 증명하지 못하는 내용은 저장소 문서 또는 별도 사업 근거로 보완한다.",
            "",
            "## 2. 수행 개요",
            "",
            "| 항목 | 확인 값 |",
            "|---|---:|",
            f"| 활동 기간 | {summary['period_start']} ~ {summary['period_end']} |",
            f"| 커밋 | {format_number(summary['commit_count'])}건 |",
            f"| 병합 커밋 | {format_number(summary['merge_commit_count'])}건 |",
            f"| 번호형 병합 | {format_number(summary['numbered_merge_commit_count'])}건 |",
            f"| 커밋 활동일 | {format_number(summary['activity_day_count'])}일 |",
            f"| 태그 | {format_number(summary['tag_count'])}개 |",
            f"| 변경 경로 | {format_number(summary['unique_path_count'])}개 |",
            "",
            "## 3. 기록된 수행 영역",
            "",
            "| 분류 | 커밋 수 |",
            "|---|---:|",
        ]
        for category, count in sorted(
            category_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(
                f"| {category_labels.get(category, category)} | {format_number(count)} |"
            )
        lines.extend(
            [
                "",
                "분류는 커밋 제목의 Conventional Commit 접두사와 병합 여부를 기준으로 "
                "정규화한 값이다. 커밋 수는 업무 난이도나 투입 시간을 의미하지 않는다.",
                "",
                "## 4. 릴리스 표식",
                "",
            ]
        )
        if display_tags:
            lines.extend(["| 태그 | 연결 커밋 | 생성 시각 |", "|---|---|---|"])
            for tag in display_tags[-20:]:
                lines.append(
                    f"| {clean_cell(tag['name'])} | `{str(tag['commit'])[:12]}` | "
                    f"{clean_cell(tag['created_at'] or '-')} |"
                )
            if len(display_tags) > 20:
                lines.append(
                    f"\n생성 시각 기준 최근 20개만 표시했으며 전체 태그는 "
                    f"{len(display_tags)}개다."
                )
        else:
            lines.append("분석 범위에서 확인된 태그가 없다.")
        lines.extend(
            [
                "",
                "## 5. 근거 완전성",
                "",
                *completeness_lines(evidence, language),
                "",
                "외부 제출 전 제품 목적, 실제 납품 범위, 검증 결과, 고객 식별정보 및 "
                "보안 민감정보를 별도로 검토해야 한다.",
                "",
                "## 6. 해석 제한",
                "",
                "- Git은 기록된 변경을 보여주지만 회의, 기획, 디자인, 미커밋 작업을 증명하지 않는다.",
                "- 커밋·변경량 통계로 투입 시간, 비용, 생산성 또는 사업 성과를 추정하지 않는다.",
                "- squash, rebase, cherry-pick 및 삭제된 원격 브랜치는 이력의 형태를 바꿀 수 있다.",
            ]
        )
    else:
        lines = [
            *markers,
            f"# {project_name} Project Execution History",
            "",
            "- Document type: External Git-evidence summary",
            f"- Evidence generated: {generated_date}",
            f"- Evidence ID: `{sha256[:16]}`",
            f"- Scope: {scope_text(evidence, language)}",
            "",
            "## 1. Purpose",
            "",
            "This document summarizes change activity and release records visible in "
            "the selected Git history. Product purpose, contractual delivery, and "
            "operational outcomes require separate repository or business evidence.",
            "",
            "## 2. Activity summary",
            "",
            "| Metric | Recorded value |",
            "|---|---:|",
            f"| Activity period | {summary['period_start']} to {summary['period_end']} |",
            f"| Commits | {format_number(summary['commit_count'])} |",
            f"| Merge commits | {format_number(summary['merge_commit_count'])} |",
            f"| Numbered merges | {format_number(summary['numbered_merge_commit_count'])} |",
            f"| Activity days | {format_number(summary['activity_day_count'])} |",
            f"| Tags | {format_number(summary['tag_count'])} |",
            f"| Unique changed paths | {format_number(summary['unique_path_count'])} |",
            "",
            "## 3. Recorded work categories",
            "",
            "| Category | Commits |",
            "|---|---:|",
        ]
        for category, count in sorted(
            category_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(
                f"| {category_labels.get(category, category)} | {format_number(count)} |"
            )
        lines.extend(
            [
                "",
                "Categories are normalized from Conventional Commit prefixes and merge "
                "status. Counts do not represent effort or difficulty.",
                "",
                "## 4. Release markers",
                "",
            ]
        )
        if display_tags:
            lines.extend(["| Tag | Commit | Created |", "|---|---|---|"])
            for tag in display_tags[-20:]:
                lines.append(
                    f"| {clean_cell(tag['name'])} | `{str(tag['commit'])[:12]}` | "
                    f"{clean_cell(tag['created_at'] or '-')} |"
                )
            if len(display_tags) > 20:
                lines.append(
                    f"\nShowing the latest 20 of {len(display_tags)} tags by creation time."
                )
        else:
            lines.append("No tags were found in the selected scope.")
        lines.extend(
            [
                "",
                "## 5. Evidence completeness",
                "",
                *completeness_lines(evidence, language),
                "",
                "Before external submission, review product purpose, actual delivery "
                "scope, verification outcomes, identities, and security-sensitive data.",
                "",
                "## 6. Interpretation limits",
                "",
                "- Git records changes, not meetings, planning, design, or uncommitted work.",
                "- Do not infer hours, cost, productivity, or business impact from counts.",
                "- Squashes, rebases, cherry-picks, and deleted refs can reshape history.",
            ]
        )
    return "\n".join(lines)


def representative_paths(commit: dict[str, object], limit: int = 8) -> str:
    changes = commit["changes"]
    assert isinstance(changes, list)
    paths = [f"`{clean_cell(change['path'])}`" for change in changes[:limit]]
    if not paths:
        return "-"
    suffix = f" … (+{len(changes) - limit})" if len(changes) > limit else ""
    return ", ".join(paths) + suffix


def internal_report(
    evidence: dict[str, object], sha256: str, project_name: str, language: str
) -> str:
    summary = evidence["summary"]
    commits = evidence["commits"]
    tags = evidence["tags"]
    refs = evidence["refs"]
    repository = evidence["repository"]
    assert isinstance(summary, dict)
    assert isinstance(commits, list)
    assert isinstance(tags, list)
    assert isinstance(refs, list)
    assert isinstance(repository, dict)
    category_labels = CATEGORY_KO if language == "ko" else CATEGORY_EN
    display_tags = sorted(
        (tag for tag in tags if isinstance(tag, dict)),
        key=lambda tag: (str(tag.get("created_at", "")), str(tag.get("name", ""))),
    )
    markers = evidence_markers(sha256, summary)
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for commit in reversed(commits):
        assert isinstance(commit, dict)
        grouped[str(commit["activity_date"])].append(commit)

    if language == "ko":
        lines = [
            *markers,
            f"# {project_name} 상세 Work Log",
            "",
            "- 문서 유형: 내부 근거용 Git 상세 로그",
            f"- 근거 파일 SHA-256: `{sha256}`",
            f"- 저장소: `{clean_cell(repository['root'])}`",
            f"- 분석 범위: {scope_text(evidence, language)}",
            f"- 기록 기간: {summary['period_start']} ~ {summary['period_end']}",
            "",
            "## 1. 근거 상태",
            "",
            *completeness_lines(evidence, language),
            f"- 수집 커밋: **{format_number(summary['commit_count'])}건**",
            f"- 근거 생성 시각: `{evidence['generated_at']}`",
            "",
            "작업 트리 변경은 기록된 커밋 범위에 포함하지 않는다. Shallow 또는 수집 제한이 "
            "표시된 경우 이 문서를 완전한 수행이력으로 취급하지 않는다.",
            "",
            "## 2. 집계",
            "",
            "| 항목 | 값 | 해석 |",
            "|---|---:|---|",
            f"| 커밋 | {format_number(summary['commit_count'])} | 선택 범위에서 도달 가능한 고유 커밋 |",
            f"| 병합 커밋 | {format_number(summary['merge_commit_count'])} | 부모가 2개 이상인 커밋 |",
            f"| 활동일 | {format_number(summary['activity_day_count'])} | 보고 시간대의 커미터 날짜 |",
            f"| 태그 | {format_number(summary['tag_count'])} | 선택 범위의 태그 인벤토리 |",
            f"| 삽입 churn | {format_number(summary['insertions'])} | 커밋별 numstat 합계 |",
            f"| 삭제 churn | {format_number(summary['deletions'])} | 커밋별 numstat 합계 |",
            f"| 고유 변경 경로 | {format_number(summary['unique_path_count'])} | 관찰된 경로의 합집합 |",
            "",
            "삽입·삭제 값은 병합과 되돌리기로 중복될 수 있으며 순증가량이 아니다.",
            "",
            "## 3. 날짜별 상세 이력",
            "",
        ]
    else:
        lines = [
            *markers,
            f"# {project_name} Detailed Work Log",
            "",
            "- Document type: Internal Git evidence log",
            f"- Evidence SHA-256: `{sha256}`",
            f"- Repository: `{clean_cell(repository['root'])}`",
            f"- Scope: {scope_text(evidence, language)}",
            f"- Recorded period: {summary['period_start']} to {summary['period_end']}",
            "",
            "## 1. Evidence state",
            "",
            *completeness_lines(evidence, language),
            f"- Collected commits: **{format_number(summary['commit_count'])}**",
            f"- Generated at: `{evidence['generated_at']}`",
            "",
            "Working-tree changes are outside the commit scope. Do not treat this as "
            "complete history when shallow or truncated evidence is reported.",
            "",
            "## 2. Metrics",
            "",
            "| Metric | Value | Definition |",
            "|---|---:|---|",
            f"| Commits | {format_number(summary['commit_count'])} | Unique reachable commits in scope |",
            f"| Merge commits | {format_number(summary['merge_commit_count'])} | Commits with two or more parents |",
            f"| Activity days | {format_number(summary['activity_day_count'])} | Committer dates in reporting timezone |",
            f"| Tags | {format_number(summary['tag_count'])} | Tags in scope |",
            f"| Insertion churn | {format_number(summary['insertions'])} | Sum of per-commit numstat |",
            f"| Deletion churn | {format_number(summary['deletions'])} | Sum of per-commit numstat |",
            f"| Unique changed paths | {format_number(summary['unique_path_count'])} | Union of observed paths |",
            "",
            "Insertion and deletion figures may overlap through merges and reversions; "
            "they are not net growth.",
            "",
            "## 3. Chronological history",
            "",
        ]

    for date in sorted(grouped):
        date_commits = grouped[date]
        lines.append(f"### {date} · {len(date_commits)}")
        lines.append("")
        for commit in date_commits:
            stats = commit["stats"]
            author = commit["author"]
            assert isinstance(stats, dict)
            assert isinstance(author, dict)
            category = category_labels.get(str(commit["category"]), str(commit["category"]))
            lines.extend(
                [
                    f"<!-- commit:{commit['hash']} -->",
                    f"- `{commit['short_hash']}` · **{category}** · "
                    f"{clean_cell(commit['subject'])}",
                    f"  - {'작성자' if language == 'ko' else 'Author'}: "
                    f"{clean_cell(author['name'])}",
                    f"  - {'변경' if language == 'ko' else 'Change'}: "
                    f"{format_number(stats['file_count'])} "
                    f"{'개 파일' if language == 'ko' else 'files'}, "
                    f"+{format_number(stats['insertions'])} / "
                    f"-{format_number(stats['deletions'])}"
                    + (
                        f", {'바이너리' if language == 'ko' else 'binary'} "
                        f"{format_number(stats['binary_file_count'])}"
                        if int(stats["binary_file_count"])
                        else ""
                    ),
                    f"  - {'경로' if language == 'ko' else 'Paths'}: "
                    f"{representative_paths(commit)}",
                    "",
                ]
            )

    if language == "ko":
        lines.extend(["## 4. 태그 및 Ref 스냅샷", ""])
    else:
        lines.extend(["## 4. Tag and ref snapshot", ""])
    if display_tags:
        lines.extend(
            [
                "| Tag | Commit | Created |",
                "|---|---|---|",
                *[
                    f"| {clean_cell(tag['name'])} | `{str(tag['commit'])[:12]}` | "
                    f"{clean_cell(tag['created_at'] or '-')} |"
                    for tag in display_tags
                ],
                "",
            ]
        )
    else:
        lines.extend(
            ["- 분석 범위에서 태그 없음." if language == "ko" else "- No tags in scope.", ""]
        )
    lines.append(f"- {'Ref 수' if language == 'ko' else 'Ref count'}: {len(refs)}")
    lines.append("")
    lines.extend(
        [
            "## 5. 해석 및 검증 규칙"
            if language == "ko"
            else "## 5. Interpretation and verification rules",
            "",
        ]
    )
    if language == "ko":
        lines.extend(
            [
                "- 커밋 수는 투입 시간, 난이도, 품질 또는 개인 생산성을 의미하지 않는다.",
                "- merge, squash, rebase, cherry-pick은 기록 형태와 통계를 바꿀 수 있다.",
                "- 이 문서의 모든 커밋 표식은 원본 근거 파일과 일대일로 검증해야 한다.",
                "- 제품 성과와 완료 상태는 테스트, 릴리스, 운영 및 사용자 근거로 별도 확인한다.",
            ]
        )
    else:
        lines.extend(
            [
                "- Commit counts do not represent hours, difficulty, quality, or productivity.",
                "- Merges, squashes, rebases, and cherry-picks can reshape records and metrics.",
                "- Every commit marker must verify one-to-one against the evidence file.",
                "- Confirm product outcomes with tests, releases, operations, and user evidence.",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        evidence_path = Path(args.evidence).expanduser().resolve()
        evidence, sha256 = load_evidence(evidence_path)
        repository = evidence["repository"]
        assert isinstance(repository, dict)
        project_name = clean_cell(args.project_name or repository["name"])
        output_dir = Path(args.output_dir).expanduser().resolve()
        external = external_report(evidence, sha256, project_name, args.language)
        internal = internal_report(evidence, sha256, project_name, args.language)
        if PLACEHOLDER_PATTERN.search(external) or PLACEHOLDER_PATTERN.search(internal):
            raise RenderError("renderer produced an unresolved placeholder")
        external_path = output_dir / args.external_name
        internal_path = output_dir / args.internal_name
        atomic_write(external_path, external)
        atomic_write(internal_path, internal)
    except (AssertionError, KeyError, OSError, RenderError, TypeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        "PASS",
        f"evidence_sha256={sha256}",
        f"external={external_path}",
        f"internal={internal_path}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
