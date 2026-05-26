"""Unit tests for scripts/update_pr_checklist.py.

Run from anywhere with pytest:

    pytest plugins/developer-workflow-skills/skills/pr-checklist-verifier/tests

The helper is pure stdlib, so no dependencies beyond pytest itself.
"""
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
SCRIPT = SCRIPT_DIR / "update_pr_checklist.py"
sys.path.insert(0, str(SCRIPT_DIR))

import update_pr_checklist as upc  # noqa: E402

QA = upc.QA_HEADING


def _count_qa(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == QA)


# --------------------------------------------------------------------------- #
# tick_items
# --------------------------------------------------------------------------- #

def test_tick_flips_matching_item():
    out, matched = upc.tick_items("- [ ] run the tests\n- [ ] deploy\n", ["run the tests"])
    assert "- [x] run the tests" in out
    assert "- [ ] deploy" in out
    assert matched == {"run the tests": True}


def test_tick_leaves_nonmatching_lines_untouched():
    body = "  - [ ] indented item\n* [ ] star bullet\n- [ ] keep me\n"
    out, _ = upc.tick_items(body, ["star bullet"])
    assert "* [x] star bullet" in out          # star bullet flipped
    assert "  - [ ] indented item" in out       # others byte-for-byte
    assert "- [ ] keep me" in out


def test_tick_ignores_already_checked_items():
    body = "- [x] already done\n- [ ] todo\n"
    out, matched = upc.tick_items(body, ["already done"])
    assert out == body                          # nothing flipped
    assert matched == {"already done": False}   # checked lines don't count as matches


def test_tick_reports_unmatched_check_as_false():
    body = "- [ ] alpha\n"
    out, matched = upc.tick_items(body, ["zeta"])
    assert out == body
    assert matched == {"zeta": False}


def test_tick_ignores_empty_check_string():
    body = "- [ ] something\n"
    out, matched = upc.tick_items(body, [""])
    assert out == body
    assert matched == {"": False}


def test_tick_preserves_trailing_newline_state():
    assert upc.tick_items("- [ ] x\n", ["x"])[0].endswith("\n")
    assert not upc.tick_items("- [ ] x", ["x"])[0].endswith("\n")


def test_tick_preserves_indentation_when_flipping():
    out, _ = upc.tick_items("    - [ ] nested\n", ["nested"])
    assert out == "    - [x] nested\n"


def test_tick_one_check_flips_every_matching_line():
    out, matched = upc.tick_items("- [ ] deploy api\n- [ ] deploy web\n", ["deploy"])
    assert out == "- [x] deploy api\n- [x] deploy web\n"
    assert matched == {"deploy": True}


# --------------------------------------------------------------------------- #
# upsert_qa_section
# --------------------------------------------------------------------------- #

def test_upsert_inserts_after_checklist_block():
    body = (
        "# PR\n\n"
        "## Testing Checklist\n"
        "- [ ] a\n"
        "- [x] b\n\n"
        "## Notes\n"
        "stuff\n"
    )
    out = upc.upsert_qa_section(body, "method: pytest\nverdict: PASS")
    lines = out.splitlines()
    assert _count_qa(out) == 1
    last_task = max(i for i, line in enumerate(lines) if line.startswith("- ["))
    assert last_task < lines.index(QA) < lines.index("## Notes")
    assert "method: pytest" in out


def test_upsert_appends_at_eof_when_no_checklist_heading():
    body = "# PR\n\n## Summary\nonly prose here\n"
    out = upc.upsert_qa_section(body, "verdict: PASS")
    lines = out.splitlines()
    assert _count_qa(out) == 1
    assert lines.index(QA) > lines.index("only prose here")


def test_upsert_replaces_existing_section_without_duplicating():
    body = "## Test plan\n- [ ] a\n"
    once = upc.upsert_qa_section(body, "verdict: first")
    twice = upc.upsert_qa_section(once, "verdict: second")
    assert _count_qa(twice) == 1
    assert "verdict: second" in twice
    assert "verdict: first" not in twice


