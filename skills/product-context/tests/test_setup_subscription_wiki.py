from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / 'scripts/setup_subscription_wiki.py'

FAKE_CLI = '''#!/usr/bin/env python3
import json,os,sys,time
from pathlib import Path
tool=Path(sys.argv[0]).name
args=sys.argv[1:]
file=Path(os.environ['FIXTURE_MCP_STATE'])
state=json.loads(file.read_text()) if file.exists() else {'registrations':{},'events':[]}
if tool=='npm':
    state['events'].append(['npm',*args])
    target=Path.cwd()/'node_modules'
    if not target.exists(): target.symlink_to(os.environ['FIXTURE_REAL_NODE_MODULES'],target_is_directory=True)
    if os.environ.get('FIXTURE_NPM_BARRIER'):
        barrier=Path(os.environ['FIXTURE_NPM_BARRIER'])
        (barrier/('entered-'+str(os.getpid()))).touch()
        deadline=time.monotonic()+15
        while not (barrier/'release').exists():
            if time.monotonic()>deadline:sys.exit(9)
            time.sleep(0.02)
elif args[:2]==['login','status']:
    print('Logged in using ChatGPT',file=sys.stderr);sys.exit(0)
elif args[:2]==['auth','status']:
    print(json.dumps({'loggedIn':True,'authMethod':'claude.ai','apiProvider':'firstParty'}));sys.exit(0)
elif args[:2]==['mcp','get']:
    entry=state['registrations'].get(tool)
    if entry is None:sys.exit(1)
    print(json.dumps(entry));sys.exit(0)
elif args[:2]==['mcp','remove']:
    state['registrations'].pop(tool,None)
elif args[:2]==['mcp','add']:
    command=args[args.index('--')+1:]
    state['registrations'][tool]={'command':command[0],'args':command[1:]}
    state['events'].append([tool,*args])
else:
    sys.exit(2)
file.write_text(json.dumps(state))
'''


class SubscriptionSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.state = self.root / 'mcp-state.json'
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        for name in ['codex', 'claude', 'npm']:
            script = bin_dir / name
            script.write_text(FAKE_CLI)
            script.chmod(0o755)
        self.env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'], FIXTURE_MCP_STATE=str(self.state), FIXTURE_REAL_NODE_MODULES=str(SKILL / 'runtime/node_modules'))
        for key in ['OPENAI_API_KEY', 'CODEX_API_KEY', 'ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'CLAUDE_CODE_OAUTH_TOKEN']:
            self.env.pop(key, None)
        self.target = self.root / 'installed/0.3.1'

    def run_setup(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(['python3', '-B', str(SCRIPT), '--install-root', str(self.target), '--host', 'both', '--json', *args], env=self.env, capture_output=True, text=True)

    def test_default_plan_is_read_only_and_names_both_subscription_hosts(self) -> None:
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['mode'], 'plan')
        self.assertEqual(report['hosts'], ['claude', 'codex'])
        self.assertEqual(report.get('completion'), 'local_only')
        self.assertFalse(report.get('automation_ready', True))
        self.assertFalse(self.target.exists())
        self.assertFalse(self.state.exists())

    def test_install_registers_stable_runtime_and_a_second_install_is_idempotent(self) -> None:
        first = self.run_setup('--install')
        self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
        self.assertEqual((self.target / 'runtime/server.mjs').read_bytes(), (SKILL / 'runtime/server.mjs').read_bytes())
        self.assertEqual((self.target / 'scripts/product_context.py').read_bytes(), (SKILL / 'scripts/product_context.py').read_bytes())
        state = json.loads(self.state.read_text())
        self.assertEqual(set(state['registrations']), {'claude', 'codex'})
        for host in ['claude', 'codex']:
            self.assertEqual(state['registrations'][host]['args'], [str(self.target / 'runtime/server.mjs'), '--host', host])
        npm = next(event for event in state['events'] if event[0] == 'npm')
        self.assertIn('--ignore-scripts', npm)
        before = self.state.read_bytes()
        second = self.run_setup('--install')
        self.assertEqual(second.returncode, 0, second.stderr + second.stdout)
        self.assertEqual(self.state.read_bytes(), before)

    def test_product_doctor_refuses_a_managed_runtime_with_missing_dependencies(self) -> None:
        result = self.run_setup('--install')
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        dependencies = self.target/'runtime/node_modules'
        dependencies.unlink()  # Fixture npm linked real dependencies; damage only the installed copy.
        (dependencies/'openwiki').mkdir(parents=True)
        (dependencies/'openwiki/package.json').write_text('{"version":"0.9.0"}')
        product = self.root/'product'
        product.mkdir()
        subprocess.run(['git', 'init', '-q', str(product)], check=True)
        subprocess.run(['git', '-C', str(product), 'remote', 'add', 'origin', 'https://github.com/acme/product.git'], check=True)
        gh = self.root/'bin/gh'
        gh.write_text('#!/bin/sh\nprintf \'%s\\n\' \'{"secrets":[],"default_branch":"develop"}\'\n')
        gh.chmod(0o755)
        result = subprocess.run(['python3', '-B', str(SKILL/'scripts/product_setup.py'), 'doctor', '--repo', str(product), '--install-root', str(self.target), '--host', 'both'], env=self.env, capture_output=True, text=True)
        report = json.loads(result.stdout)
        self.assertEqual(report['local']['status'], 'incomplete')
        for host in ('claude', 'codex'):
            self.assertNotEqual(report['local']['hosts'][host]['status'], 'ready')

    def test_an_unowned_same_name_server_is_preserved_without_installing(self) -> None:
        state = {'registrations': {'claude': {'command': 'node', 'args': ['/unrelated/server.mjs']}}, 'events': []}
        self.state.write_text(json.dumps(state))
        before = self.state.read_bytes()
        result = self.run_setup('--install')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('UNMANAGED_SERVER', result.stdout)
        self.assertEqual(self.state.read_bytes(), before)
        self.assertFalse(self.target.exists())

    def test_a_symlinked_install_ancestor_is_rejected_without_writing_its_target(self) -> None:
        outside = self.root / 'outside'
        outside.mkdir()
        alias = self.root / 'alias'
        alias.symlink_to(outside, target_is_directory=True)
        self.target = alias / '0.3.1'
        result = self.run_setup('--install')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('UNSAFE_DESTINATION', result.stdout)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse(self.state.exists())

    def test_a_symlinked_registry_does_not_overwrite_unrelated_json(self) -> None:
        self.target.parent.mkdir()
        unrelated = self.root / 'unrelated.json'
        unrelated.write_text('{}\n')
        (self.target.parent / 'registrations.json').symlink_to(unrelated)
        result = self.run_setup('--install')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('UNSAFE_DESTINATION', result.stdout)
        self.assertEqual(unrelated.read_text(), '{}\n')
        self.assertFalse(self.target.exists())

    def test_concurrent_setup_cannot_enter_npm_or_registration_twice(self) -> None:
        barrier = self.root / 'barrier'
        barrier.mkdir()
        env = dict(self.env, FIXTURE_NPM_BARRIER=str(barrier))
        args = ['python3', '-B', str(SCRIPT), '--install-root', str(self.target), '--host', 'both', '--json', '--install']
        first = subprocess.Popen(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        second = None
        second_entered = False
        try:
            deadline = time.monotonic() + 10
            while not list(barrier.glob('entered-*')):
                self.assertIsNone(first.poll(), 'First installer exited before the npm boundary')
                self.assertLess(time.monotonic(), deadline, 'First installer did not reach npm')
                time.sleep(0.02)
            second = subprocess.Popen(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            deadline = time.monotonic() + 10
            while second.poll() is None and len(list(barrier.glob('entered-*'))) < 2:
                self.assertLess(time.monotonic(), deadline, 'Second installer neither stopped nor reached npm')
                time.sleep(0.02)
            second_entered = len(list(barrier.glob('entered-*'))) > 1
        finally:
            (barrier / 'release').touch()
            out1, err1 = first.communicate(timeout=15)
            if second is not None:
                out2, err2 = second.communicate(timeout=15)
        self.assertFalse(second_entered, 'Concurrent installers both entered the same npm transaction')
        self.assertEqual(first.returncode, 0, out1 + err1)
        self.assertEqual(second.returncode, 2, out2 + err2)
        self.assertIn('SETUP_BUSY', out2)


if __name__ == '__main__':
    unittest.main()
