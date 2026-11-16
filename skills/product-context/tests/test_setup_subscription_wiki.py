from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / 'scripts/setup_subscription_wiki.py'

FAKE_CLI = '''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
tool=Path(sys.argv[0]).name
args=sys.argv[1:]
file=Path(os.environ['FIXTURE_MCP_STATE'])
state=json.loads(file.read_text()) if file.exists() else {'registrations':{},'events':[]}
if tool=='npm':
    state['events'].append(['npm',*args])
    target=Path.cwd()/'node_modules'
    if not target.exists(): target.symlink_to(os.environ['FIXTURE_REAL_NODE_MODULES'],target_is_directory=True)
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
        self.root = Path(self.temporary.name)
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
        self.target = self.root / 'installed/0.2.0'

    def run_setup(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(['python3', '-B', str(SCRIPT), '--install-root', str(self.target), '--host', 'both', '--json', *args], env=self.env, capture_output=True, text=True)

    def test_default_plan_is_read_only_and_names_both_subscription_hosts(self) -> None:
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['mode'], 'plan')
        self.assertEqual(report['hosts'], ['claude', 'codex'])
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

    def test_an_unowned_same_name_server_is_preserved_without_installing(self) -> None:
        state = {'registrations': {'claude': {'command': 'node', 'args': ['/unrelated/server.mjs']}}, 'events': []}
        self.state.write_text(json.dumps(state))
        before = self.state.read_bytes()
        result = self.run_setup('--install')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('UNMANAGED_SERVER', result.stdout)
        self.assertEqual(self.state.read_bytes(), before)
        self.assertFalse(self.target.exists())


if __name__ == '__main__':
    unittest.main()