def test_upsert_is_idempotent_fixed_point():
    body = "## Test plan\n- [ ] a\n\n## Notes\nx\n"
    once = upc.upsert_qa_section(body, "verdict: PASS\nmetric: 3/3")
    twice = upc.upsert_qa_section(once, "verdict: PASS\nmetric: 3/3")
    assert once == twice


def test_upsert_section_bounded_by_thematic_break():
    body = (
        "## Test plan\n- [ ] a\n\n"
        f"{QA}\n\nold content\n\n---\n\n## Footer\n"
    )
    out = upc.upsert_qa_section(body, "new content")
    assert _count_qa(out) == 1
    assert "old content" not in out
    assert "new content" in out
    assert "## Footer" in out
    assert "---" in out


def test_upsert_preserves_trailing_newline_state():
    assert upc.upsert_qa_section("## Test plan\n- [ ] a\n", "x").endswith("\n")
    assert not upc.upsert_qa_section("## Test plan\n- [ ] a", "x").endswith("\n")


# --------------------------------------------------------------------------- #
# CLI (subprocess against the real entrypoint)
# --------------------------------------------------------------------------- #

def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


def test_cli_out_writes_result_and_leaves_source_untouched(tmp_path):
    body = tmp_path / "body.md"
    body.write_text("- [ ] ship it\n")
    out = tmp_path / "out.md"
    r = _run("--body-file", str(body), "--check", "ship it", "--out", str(out))
    assert r.returncode == 0
    assert out.read_text() == "- [x] ship it\n"
    assert body.read_text() == "- [ ] ship it\n"


def test_cli_in_place_overwrites(tmp_path):
    body = tmp_path / "body.md"
    body.write_text("- [ ] ship it\n")
    r = _run("--body-file", str(body), "--check", "ship it", "--in-place")
    assert r.returncode == 0
    assert body.read_text() == "- [x] ship it\n"


def test_cli_writes_to_stdout_by_default(tmp_path):
    body = tmp_path / "body.md"
    body.write_text("- [ ] ship it\n")
    r = _run("--body-file", str(body), "--check", "ship it")
    assert r.returncode == 0
    assert r.stdout == "- [x] ship it\n"


def test_cli_strict_exits_2_on_unmatched_check(tmp_path):
    body = tmp_path / "body.md"
    body.write_text("- [ ] alpha\n")
    r = _run("--body-file", str(body), "--check", "nope", "--strict")
    assert r.returncode == 2
    assert "no unchecked item matched" in r.stderr


def test_cli_unmatched_check_without_strict_is_ok(tmp_path):
    body = tmp_path / "body.md"
    body.write_text("- [ ] alpha\n")
    r = _run("--body-file", str(body), "--check", "nope")
    assert r.returncode == 0
    assert "no unchecked item matched" in r.stderr


def test_cli_missing_body_file_exits_1(tmp_path):
    r = _run("--body-file", str(tmp_path / "absent.md"), "--check", "x")
    assert r.returncode == 1
    assert "cannot read --body-file" in r.stderr


def test_cli_qa_section_file_integration(tmp_path):
    body = tmp_path / "body.md"
    body.write_text("## Test plan\n- [ ] a\n")
    qa = tmp_path / "qa.md"
    qa.write_text("verdict: PASS\n")
    out = tmp_path / "out.md"
    r = _run("--body-file", str(body), "--check", "a",
             "--qa-section-file", str(qa), "--out", str(out))
    assert r.returncode == 0
    text = out.read_text()
    assert "- [x] a" in text
    assert QA in text
    assert "verdict: PASS" in text


def test_cli_full_run_is_idempotent(tmp_path):
    body = tmp_path / "body.md"
    body.write_text("## Test plan\n- [ ] a\n- [ ] b\n\n## Notes\nx\n")
    qa = tmp_path / "qa.md"
    qa.write_text("verdict: PASS\nmetric: 2/2\n")
    args = ("--body-file", str(body), "--check", "a",
            "--qa-section-file", str(qa), "--in-place")
    assert _run(*args).returncode == 0
    first = body.read_text()
    assert _run(*args).returncode == 0
    second = body.read_text()
    assert first == second
    assert first.count(QA) == 1
    assert first.count("- [x] a") == 1
