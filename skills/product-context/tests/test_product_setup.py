"""Product onboarding contracts through the real CLI; fake only GitHub transport."""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / 'scripts/product_setup.py'
PIN = 'a' * 40
SECRET = 'sk-ant-oat01-synthetic-subscription-fixture'
GH = '''#!/usr/bin/env python3
import json,os,sys,hashlib
from pathlib import Path
p=Path(os.environ['FIXTURE_GITHUB']); d=json.loads(p.read_text()); a=sys.argv[1:]
if a[:2]==['secret','set']:
    if '--body' in a:sys.exit(90)
    token=sys.stdin.read().strip()
    d['secret_digest']=hashlib.sha256(token.encode()).hexdigest()
    d['secret_writes']=d.get('secret_writes',0)+1
    d['routes']['repos/acme/product/actions/secrets']={'secrets':[{'name':'CLAUDE_CODE_OAUTH_TOKEN'}]}
    p.write_text(json.dumps(d))
    if d.get('secret_exit',0):print(token,file=sys.stderr)
    sys.exit(d.get('secret_exit',0))
if a and a[0]=='api':
    endpoint=a[1].replace('?per_page=100&page=1','')
    value=d['routes'].get(endpoint,{'_http':404})
    if isinstance(value,dict) and '_http' in value:
        print('HTTP '+str(value['_http']),file=sys.stderr);sys.exit(1)
    if isinstance(value,dict) and ('_zip' in value or '_raw' in value):
        import base64
        sys.stdout.buffer.write(base64.b64decode(value.get('_zip',value.get('_raw'))));sys.exit(0)
    print(json.dumps(value));sys.exit(0)
sys.exit(91)
'''


def contents(value):
    raw = json.dumps(value).encode() if not isinstance(value, str) else value.encode()
    return {'type': 'file', 'encoding': 'base64', 'content': base64.b64encode(raw).decode()}


class ProductSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / 'product'
        self.repo.mkdir()
        (self.repo / 'README.md').write_text('# Product\n')
        (self.repo / 'spec.md').write_text('Accepted retention: 14 days.\n')
        self.git('init', '-q')
        self.git('remote', 'add', 'origin', 'https://github.com/acme/product.git')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=f@example.invalid', 'commit', '-qm', 'Initial')
        self.fixture = self.root / 'github.json'
        self.data = {'routes': {
            'repos/acme/product': {'full_name': 'acme/product', 'default_branch': 'develop'},
            'repos/acme/product/actions/secrets': {'secrets': []},
            'repos/acme/product/actions/organization-secrets': {'secrets': []},
            'repos/dabsdamoon/my-little-skills/contents/skills/product-context/runtime/package.json?ref='+PIN: contents({'version': '0.4.3'}),
        }}
        self.save()
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        (bin_dir / 'gh').write_text(GH)
        (bin_dir / 'gh').chmod(0o755)
        for host in ('claude', 'codex'):
            file = bin_dir / host
            file.write_text('#!/bin/sh\nexit 1\n')
            file.chmod(0o755)
        self.env = dict(os.environ, PATH=str(bin_dir)+os.pathsep+os.environ['PATH'], FIXTURE_GITHUB=str(self.fixture))
        self.runtime = self.root / 'missing-runtime'

    def save(self):
        self.fixture.write_text(json.dumps(self.data))

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True, stderr=subprocess.PIPE)

    def call(self, command='doctor', *args, code=1, token=None):
        result = subprocess.run(['python3', '-B', str(SCRIPT), command, '--repo', str(self.repo), '--github-repo', 'acme/product', '--install-root', str(self.runtime), '--host', 'codex', *args], env=self.env, input=token, capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout+result.stderr)
        self.assertNotIn(SECRET, result.stdout+result.stderr)
        self.assertTrue(result.stdout.strip().startswith('{'), result.stderr)
        return json.loads(result.stdout)

    def profile(self):
        profile = {'schema_version': 1, 'product': 'fixture', 'sources': ['README.md', 'spec.md'], 'exclude': [], 'topics': []}
        (self.repo / '.product-context.json').write_text(json.dumps(profile))

    def workflow(self):
        self.profile()
        result = subprocess.run(['python3', '-B', str(SKILL/'scripts/pr_wiki.py'), 'install', '--repo', str(self.repo), '--runtime-ref', PIN, '--write'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        path = self.repo / '.github/workflows/product-context-wiki.yml'
        return json.loads(path.read_text())

    def publish_configuration(self, workflow):
        for path in ('.product-context.json', '.github/workflows/product-context-wiki.yml'):
            self.data['routes']['repos/acme/product/contents/'+path+'?ref=develop'] = contents(json.loads((self.repo/path).read_text()))
        self.data['routes']['repos/acme/product/actions/secrets'] = {'secrets': [{'name': 'CLAUDE_CODE_OAUTH_TOKEN'}]}
        self.save()

    def test_local_only_cannot_be_reported_as_product_automation_complete(self):
        report = self.call()
        self.assertEqual(report['local']['status'], 'incomplete')
        self.assertEqual(report['automation']['checks']['profile']['code'], 'PROFILE_MISSING')
        self.assertEqual(report['automation']['checks']['workflow']['code'], 'WORKFLOW_MISSING')
        self.assertEqual(report['automation']['checks']['oauth']['code'], 'OAUTH_MISSING')
        self.assertEqual(report['verification']['status'], 'unverified')
        self.assertFalse(report['complete'])
        self.assertEqual(report['model_calls'], 0)
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_permission_denial_is_unknown_not_a_missing_secret(self):
        for suffix in ('secrets', 'organization-secrets'):
            self.data['routes']['repos/acme/product/actions/'+suffix] = {'_http': 403}
        self.save()
        report = self.call()
        self.assertEqual(report['automation']['checks']['oauth']['status'], 'unknown')
        self.assertEqual(report['automation']['checks']['oauth']['code'], 'OAUTH_UNVERIFIABLE')

    def test_personal_repository_has_no_organization_secret_scope(self):
        self.data['routes']['repos/acme/product']['owner'] = {'type':'User'}
        self.data['routes']['repos/acme/product/actions/organization-secrets'] = {'_http':404}
        self.save()
        self.assertEqual(self.call()['automation']['checks']['oauth']['code'], 'OAUTH_MISSING')

    def test_repository_or_provided_organization_secret_satisfies_configuration(self):
        for scope in ('secrets', 'organization-secrets'):
            with self.subTest(scope=scope):
                self.data['routes']['repos/acme/product/actions/secrets'] = {'secrets': []}
                self.data['routes']['repos/acme/product/actions/organization-secrets'] = {'secrets': []}
                self.data['routes']['repos/acme/product/actions/'+scope] = {'secrets': [{'name': 'CLAUDE_CODE_OAUTH_TOKEN'}]}
                self.save()
                self.assertEqual(self.call()['automation']['checks']['oauth']['status'], 'configured')

    def test_written_configuration_is_not_published_configuration_or_auth_validation(self):
        self.workflow()
        report = self.call()
        self.assertEqual(report['automation']['checks']['published']['code'], 'CONFIG_NOT_PUBLISHED')
        self.assertFalse(report['complete'])

    def test_ready_configuration_is_separate_from_live_pr_verification(self):
        self.publish_configuration(self.workflow())
        report = self.call()
        self.assertEqual(report['automation']['status'], 'ready')
        self.assertEqual(report['automation']['checks']['oauth']['authentication'], 'unverified')
        self.assertEqual(report['verification']['status'], 'unverified')
        self.assertFalse(report['complete'])

    def test_unknown_or_unsupported_workflow_is_preserved(self):
        self.profile()
        path = self.repo / '.github/workflows/product-context-wiki.yml'
        path.parent.mkdir(parents=True)
        path.write_text('name: custom workflow\n')
        before = path.read_bytes()
        report = self.call('setup', '--runtime-ref', PIN, '--write', '--skip-local')
        self.assertEqual(report['automation']['checks']['workflow']['code'], 'WORKFLOW_UNREVIEWED')
        self.assertEqual(path.read_bytes(), before)

    def test_setup_plan_is_read_only_and_setup_stays_incomplete_without_oauth(self):
        self.call('setup', '--runtime-ref', PIN)
        self.assertEqual(self.git('status', '--porcelain'), '')
        profile = self.root/'profile.json'
        profile.write_text(json.dumps({'schema_version': 1, 'product': 'fixture', 'sources': ['README.md', 'spec.md'], 'exclude': [], 'topics': []}))
        report = self.call('setup', '--runtime-ref', PIN, '--profile', str(profile), '--write', '--skip-local')
        self.assertTrue((self.repo/'.product-context.json').is_file())
        self.assertTrue((self.repo/'.github/workflows/product-context-wiki.yml').is_file())
        self.assertEqual(report['automation']['checks']['oauth']['code'], 'OAUTH_MISSING')
        self.assertFalse(report['complete'])
        self.assertIn('oauth', ' '.join(report['next_actions']))

    def test_oauth_is_transferred_through_stdin_without_leaking_or_replacing(self):
        result = self.call('oauth', '--token-stdin', token=SECRET+'\n', code=0)
        self.assertEqual(result['oauth']['status'], 'configured')
        state = json.loads(self.fixture.read_text())
        self.assertEqual(state['secret_digest'], hashlib.sha256(SECRET.encode()).hexdigest())
        self.call('oauth', '--token-stdin', token=SECRET+'\n', code=0)
        self.assertEqual(json.loads(self.fixture.read_text())['secret_writes'], 1)
        self.assertFalse(any('token' in p.name for p in self.repo.rglob('*')))

    def test_api_keys_are_rejected_and_failed_credential_transport_is_sanitized(self):
        report = self.call('oauth', '--token-stdin', token='sk-ant-api03-not-a-subscription-key', code=2)
        self.assertEqual(report['error']['code'], 'SUBSCRIPTION_TOKEN_REQUIRED')
        self.data['secret_exit'] = 1
        self.save()
        report = self.call('oauth', '--token-stdin', token=SECRET, code=2)
        self.assertEqual(report['error']['code'], 'OAUTH_REGISTRATION_FAILED')

    def test_secret_visibility_failure_prevents_blind_replacement(self):
        for suffix in ('secrets', 'organization-secrets'):
            self.data['routes']['repos/acme/product/actions/'+suffix] = {'_http': 403}
        self.save()
        self.call('oauth', '--token-stdin', token=SECRET, code=1)
        self.assertNotIn('secret_writes', json.loads(self.fixture.read_text()))

    def test_explicit_repository_must_match_origin_before_writes(self):
        self.git('remote', 'set-url', 'origin', 'https://github.com/another/product.git')
        report = self.call('oauth', '--token-stdin', token=SECRET, code=2)
        self.assertEqual(report['error']['code'], 'REPOSITORY_MISMATCH')
        self.assertNotIn('secret_writes', json.loads(self.fixture.read_text()))

    def live_proof(self):
        workflow = self.workflow()
        self.publish_configuration(workflow)
        source, published, snapshot = 'b'*40, 'c'*40, 'd'*64
        wiki = {'schema_version': 1, 'snapshot': snapshot, 'wiki_digest': 'e'*64, 'recorded_at': '2026-11-17T01:00:00Z'}
        review = {'schema_version': 1, 'snapshot': snapshot, 'git_head': source, 'files': {}, 'questions': []}
        proof = {'schema_version': 1, 'repository': 'acme/product', 'pr_number': 7, 'run_id': 42, 'source_head': source, 'published_commit': published, 'snapshot': snapshot,
                 'wiki_receipt_sha256': hashlib.sha256(json.dumps(wiki).encode()).hexdigest(),
                 'review_receipt_sha256': hashlib.sha256(json.dumps(review).encode()).hexdigest()}
        routes = self.data['routes']
        routes['repos/acme/product/pulls/7'] = {'number': 7, 'draft': False, 'author_association': 'OWNER', 'head': {'sha': published, 'ref': 'feature', 'repo': {'full_name': 'acme/product'}}, 'base': {'ref': 'develop'}}
        routes['repos/acme/product/actions/workflows/product-context-wiki.yml/runs?event=pull_request&branch=feature&per_page=100&page=1'] = {'workflow_runs': [{'id': 42, 'head_sha': source, 'status': 'completed', 'conclusion': 'success', 'event': 'pull_request', 'html_url': 'https://github.com/acme/product/actions/runs/42'}]}
        routes['repos/acme/product/actions/runs/42/jobs'] = {'jobs': [{'name': 'wiki', 'conclusion': 'success', 'steps': [{'name': name, 'conclusion': 'success'} for name in ('Update wiki with Claude subscription', 'Verify completion and publish document changes', 'Upload verified publication receipt')]}]}
        routes['repos/acme/product/actions/runs/42/artifacts'] = {'artifacts': [{'id': 99, 'name': 'product-context-publication-7', 'expired': False}]}
        routes['repos/acme/product/contents/.github/workflows/product-context-wiki.yml?ref='+source] = contents(workflow)
        routes['repos/acme/product/contents/.github/workflows/product-context-wiki.yml?ref='+published] = contents(workflow)
        routes['repos/acme/product/contents/.product-context.json?ref='+published] = contents(json.loads((self.repo/'.product-context.json').read_text()))
        routes['repos/acme/product/contents/.product-context/wiki-review.json?ref='+published] = contents(wiki)
        routes['repos/acme/product/contents/.product-context/review.json?ref='+published] = contents(review)
        self.set_proof(proof)
        return proof

    def set_proof(self, proof):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('product-context-publication.json', json.dumps(proof))
        self.data['routes']['repos/acme/product/actions/artifacts/99/zip'] = {'_zip': base64.b64encode(buffer.getvalue()).decode()}
        self.save()

    def test_live_publication_requires_run_bound_proof_and_current_pr_head(self):
        proof = self.live_proof()
        report = self.call('doctor', '--pr', '7')
        self.assertEqual(report['verification']['status'], 'verified')
        self.assertEqual(report['verification']['snapshot'], proof['snapshot'])
        self.assertEqual(report['verification']['published_commit'], proof['published_commit'])
        self.assertEqual(report['verification']['base_branch'], 'develop')

    def test_skipped_writer_or_ordinary_ci_success_is_not_live_verification(self):
        self.live_proof()
        self.data['routes']['repos/acme/product/actions/runs/42/jobs']['jobs'][0]['steps'][0]['conclusion'] = 'skipped'
        self.save()
        report = self.call('doctor', '--pr', '7')
        self.assertNotEqual(report['verification']['status'], 'verified')
        self.assertFalse(report['complete'])

    def test_wrong_pr_stale_head_mismatched_receipts_and_failed_push_do_not_verify(self):
        for kind in ('wrong_pr', 'stale_head', 'changed_receipt', 'failed_push', 'missing_artifact'):
            with self.subTest(kind=kind):
                proof = self.live_proof()
                if kind == 'wrong_pr':
                    proof['pr_number'] = 8
                elif kind == 'stale_head':
                    self.data['routes']['repos/acme/product/pulls/7']['head']['sha'] = 'f'*40
                elif kind == 'changed_receipt':
                    proof['wiki_receipt_sha256'] = '0'*64
                elif kind == 'failed_push':
                    self.data['routes']['repos/acme/product/actions/runs/42/jobs']['jobs'][0]['steps'][1]['conclusion'] = 'failure'
                else:
                    self.data['routes']['repos/acme/product/actions/runs/42/artifacts']['artifacts'] = []
                self.set_proof(proof)
                self.assertNotEqual(self.call('doctor', '--pr', '7')['verification']['status'], 'verified')

    def test_fork_pr_is_excluded_without_exposing_subscription_credentials(self):
        self.live_proof()
        self.data['routes']['repos/acme/product/pulls/7']['head']['repo']['full_name'] = 'fork/product'
        self.save()
        report = self.call('doctor', '--pr', '7')
        self.assertEqual(report['verification']['status'], 'excluded')
        self.assertEqual(report['verification']['code'], 'UNTRUSTED_PR')

    def test_base_branch_exclusion_is_reported_from_the_actual_workflow(self):
        self.live_proof()
        path = self.repo/'.github/workflows/product-context-wiki.yml'
        config = json.loads(path.read_text())
        config['on']['pull_request']['branches'] = ['main']
        path.write_text(json.dumps(config))
        self.data['routes']['repos/acme/product/contents/.github/workflows/product-context-wiki.yml?ref='+'c'*40] = contents(config)
        self.save()
        report = self.call('doctor', '--pr', '7')
        self.assertEqual(report['eligibility']['status'], 'excluded')
        self.assertEqual(report['eligibility']['code'], 'BASE_BRANCH_EXCLUDED')
        self.assertEqual(report['eligibility']['base_branch'], 'develop')

    def test_opt_in_conflict_and_symlinked_workflow_are_rejected_before_writes(self):
        self.profile()
        opt_in = self.repo/'.product-context/automation.json'
        opt_in.parent.mkdir()
        opt_in.write_text('{"mode":"manual"}\n')
        before = self.git('status', '--porcelain')
        report = self.call('setup', '--runtime-ref', PIN, '--write', '--skip-local', code=2)
        self.assertEqual(report['error']['code'], 'SETUP_EXISTS')
        self.assertEqual(self.git('status', '--porcelain'), before)
        opt_in.unlink()
        outside = self.root/'outside.json'
        outside.write_text('{}')
        path = self.repo/'.github/workflows/product-context-wiki.yml'
        path.parent.mkdir(parents=True)
        path.symlink_to(outside)
        report = self.call('setup', '--runtime-ref', PIN, '--write', '--skip-local', code=2)
        self.assertEqual(report['error']['code'], 'UNSAFE_DESTINATION')
        self.assertEqual(outside.read_text(), '{}')

    def test_new_profile_preflights_publishability_before_any_product_write(self):
        (self.repo/'.gitignore').write_text('openwiki/\n.product-context/\n')
        profile = self.root/'profile.json'
        profile.write_text(json.dumps({'schema_version':1,'product':'fixture','sources':['README.md'],'exclude':[],'topics':[]}))
        before = self.git('status', '--porcelain')
        report = self.call('setup', '--runtime-ref', PIN, '--profile', str(profile), '--write', '--skip-local', code=2)
        self.assertEqual(report['error']['code'], 'IGNORED_OUTPUT')
        self.assertEqual(self.git('status', '--porcelain'), before)
        self.assertFalse((self.repo/'.product-context.json').exists())

    def test_github_repository_case_differences_do_not_exclude_a_trusted_pr(self):
        proof = self.live_proof()
        self.data['routes']['repos/acme/product/pulls/7']['head']['repo']['full_name'] = 'Acme/Product'
        proof['repository'] = 'Acme/Product'
        self.set_proof(proof)
        report = self.call('doctor', '--pr', '7')
        self.assertEqual(report['verification']['status'], 'verified')

    def test_rejected_actions_oauth_is_distinct_and_requires_explicit_rotation(self):
        proof = self.live_proof()
        routes = self.data['routes']
        routes['repos/acme/product/pulls/7']['head']['sha'] = proof['source_head']
        run = routes['repos/acme/product/actions/workflows/product-context-wiki.yml/runs?event=pull_request&branch=feature&per_page=100&page=1']['workflow_runs'][0]
        run['conclusion'] = 'failure'
        job = routes['repos/acme/product/actions/runs/42/jobs']['jobs'][0]
        job['id'] = 55
        job['conclusion'] = 'failure'
        job['steps'][0]['conclusion'] = 'failure'
        log = '2026-11-17T01:00:00.000Z API Error: 401 authentication_error: OAuth token has expired '+SECRET
        routes['repos/acme/product/actions/jobs/55/logs'] = {'_raw':base64.b64encode(log.encode()).decode()}
        self.save()
        report = self.call('doctor', '--pr', '7')
        self.assertEqual(report['verification']['code'], 'OAUTH_AUTHENTICATION_FAILED')
        self.assertEqual(report['automation']['checks']['oauth']['authentication'], 'rejected')
        self.assertEqual(report['automation']['status'], 'incomplete')
        self.assertIn('--replace', ' '.join(report['next_actions']))
        self.call('oauth', '--replace', '--token-stdin', token=SECRET, code=0)
        self.assertEqual(json.loads(self.fixture.read_text())['secret_writes'], 1)

    def test_application_text_about_authentication_errors_does_not_reject_the_oauth_secret(self):
        proof = self.live_proof()
        routes = self.data['routes']
        routes['repos/acme/product/pulls/7']['head']['sha'] = proof['source_head']
        routes['repos/acme/product/actions/workflows/product-context-wiki.yml/runs?event=pull_request&branch=feature&per_page=100&page=1']['workflow_runs'][0]['conclusion'] = 'failure'
        job = routes['repos/acme/product/actions/runs/42/jobs']['jobs'][0]
        job['id'], job['conclusion'] = 55, 'failure'
        job['steps'][0]['conclusion'] = 'failure'
        log = 'Reading source: authentication_error is an application event documented in spec.md.\nError: Reached maximum number of turns (16).'
        routes['repos/acme/product/actions/jobs/55/logs'] = {'_raw':base64.b64encode(log.encode()).decode()}
        self.save()
        report = self.call('doctor', '--pr', '7')
        self.assertEqual(report['verification']['code'], 'PR_PUBLICATION_UNVERIFIED')
        self.assertEqual(report['automation']['checks']['oauth']['authentication'], 'unverified')
        self.assertNotIn('--replace', ' '.join(report['next_actions']))

    def test_setup_preserves_formatter_rules_and_excludes_only_its_generated_outputs(self):
        self.profile()
        ignore = self.repo/'.prettierignore'
        ignore.write_text('# Existing owner rules\ndocs/legacy.md\n')
        self.call('setup', '--runtime-ref', PIN, '--write', '--skip-local')
        content = ignore.read_text()
        self.assertTrue(content.startswith('# Existing owner rules\ndocs/legacy.md\n'))
        entries = [line for line in content.splitlines() if line and not line.startswith('#')]
        self.assertEqual(entries, ['docs/legacy.md','.github/workflows/product-context-wiki.yml','openwiki/','.product-context/'])
        self.call('setup', '--runtime-ref', PIN, '--write', '--skip-local')
        self.assertEqual(ignore.read_text(), content)


if __name__ == '__main__':
    unittest.main()
