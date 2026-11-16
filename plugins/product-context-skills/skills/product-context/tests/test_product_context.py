"""Public CLI contracts; real files and persistence, no internal module mocks."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().parents[1] / "scripts" / "product_context.py"


class ProductContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "product"
        self.root.mkdir()
        (self.root / "README.md").write_text("# Product\n\n[Design](docs/design.md)\n")
        (self.root / "docs").mkdir()
        (self.root / "docs/design.md").write_text("# Design\n\nInitial decision.\n")

    def run_cli(self, command, *args, repo=None, expected=0, env=None):
        result = subprocess.run(
            [sys.executable, "-B", str(CLI), command, "--repo", str(repo or self.root), *args],
            capture_output=True, text=True, env=env,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def init(self):
        self.run_cli("init", "--product", "clinic")

    def check(self, **kwargs):
        return json.loads(self.run_cli("check", "--json", **kwargs).stdout)

    def record(self, snapshot, *args, expected=0):
        return self.run_cli("record", "--snapshot", snapshot, "--actor", "agent:test",
                            "--note", "Reviewed source changes.", *args, expected=expected)

    def decision(self, record, expected=0):
        path = Path(self.temp.name) / "decision-input.json"
        path.write_text(json.dumps(record))
        return self.run_cli("decision", "--file", str(path), expected=expected)

    def test_check_and_prepare_are_read_only_and_do_not_start_providers(self):
        self.init()
        trap = Path(self.temp.name) / "bin"
        trap.mkdir()
        marker = Path(self.temp.name) / "provider-started"
        for name in ["openwiki", "codex", "claude", "curl"]:
            executable = trap / name
            executable.write_text("#!/bin/sh\n: > '" + str(marker) + "'\nexit 99\n")
            executable.chmod(0o755)
        env = dict(os.environ, PATH=str(trap) + os.pathsep + os.environ.get("PATH", ""))
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = self.check(env=env)
        self.assertEqual(result["review"]["status"], "unreviewed")
        self.assertEqual(result["model_calls"], 0)
        packet = self.run_cli("prepare", env=env).stdout
        self.assertIn("docs/design.md", packet)
        self.assertFalse(marker.exists())
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_init_never_overwrites_an_existing_configuration(self):
        self.init()
        config = self.root / ".product-context.json"
        before = config.read_bytes()
        self.run_cli("init", "--product", "other", expected=2)
        self.assertEqual(config.read_bytes(), before)

    def test_review_detects_modified_added_and_deleted_sources(self):
        self.init()
        initial = self.check()
        self.record(initial["snapshot"])
        self.assertEqual(self.check()["review"]["status"], "current")
        (self.root / "docs/design.md").write_text("# Revised design\n")
        (self.root / "docs/new.md").write_text("# New observations\n")
        result = self.check()
        self.assertEqual(result["review"]["status"], "stale")
        self.assertEqual({c["path"]: c["kind"] for c in result["changes"]},
                         {"docs/design.md": "modified", "docs/new.md": "added"})
        self.record(result["snapshot"])
        (self.root / "docs/new.md").unlink()
        self.assertEqual(self.check()["changes"], [{"path": "docs/new.md", "kind": "deleted"}])

    def test_a_changed_snapshot_cannot_be_recorded_as_reviewed(self):
        self.init()
        inspected = self.check()["snapshot"]
        (self.root / "docs/design.md").write_text("Changed after inspection.\n")
        result = self.record(inspected, expected=2)
        self.assertIn("SNAPSHOT_CHANGED", result.stderr)
        self.assertFalse((self.root / ".product-context/review.json").exists())

    def test_questions_survive_a_later_review_and_need_explicit_resolution(self):
        self.init()
        self.record(self.check()["snapshot"], "--question", "Production ownership unresolved.")
        (self.root / "docs/design.md").write_text("Updated implementation.\n")
        self.record(self.check()["snapshot"])
        self.assertEqual(self.check()["review"]["questions"], ["Production ownership unresolved."])
        self.record(self.check()["snapshot"], "--resolve-question", "Production ownership unresolved.")
        self.assertEqual(self.check()["review"]["questions"], [])

    def test_proposal_and_reconsideration_preserve_the_accepted_decision(self):
        self.init()
        base = {"id": "D1", "title": "Central ownership", "status": "accepted",
                "reason": "Initial shared operations.", "actor": "human:owner",
                "evidence": ["docs/design.md"]}
        self.decision(base)
        self.decision({**base, "id": "D2", "status": "proposed", "title": "Delegated ownership",
                       "reason": "Consider independent releases.", "supersedes": ["D1"]})
        self.decision({**base, "id": "D3", "status": "reconsideration",
                       "reason": "New staging evidence.", "reconsiders": ["D1"]})
        decisions = {d["id"]: d for d in self.check()["decisions"]}
        self.assertEqual(decisions["D1"]["effective_status"], "under-review")
        self.assertEqual(decisions["D2"]["effective_status"], "proposed")
        self.assertEqual(decisions["D1"]["reason"], "Initial shared operations.")
        self.decision({**base, "id": "D4", "title": "Delegated ownership", "status": "accepted",
                       "reason": "Staging verifies the new boundary.", "supersedes": ["D1", "D2"],
                       "scope": "staging; production pending"})
        decisions = {d["id"]: d for d in self.check()["decisions"]}
        self.assertEqual(decisions["D1"]["effective_status"], "superseded")
        self.assertEqual(decisions["D4"]["scope"], "staging; production pending")
        self.assertEqual(decisions["D1"]["reason"], "Initial shared operations.")

    def test_duplicate_or_unknown_decision_references_do_not_change_history(self):
        self.init()
        record = {"id": "D1", "title": "Choice", "status": "accepted", "reason": "Evidence",
                  "actor": "agent:test", "evidence": ["docs/design.md"]}
        self.decision(record)
        before = (self.root / ".product-context/decisions.json").read_bytes()
        self.decision(record, expected=2)
        self.decision({**record, "id": "D2", "supersedes": ["missing"]}, expected=2)
        self.assertEqual((self.root / ".product-context/decisions.json").read_bytes(), before)

    def test_missing_links_fail_but_code_examples_and_external_refs_do_not(self):
        self.init()
        (self.root / "README.md").write_text(
            '# Product\n[Missing](docs/missing.md)\n```md\n[Example](not-a-file.md)\n```\n'
            '[Sibling](../other/README.md)\n[Web](https://example.invalid/no-fetch)\n')
        result = self.check(expected=1)
        self.assertEqual([(x["source"], x["target"]) for x in result["broken_links"]],
                         [("README.md", "docs/missing.md")])
        self.assertEqual(len(result["external_references"]), 1)

    def test_source_symlinks_and_traversal_cannot_read_outside_the_product(self):
        self.init()
        secret = Path(self.temp.name) / "outside.md"
        secret.write_text("NEVER_INCLUDE_THIS_SECRET")
        (self.root / "docs/escape.md").symlink_to(secret)
        result = self.run_cli("check", "--json", expected=2)
        self.assertIn("UNSAFE_PATH", result.stderr)
        self.assertNotIn("NEVER_INCLUDE_THIS_SECRET", result.stdout + result.stderr)
        (self.root / "docs/escape.md").unlink()
        config = self.root / ".product-context.json"
        data = json.loads(config.read_text())
        data["sources"] = ["../outside.md"]
        config.write_text(json.dumps(data))
        self.assertIn("UNSAFE_PATH", self.run_cli("check", "--json", expected=2).stderr)

    def test_state_symlink_and_writer_lock_do_not_overwrite_other_files(self):
        self.init()
        snapshot = self.check()["snapshot"]
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / ".product-context").symlink_to(outside, target_is_directory=True)
        self.record(snapshot, expected=2)
        self.assertEqual(list(outside.iterdir()), [])
        (self.root / ".product-context").unlink()
        state = self.root / ".product-context"
        state.mkdir()
        (state / ".lock").write_text("another writer")
        self.assertIn("LOCKED", self.record(snapshot, expected=2).stderr)
        self.assertEqual((state / ".lock").read_text(), "another writer")

    def test_snapshot_is_portable_and_scope_changes_invalidate_review(self):
        self.init()
        self.record(self.check()["snapshot"])
        import shutil
        clone = Path(self.temp.name) / "second-checkout"
        shutil.copytree(self.root, clone)
        self.assertEqual(self.check(repo=clone)["review"]["status"], "current")
        config = clone / ".product-context.json"
        data = json.loads(config.read_text())
        data["exclude"] = ["docs/new-topic/**"]
        config.write_text(json.dumps(data))
        self.assertEqual(self.check(repo=clone)["review"]["status"], "stale")

    def test_strict_freshness_is_opt_in_and_bad_state_is_not_silently_reset(self):
        self.init()
        self.check()
        self.run_cli("check", "--require-reviewed", "--json", expected=1)
        state = self.root / ".product-context"
        state.mkdir()
        (state / "review.json").write_text("not json")
        self.assertIn("INVALID_STATE", self.run_cli("check", "--json", expected=2).stderr)

    def test_oversized_sources_and_unknown_config_fields_are_rejected(self):
        self.init()
        config = self.root / ".product-context.json"
        data = json.loads(config.read_text())
        data["max_file_bytes"] = 16
        config.write_text(json.dumps(data))
        self.assertIn("SOURCE_TOO_LARGE", self.run_cli("check", "--json", expected=2).stderr)
        data["provider"] = "paid-api"
        config.write_text(json.dumps(data))
        self.assertIn("INVALID_CONFIG", self.run_cli("check", "--json", expected=2).stderr)

    def test_recursive_exclusions_cover_nested_archives(self):
        self.init()
        archive = self.root / "docs/archive/nested"
        archive.mkdir(parents=True)
        (archive / "private.md").write_text("excluded " * 1000)
        config = self.root / ".product-context.json"
        data = json.loads(config.read_text())
        data["exclude"] = ["docs/archive/**"]
        data["max_file_bytes"] = 100
        config.write_text(json.dumps(data))
        self.assertEqual(set(self.check()["files"]), {"README.md", "docs/design.md"})

    def test_an_empty_selected_scope_cannot_be_recorded_as_a_success(self):
        self.init()
        config = self.root / ".product-context.json"
        data = json.loads(config.read_text())
        data["sources"] = ["absent/**/*.md"]
        config.write_text(json.dumps(data))
        self.assertIn("EMPTY_SCOPE", self.run_cli("check", "--json", expected=2).stderr)

    def test_malformed_decision_and_topic_types_return_structured_errors(self):
        self.init()
        record = {"id": "D1", "title": "Choice", "status": {}, "reason": "Evidence",
                  "actor": "agent:test", "evidence": ["docs/design.md"]}
        result = self.decision(record, expected=2)
        self.assertEqual(json.loads(result.stderr)["error"], "INVALID_DECISION")
        config = self.root / ".product-context.json"
        data = json.loads(config.read_text())
        data["topics"] = [{"id": [], "question": "Which boundary?", "sources": ["README.md"]}]
        config.write_text(json.dumps(data))
        result = self.run_cli("check", "--json", expected=2)
        self.assertEqual(json.loads(result.stderr)["error"], "INVALID_CONFIG")

    def test_prepared_packet_preserves_scope_relationships_and_evidence_drift(self):
        self.init()
        base = {"id": "D1", "title": "Central ownership", "status": "accepted",
                "reason": "Initial boundary.", "actor": "human:owner", "evidence": ["docs/design.md"]}
        self.decision(base)
        self.decision({**base, "id": "R1", "status": "reconsideration", "reconsiders": ["D1"]})
        self.decision({**base, "id": "D2", "title": "Delegated ownership", "supersedes": ["D1"],
                       "scope": "staging only; production pending", "reason": "Staging handoff checked."})
        (self.root / "docs/design.md").write_text("New evidence after the recorded decision.\n")
        packet = self.run_cli("prepare").stdout
        for required in ["staging only; production pending", "Supersedes: D1", "Reconsiders: D1",
                         "Evidence changed: yes", "human:owner", "docs/design.md"]:
            self.assertIn(required, packet)

    def test_malformed_external_url_does_not_crash_an_offline_check(self):
        self.init()
        (self.root / "README.md").write_text("# Product\n[Malformed URL](https://[broken)\n")
        report = self.check()
        self.assertEqual(report["broken_links"], [])
        self.assertEqual(report["model_calls"], 0)
        self.run_cli("prepare")


if __name__ == "__main__":
    unittest.main()
