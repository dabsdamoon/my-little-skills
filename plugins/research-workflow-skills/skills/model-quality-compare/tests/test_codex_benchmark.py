"""Public CLI contracts. Fake only the external Codex process; never call a model."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/codex_benchmark.py"


class BenchmarkCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.out = self.root / "experiment"
        self.suite = self.root / "suite.json"
        self.suite.write_text(json.dumps({"name": "fixture", "cases": [
            {"id": "r1", "category": "reasoning", "prompt": "2-2?", "expected": 0},
            {"id": "k1", "category": "knowledge", "prompt": "Water formula?", "expected": "H2O"}
        ]}))
        self.fake = self.root / "codex"
        self.fake.write_text('''#!/usr/bin/env python3
import json, os, pathlib, sys
if sys.argv[1:] == ["--version"]:
    print("codex-cli fixture"); sys.exit(0)
if sys.argv[1:] == ["login", "status"]:
    auth = pathlib.Path(__file__).with_name("auth.txt")
    print(auth.read_text() if auth.exists() else "Logged in using ChatGPT"); sys.exit(0)
assert "--ignore-user-config" in sys.argv
assert 'forced_login_method="chatgpt"' in sys.argv
assert 'features.shell_tool=false' in sys.argv
assert not os.environ.get("OPENAI_API_KEY")
assert not os.environ.get("ANTHROPIC_API_KEY")
assert not os.environ.get("OPENAI_BASE_URL")
assert not os.environ.get("CODEX_ACCESS_TOKEN")
assert not os.environ.get("CODEX_APP_SERVER_CHATGPT_BASE_URL")
assert not os.environ.get("CODEX_AUTHAPI_BASE_URL")
assert not os.environ.get("CODEX_REFRESH_TOKEN_URL_OVERRIDE")
assert not os.environ.get("CODEX_EXEC_SERVER_URL")
prompt = sys.stdin.read()
assert "expected" not in prompt
assert not list(pathlib.Path.cwd().iterdir())
model = sys.argv[sys.argv.index("--model") + 1]
if model == "good":
    print(json.dumps({"type":"item.completed","item":{"type":"error","message":"Under-development features enabled: omit_skill_descriptions, skip_host_skill_discovery."}}))
if model == "unavailable":
    print(json.dumps({"type":"turn.failed", "error":{"message":"model unavailable"}})); sys.exit(1)
answer = {"r1":0, "k1":"H2O"} if model == "good" else {"r1":False,"k1":"H2O"}
text = json.dumps(answer)
if model == "malformed": text = '{"r1":5,"r1":0,"k1":"H2O"}'
pathlib.Path(sys.argv[sys.argv.index("--output-last-message") + 1]).write_text(text)
print(json.dumps({"type":"item.completed","item":{"type":"agent_message","text":text}}))
print(json.dumps({"type":"turn.completed","usage":{"input_tokens":20,"cached_input_tokens":0,"output_tokens":10}}))
''')
        self.fake.chmod(0o755)

    def cli(self, *args, env=None, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True, env=env)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def plan(self, models=("good", "wrong"), trials=2):
        self.cli("plan", "--out", self.out, "--suite", self.suite,
                 "--models", *models, "--trials", trials)

    def run_report(self, max_calls=4, env=None):
        self.cli("run", "--out", self.out, "--codex", self.fake,
                 "--max-calls", max_calls, env=env)
        self.cli("report", "--out", self.out)
        return json.loads((self.out / "results.json").read_text())

    def test_frozen_plan_order_budget_and_resume(self):
        self.plan()
        plan = json.loads((self.out / "plan.json").read_text())
        self.assertEqual([r["model"] for r in plan["schedule"]], ["good", "wrong", "wrong", "good"])
        self.cli("run", "--out", self.out, "--codex", self.fake, "--max-calls", 3, ok=False)
        result = self.run_report()
        self.assertEqual(result["models"]["good"]["accuracy"], 1.0)
        self.assertEqual(result["models"]["wrong"]["accuracy"], 0.5)
        runs_before = (self.out / "runs.json").read_bytes()
        self.run_report()
        self.assertEqual((self.out / "runs.json").read_bytes(), runs_before)
        self.assertIn("fixture", (self.out / "report.html").read_text())

    def test_changed_prompt_and_overwrite_are_rejected(self):
        self.plan()
        self.cli("plan", "--out", self.out, "--suite", self.suite,
                 "--models", "good", "wrong", ok=False)
        with (self.out / "prompt.txt").open("a") as f:
            f.write("changed")
        self.cli("run", "--out", self.out, "--codex", self.fake,
                 "--max-calls", 4, ok=False)

    def test_unavailable_is_not_zero_quality_and_duplicate_json_is_invalid(self):
        self.plan(("unavailable", "malformed"), trials=1)
        result = self.run_report(2)
        self.assertIsNone(result["models"]["unavailable"]["accuracy"])
        self.assertEqual(result["models"]["unavailable"]["unavailable_trials"], 1)
        self.assertEqual(result["models"]["malformed"]["accuracy"], 0.0)
        self.assertEqual(result["models"]["malformed"]["format_failures"], 1)

    def test_api_login_refused_and_api_environment_removed(self):
        self.plan(trials=1)
        auth = self.root / "auth.txt"
        auth.write_text("Logged in using an API key")
        env = dict(os.environ, OPENAI_API_KEY="fixture", ANTHROPIC_API_KEY="fixture",
                   OPENAI_BASE_URL="https://invalid.example", CODEX_ACCESS_TOKEN="fixture",
                   CODEX_APP_SERVER_CHATGPT_BASE_URL="https://invalid.example",
                   CODEX_AUTHAPI_BASE_URL="https://invalid.example",
                   CODEX_REFRESH_TOKEN_URL_OVERRIDE="https://invalid.example",
                   CODEX_EXEC_SERVER_URL="https://invalid.example")
        self.cli("run", "--out", self.out, "--codex", self.fake,
                 "--max-calls", 2, env=env, ok=False)
        self.assertFalse((self.out / "runs.json").exists())
        auth.unlink()
        result = self.run_report(2, env)
        self.assertTrue(result["complete"])
        self.assertEqual(result["models"]["good"]["accuracy"], 1.0)

    def test_bool_is_not_integer_and_case_failures_are_auditable(self):
        self.plan(trials=1)
        result = self.run_report(2)
        wrong = next(r for r in result["trials"] if r["model"] == "wrong")
        self.assertFalse(wrong["cases"][0]["passed"])
        self.assertEqual(wrong["cases"][0]["expected"], 0)
        self.assertIs(wrong["cases"][0]["actual"], False)
        self.assertEqual(wrong["categories"]["reasoning"], 0.0)

    def test_completed_turn_with_startup_warning_is_not_tool_use(self):
        self.plan(trials=1)
        result = self.run_report(2)
        good = next(r for r in result["trials"] if r["model"] == "good")
        self.assertEqual(good["status"], "completed")
        self.assertEqual(good["accuracy"], 1.0)

    def test_report_can_correct_old_warning_classifier_without_rerunning(self):
        self.plan(trials=1)
        self.run_report(2)
        path = self.out / "runs.json"
        runs = json.loads(path.read_text())
        runs["runs"][0]["status"] = "control_violation"
        runs["runs"][0]["tool_items"] = ["error"]
        path.write_text(json.dumps(runs))
        before = path.read_bytes()
        self.cli("report", "--out", self.out)
        result = json.loads((self.out / "results.json").read_text())
        self.assertEqual(result["models"]["good"]["accuracy"], 1.0)
        self.assertTrue(result["collection_corrections"])
        self.assertEqual(path.read_bytes(), before)

    def test_missing_or_corrupt_evidence_is_na_and_other_trials_still_report(self):
        self.plan(trials=1)
        self.run_report(2)
        paths = [self.out / "run-01.answer.txt", self.out / "run-01.events.jsonl"]
        for path in paths:
            original = path.read_bytes()
            for mode in ("missing", "corrupt"):
                with self.subTest(path=path.name, mode=mode):
                    if mode == "missing":
                        path.unlink()
                    else:
                        path.write_text("corrupt evidence")
                    self.cli("report", "--out", self.out)
                    result = json.loads((self.out / "results.json").read_text())
                    self.assertIsNone(result["models"]["good"]["accuracy"])
                    self.assertEqual(result["trials"][0]["status"], "evidence_error")
                    self.assertEqual(result["models"]["wrong"]["accuracy"], 0.5)
                    self.assertFalse(result["complete"])
                    path.write_bytes(original)

    def test_legacy_events_are_cross_checked_and_parse_errors_do_not_hide_other_trials(self):
        self.plan(trials=1)
        self.run_report(2)
        path = self.out / "runs.json"
        data = json.loads(path.read_text())
        data["runs"][0].pop("events_sha256", None)
        path.write_text(json.dumps(data))
        events = self.out / "run-01.events.jsonl"
        events.write_text('{not json}\n')
        self.cli("report", "--out", self.out)
        result = json.loads((self.out / "results.json").read_text())
        self.assertIsNone(result["models"]["good"]["accuracy"])
        self.assertEqual(result["models"]["wrong"]["accuracy"], 0.5)
        events.write_text(json.dumps({"type":"item.completed", "item":{"type":"agent_message", "text":"different answer"}})+'\n'+json.dumps({"type":"turn.completed"})+'\n')
        self.cli("report", "--out", self.out)
        result = json.loads((self.out / "results.json").read_text())
        self.assertIsNone(result["models"]["good"]["accuracy"])
        self.assertTrue(result["evidence_audit"])

    def test_orphan_artifacts_or_duplicate_manifest_cannot_trigger_more_calls(self):
        self.plan(trials=1)
        self.run_report(2)
        path = self.out / "runs.json"
        before = path.read_bytes()
        path.unlink()
        self.cli("run", "--out", self.out, "--codex", self.fake, "--max-calls", 2, ok=False)
        data = json.loads(before)
        data["runs"] = []
        path.write_text(json.dumps(data))
        self.cli("run", "--out", self.out, "--codex", self.fake, "--max-calls", 2, ok=False)
        data = json.loads(before)
        data["runs"].append(data["runs"][0])
        path.write_text(json.dumps(data))
        self.cli("run", "--out", self.out, "--codex", self.fake, "--max-calls", 2, ok=False)
        self.cli("report", "--out", self.out, ok=False)

    def test_report_heading_uses_requested_model_names(self):
        self.plan(trials=1)
        self.run_report(2)
        page = (self.out / "report.html").read_text()
        self.assertIn("<h1>good / wrong</h1>", page)
        self.assertNotIn("GPT 6.1 Sol / GPT 6.2 Sol", page)


if __name__ == "__main__":
    unittest.main()
