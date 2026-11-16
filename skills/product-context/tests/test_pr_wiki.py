"""Public CLI contracts. Synthetic wiki metadata is verifier input, not a model mock."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / 'scripts/pr_wiki.py'


class PrWikiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve()
        self.repo = self.home / 'product'
        self.repo.mkdir()
        (self.repo / 'README.md').write_text('# Product\n')
        (self.repo / 'spec.md').write_text('Accepted policy: retention is 14 days.\n')
        (self.repo / '.product-context.json').write_text(json.dumps({'schema_version': 1, 'product': 'fixture', 'sources': ['README.md', 'spec.md'], 'exclude': [], 'topics': []}))
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=f@example.invalid', 'commit', '-qm', 'Initial product')
        self.event = self.home / 'event.json'
        self.state = self.home / 'state.json'
        self.payload = {'action': 'synchronize', 'repository': {'full_name': 'owner/product'}, 'sender': {'type': 'User'}, 'pull_request': {'number': 7, 'draft': False, 'author_association': 'OWNER', 'head': {'sha': self.git('rev-parse', 'HEAD').strip(), 'ref': 'feature', 'repo': {'full_name': 'owner/product'}}}}
        self.event.write_text(json.dumps(self.payload))

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True, stderr=subprocess.PIPE)

    def run_cli(self, command, *args, code=0):
        result = subprocess.run(['python3', '-B', str(SCRIPT), command, '--repo', str(self.repo), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def prepare(self, code=0):
        self.event.write_text(json.dumps(self.payload))
        return self.run_cli('prepare', '--event', str(self.event), '--state', str(self.state), code=code)

    def seal(self):
        wiki = self.repo / 'openwiki'
        wiki.mkdir(exist_ok=True)
        (wiki / 'quickstart.md').write_text('# Product\nRetention is 14 days.\n')
        (wiki / '.last-update.json').write_text('{"status":"complete"}')
        (self.repo / '.product-context').mkdir(exist_ok=True)
        js = "const {context,saveReceipt}=await import(process.argv[1]); const report=await context(process.argv[2]);await saveReceipt(process.argv[2],report);console.log(report.snapshot);"
        snapshot = subprocess.check_output(['node', '--input-type=module', '-e', js, (SKILL / 'runtime/guard.mjs').as_uri(), str(self.repo)], text=True).strip()
        subprocess.check_call(['python3', '-B', str(SKILL / 'scripts/product_context.py'), 'record', '--repo', str(self.repo), '--snapshot', snapshot, '--actor', 'fixture', '--note', 'Synthetic verifier input'], stdout=subprocess.DEVNULL)

    def test_plan_is_read_only_and_install_emits_oauth_pr_events_with_pinned_actions(self):
        args = ['--runtime-ref', '1' * 40]
        report = self.run_cli('install', *args)
        file = self.repo / report['workflow']
        self.assertFalse(file.exists())
        self.run_cli('install', *args, '--write')
        workflow = json.loads(file.read_text())  # JSON is a YAML-compatible workflow representation.
        self.assertEqual(workflow['on']['pull_request']['types'], ['opened', 'synchronize', 'reopened', 'ready_for_review'])
        self.assertNotIn('schedule', workflow['on'])
        job = workflow['jobs']['wiki']
        self.assertIn('head.repo.full_name == github.repository', job['if'])
        writer = next(s for s in job['steps'] if s.get('id') == 'writer')
        self.assertEqual(writer['with']['claude_code_oauth_token'], '${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}')
        self.assertNotIn('anthropic_api_key', writer['with'])
        self.assertIn('--max-turns 16', writer['with']['claude_args'])
        self.assertIn('--permission-mode default', writer['with']['claude_args'])
        for step in job['steps']:
            if 'uses' in step:
                self.assertRegex(step['uses'], r'@[a-f0-9]{40}$')

    def test_official_action_has_a_git_workspace_and_explicit_bot_support(self):
        report = self.run_cli('install', '--runtime-ref', '1' * 40, '--write')
        workflow = json.loads((self.repo / report['workflow']).read_text())
        job = workflow['jobs']['wiki']
        checkout = next(step for step in job['steps'] if step.get('uses', '').startswith('actions/checkout@'))
        self.assertEqual(checkout['with'].get('path', '.'), '.')
        writer = next(step for step in job['steps'] if step.get('id') == 'writer')
        self.assertIn('chatgpt-codex-connector[bot]', writer['with'].get('allowed_bots', '').split(','))

    def test_action_config_restoration_does_not_change_the_generation_evidence(self):
        (self.repo / 'CLAUDE.md').write_text('Approved PR policy\n')
        config = json.loads((self.repo / '.product-context.json').read_text())
        config['sources'].append('CLAUDE.md')
        (self.repo / '.product-context.json').write_text(json.dumps(config))
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=f@example.invalid', 'commit', '-qm', 'PR policy change')
        head = self.git('rev-parse', 'HEAD').strip()
        original = self.repo
        evidence = self.home / 'evidence-worktree'
        self.run_cli('checkout', '--destination', str(evidence), '--head', head)
        self.assertEqual(self.git('rev-parse', '--show-toplevel').strip(), str(original))
        # External Action restores its own workspace's protected configuration.
        (original / 'CLAUDE.md').write_text('Base-branch policy restored by Action\n')
        self.repo = evidence
        self.payload['pull_request']['head']['sha'] = head
        self.prepare()
        self.seal()
        self.assertTrue(self.run_cli('verify', '--state', str(self.state))['verified'])
        self.assertEqual((evidence / 'CLAUDE.md').read_text(), 'Approved PR policy\n')

    def test_known_codex_bot_prs_are_eligible_but_unknown_bots_are_not(self):
        self.payload['pull_request']['author_association'] = 'NONE'
        self.payload['pull_request']['user'] = {'login': 'chatgpt-codex-connector[bot]'}
        self.payload['sender'] = {'type': 'Bot', 'login': 'chatgpt-codex-connector[bot]'}
        self.assertTrue(self.prepare()['should_run'])
        self.payload['sender']['login'] = 'unknown-app[bot]'
        self.assertIn('UNTRUSTED_PR', self.prepare(code=2)['error'])

    def test_ignored_required_receipts_fail_before_any_model_execution(self):
        (self.repo / '.gitignore').write_text('.product-context/\n')
        self.assertIn('IGNORED_OUTPUT', self.prepare(code=2)['error'])
        self.assertFalse(self.state.exists())

    def test_ignored_generated_outputs_cannot_receive_a_publication_success(self):
        self.prepare()
        exclude = self.repo / '.git/info/exclude'
        exclude.write_text(exclude.read_text() + '\n.product-context/\n')
        self.seal()
        self.assertIn('IGNORED_OUTPUT', self.run_cli('verify', '--state', str(self.state), '--commit', code=2)['error'])

    def test_verified_publication_keeps_receipts_and_current_status_in_a_fresh_clone(self):
        self.prepare()
        self.seal()
        result = self.run_cli('verify', '--state', str(self.state), '--commit')
        self.assertTrue(result['verified'])
        clone = self.home / 'published-clone'
        subprocess.check_call(['git', 'clone', '-q', str(self.repo), str(clone)])
        self.repo = clone
        self.payload['pull_request']['head']['sha'] = self.git('rev-parse', 'HEAD').strip()
        for name in ['.product-context/review.json', '.product-context/wiki-review.json', 'openwiki/.last-update.json', 'openwiki/quickstart.md']:
            self.assertTrue((clone / name).is_file(), name)
        self.assertFalse(self.prepare()['should_run'])

    def test_install_preserves_an_unowned_workflow(self):
        file = self.repo / '.github/workflows/product-context-wiki.yml'
        file.parent.mkdir(parents=True)
        file.write_text('name: Custom\n')
        self.assertIn('WORKFLOW_EXISTS', self.run_cli('install', '--runtime-ref', '1' * 40, '--write', code=2)['error'])
        self.assertEqual(file.read_text(), 'name: Custom\n')

    def test_source_drift_runs_but_a_current_wiki_skips_generation(self):
        self.assertTrue(self.prepare()['should_run'])
        self.seal()
        self.assertFalse(self.prepare()['should_run'])
        (self.repo / 'spec.md').write_text('Accepted policy: retention is 30 days.\n')
        self.assertTrue(self.prepare()['should_run'])

    def test_forks_and_unknown_authors_are_refused_before_any_run_state(self):
        self.payload['pull_request']['head']['repo']['full_name'] = 'external/product'
        self.assertIn('UNTRUSTED_PR', self.prepare(code=2)['error'])
        self.assertFalse(self.state.exists())
        self.payload['pull_request']['head']['repo']['full_name'] = 'owner/product'
        self.payload['pull_request']['author_association'] = 'NONE'
        self.assertIn('UNTRUSTED_PR', self.prepare(code=2)['error'])

    def test_drafts_skip_and_a_wrong_checked_out_head_is_refused(self):
        self.payload['pull_request']['draft'] = True
        self.assertFalse(self.prepare()['should_run'])
        self.payload['pull_request']['draft'] = False
        self.payload['pull_request']['head']['sha'] = '0' * 40
        self.assertIn('HEAD_CHANGED', self.prepare(code=2)['error'])

    def test_verification_requires_clean_completion_and_only_document_outputs(self):
        self.prepare()
        self.assertIn('WIKI_NOT_CURRENT', self.run_cli('verify', '--state', str(self.state), code=2)['error'])
        self.seal()
        report = self.run_cli('verify', '--state', str(self.state))
        self.assertIn('openwiki/quickstart.md', report['publish_paths'])
        (self.repo / 'new_code.py').write_text('print("unexpected")\n')
        self.assertIn('OUT_OF_SCOPE', self.run_cli('verify', '--state', str(self.state), code=2)['error'])

    def test_even_a_fresh_review_cannot_hide_a_primary_source_edit_during_generation(self):
        self.prepare()
        (self.repo / 'spec.md').write_text('The agent silently changed policy.\n')
        self.seal()
        self.assertIn('SOURCE_CHANGED', self.run_cli('verify', '--state', str(self.state), code=2)['error'])

    def test_workflow_install_refuses_symlinked_parent_paths(self):
        outside = self.home / 'outside'
        outside.mkdir()
        (self.repo / '.github').symlink_to(outside, target_is_directory=True)
        self.assertIn('UNSAFE_DESTINATION', self.run_cli('install', '--runtime-ref', '1' * 40, '--write', code=2)['error'])
        self.assertEqual(list(outside.iterdir()), [])

    def test_a_decision_change_triggers_generation_without_editing_source_files(self):
        self.seal()
        self.assertFalse(self.prepare()['should_run'])
        file = self.home / 'decision.json'
        file.write_text(json.dumps({'id': 'D-001', 'title': 'Retain policy', 'status': 'accepted', 'reason': 'User-confirmed fixture requirement', 'actor': 'fixture', 'evidence': ['spec.md']}))
        subprocess.check_call(['python3', '-B', str(SKILL / 'scripts/product_context.py'), 'decision', '--repo', str(self.repo), '--file', str(file)], stdout=subprocess.DEVNULL)
        self.assertTrue(self.prepare()['should_run'])

    def test_a_changed_local_head_or_nonmanaged_agent_instruction_is_not_publishable(self):
        self.prepare()
        self.seal()
        (self.repo / 'AGENTS.md').write_text('New arbitrary policy\n')
        self.assertIn('SOURCE_CHANGED', self.run_cli('verify', '--state', str(self.state), code=2)['error'])
        (self.repo / 'AGENTS.md').unlink()
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=f@example.invalid', 'commit', '--allow-empty', '-qm', 'New head')
        self.assertIn('HEAD_CHANGED', self.run_cli('verify', '--state', str(self.state), code=2)['error'])


if __name__ == '__main__':
    unittest.main()
