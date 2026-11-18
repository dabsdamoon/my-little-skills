"""Artifact-route CLI behavior using only a fake external model process."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/artifact_benchmark.py'


class ArtifactCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.out = self.root / 'experiment'
        self.starter = self.root / 'starter'
        self.starter.mkdir()
        (self.starter / 'input.txt').write_text('same starting state')
        self.prompt = self.root / 'task.txt'
        self.prompt.write_text('Implement the requested artifact and verify it.')
        self.criteria = self.root / 'grading.json'
        self.criteria.write_text('{"acceptance":"result.txt must say implemented"}')
        self.fake = self.root / 'codex'
        self.fake.write_text('''#!/usr/bin/env python3
import json,pathlib,sys
if sys.argv[1:]==['login','status']: print('Logged in using ChatGPT');sys.exit(0)
if sys.argv[1:]==['--version']: print('codex-cli fixture');sys.exit(0)
cwd=pathlib.Path(sys.argv[sys.argv.index('--cd')+1])
assert (cwd/'input.txt').read_text()=='same starting state'
assert 'features.shell_tool=true' in sys.argv
assert sys.argv[sys.argv.index('--sandbox')+1]=='workspace-write'
assert 'approval_policy="never"' in sys.argv
model=sys.argv[sys.argv.index('--model')+1]
if model=='missing': print(json.dumps({'type':'turn.failed'}));sys.exit(1)
(cwd/'result.txt').write_text('implemented')
answer='Finished artifact'
pathlib.Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text(answer)
kind='mcp_tool_call' if model=='forbidden' else 'command_execution'
print(json.dumps({'type':'item.completed','item':{'type':kind,'command':'python3 verify.py','exit_code':0}}))
print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':answer}}))
print(json.dumps({'type':'turn.completed','usage':{'input_tokens':20,'output_tokens':10}}))
''')
        self.fake.chmod(0o755)

    def cli(self, *args, ok=True):
        r = subprocess.run([sys.executable, str(SCRIPT), *map(str,args)],capture_output=True,text=True)
        if ok: self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        else: self.assertNotEqual(r.returncode,0)
        return r

    def plan(self, models=('a','b')):
        self.cli('plan','--out',self.out,'--starter',self.starter,'--prompt',self.prompt,
                 '--grading-spec',self.criteria,'--models',*models,'--effort','low')

    def test_isolated_artifacts_frozen_inputs_budget_and_no_duplicate_launches(self):
        self.plan()
        self.cli('run','--out',self.out,'--codex',self.fake,'--max-calls',1,ok=False)
        self.cli('run','--out',self.out,'--codex',self.fake,'--max-calls',2)
        manifest = self.out / 'runs.json'
        data = json.loads(manifest.read_text())
        self.assertEqual([r['status'] for r in data['runs']],['completed','completed'])
        for i in (1,2):
            self.assertEqual((self.out/f'workspaces/run-{i:02}/result.txt').read_text(),'implemented')
        self.assertFalse((self.out/'starter/result.txt').exists())
        self.assertIn('result.txt',data['runs'][0]['artifacts'])
        self.assertIn('implemented',(self.out/'run-01.diff').read_text())
        before=manifest.read_bytes()
        self.cli('run','--out',self.out,'--codex',self.fake,'--max-calls',2)
        self.assertEqual(manifest.read_bytes(),before)
        manifest.unlink()
        self.cli('run','--out',self.out,'--codex',self.fake,'--max-calls',2,ok=False)

    def test_frozen_starter_or_grading_changes_block_execution(self):
        self.plan()
        (self.out/'starter/input.txt').write_text('changed')
        self.cli('run','--out',self.out,'--codex',self.fake,'--max-calls',2,ok=False)
        self.assertFalse((self.out/'runs.json').exists())

    def test_external_tools_and_transport_failures_are_distinct(self):
        self.plan(('forbidden','missing'))
        self.cli('run','--out',self.out,'--codex',self.fake,'--max-calls',2)
        data=json.loads((self.out/'runs.json').read_text())
        self.assertEqual([r['status'] for r in data['runs']],['control_violation','unavailable'])

    def test_extra_unfrozen_starter_file_cannot_change_contestant_context(self):
        self.plan()
        (self.out/'starter/extra.txt').write_text('not present at design freeze')
        self.cli('run','--out',self.out,'--codex',self.fake,'--max-calls',2,ok=False)
        self.assertFalse((self.out/'runs.json').exists())

    def test_ignored_directories_are_excluded_from_contestant_copies(self):
        self.plan()
        for name in ('.git','__pycache__'):
            p=self.out/'starter'/name
            p.mkdir()
            (p/'unfrozen.txt').write_text('must not reach a contestant')
        self.cli('run','--out',self.out,'--codex',self.fake,'--max-calls',2)
        for i in (1,2):
            for name in ('.git','__pycache__'):
                self.assertFalse((self.out/f'workspaces/run-{i:02}'/name).exists())


if __name__=='__main__': unittest.main()
