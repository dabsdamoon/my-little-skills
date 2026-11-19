"""Cross-host behavior through fake native executables, never through a provider API."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
MODEL='claude-sonnet-5-5'


class ClaudeSubscriptionCLI(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.out=self.root/'experiment'
        self.suite=self.root/'suite.json'
        self.suite.write_text(json.dumps({'name':'fixture','cases':[{'id':'a','category':'math','prompt':'2-2?','expected':0}]}))
        self.claude=self.root/'claude'
        self.claude.write_text('''#!/usr/bin/env python3
import json,pathlib,sys
args=sys.argv[1:];root=pathlib.Path(__file__).parent
if args==['--version']: print('2.1.fixture (Claude Code)');sys.exit(0)
if args==['auth','status','--json']:
    print(json.dumps({'loggedIn':True,'authMethod':'api_key' if (root/'api-auth').exists() else 'claude.ai','apiProvider':'firstParty'}));sys.exit(0)
for marker in ['--safe-mode','--restricted','--no-session-persistence','--strict-mcp-config','--disable-slash-commands']: assert marker in args
assert '--bare' not in args and '--continue' not in args and '--resume' not in args
assert args[args.index('--effort')+1]=='low'
session=args[args.index('--session-id')+1]
with (root/'sessions.log').open('a') as f:f.write(session+'\\n')
tools=args[args.index('--tools')+1]
settings=json.loads(args[args.index('--settings')+1])
assert settings.get('availableModelsMatch')=='exact'
assert settings.get('enforceAvailableModels') is True
if tools: assert settings['sandbox'].get('failIfUnavailable') is True
actual='claude-other' if (root/'fallback').exists() else 'claude-sonnet-5-5'
plugins=[{'name':'cc-plugin-privacy','path':'builtin','source':'cc-plugin-privacy@builtin'}] if (root/'builtin').exists() else []
if (root/'custom-plugin').exists():plugins.append({'name':'personal','path':'/private/plugin','source':'personal@custom'})
inventory=tools.split(',') if tools else []
if (root/'untrusted-inventory').exists(): inventory=['WebSearch']
print(json.dumps({'type':'system','subtype':'init','session_id':session,'model':actual,'tools':inventory,'permissionMode':'bypassPermissions' if (root/'wrong-mode').exists() else 'dontAsk','apiKeySource':'env' if (root/'api-source').exists() else 'none','mcp_servers':[],'plugins':plugins,'skills':['ambient-skill'] if (root/'ambient').exists() else []}))
if (root/'server-search').exists(): print(json.dumps({'type':'assistant','message':{'model':actual,'content':[{'type':'server_tool_use','name':'web_search','id':'s1'}]}}))
if tools:
    pathlib.Path('result.txt').write_text('implemented')
    print(json.dumps({'type':'assistant','message':{'model':actual,'content':[{'type':'tool_use','id':'t1','name':'Bash','input':{'command':'python3 verify.py'}}]}}))
text='done' if tools else '{"a":0}'
print(json.dumps({'type':'assistant','message':{'model':actual,'content':[{'type':'text','text':text}]}}))
usage={'input_tokens':10,'cache_read_input_tokens':4,'cache_creation_input_tokens':2,'output_tokens':8}
if (root/'server-usage').exists():usage['server_tool_use']={'web_search_requests':1}
print(json.dumps({'type':'result','subtype':'success','is_error':False,'result':text,'session_id':'different' if (root/'wrong-session').exists() else session,'permission_denials':[],'usage':usage,'modelUsage':{actual:{'inputTokens':16,'outputTokens':8}}}))
''');self.claude.chmod(0o755)
        self.codex=self.root/'codex'
        self.codex.write_text('''#!/usr/bin/env python3
import json,pathlib,sys
args=sys.argv[1:]
if args==['--version']:print('codex-cli fixture');sys.exit(0)
if args==['login','status']:print('Logged in using ChatGPT');sys.exit(0)
text='{"a":0}'
pathlib.Path(args[args.index('--output-last-message')+1]).write_text(text)
print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':text}}))
print(json.dumps({'type':'turn.completed','usage':{'input_tokens':16,'output_tokens':8}}))
''');self.codex.chmod(0o755)

    def cli(self, script, *args, ok=True):
        p=subprocess.run([sys.executable,str(SCRIPTS/script),*map(str,args)],text=True,capture_output=True)
        if ok:self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        else:self.assertNotEqual(p.returncode,0)
        return p

    def plan_text(self,trials=1):
        self.cli('codex_benchmark.py','plan','--out',self.out,'--suite',self.suite,
                 '--models','good',MODEL,'--claude-models',MODEL,'--effort','low','--trials',trials)

    def run_text(self,budget=2,ok=True):
        self.cli('codex_benchmark.py','run','--out',self.out,'--codex',self.codex,
                 '--claude',self.claude,'--max-calls',budget,ok=ok)

    def test_fresh_subscription_sessions_and_original_native_evidence(self):
        self.plan_text(2);self.run_text(4)
        self.cli('codex_benchmark.py','report','--out',self.out)
        scores=json.loads((self.out/'results.json').read_text())
        self.assertTrue(scores['complete'])
        self.assertEqual(scores['models'][MODEL]['trial_accuracy'],[1,1])
        sessions=(self.root/'sessions.log').read_text().splitlines()
        self.assertEqual(len(sessions),2);self.assertEqual(len(set(sessions)),2)
        runs=json.loads((self.out/'runs.json').read_text())['runs']
        native=next(r for r in runs if r['model']==MODEL)
        self.assertEqual(native['host'],'claude')
        self.assertTrue((self.out/native['native_events_file']).exists())
        self.assertEqual(native['usage']['input_tokens'],16)
        self.assertEqual(native['usage']['cached_input_tokens'],4)
        before=(self.root/'sessions.log').read_bytes();self.run_text(4)
        self.assertEqual((self.root/'sessions.log').read_bytes(),before)

    def test_api_auth_rejected_before_any_contestant_call(self):
        self.plan_text();(self.root/'api-auth').touch();self.run_text(ok=False)
        self.assertFalse((self.out/'runs.json').exists())
        self.assertFalse((self.root/'sessions.log').exists())

    def test_fallback_or_ambient_context_invalidates_trial(self):
        for marker in ['fallback','ambient']:
            with self.subTest(marker=marker):
                self.out=self.root/(marker+'-run');self.plan_text()
                flag=self.root/('fallback' if marker=='fallback' else 'ambient')
                flag.touch()
                self.run_text();self.cli('codex_benchmark.py','report','--out',self.out)
                result=json.loads((self.out/'results.json').read_text())
                self.assertIsNone(result['models'][MODEL]['accuracy'])
                self.assertEqual(next(r for r in result['trials'] if r['model']==MODEL)['status'],'control_violation')
                flag.unlink()

    def test_claude_artifact_route_writes_real_workspace_and_records_tools(self):
        starter=self.root/'starter';starter.mkdir();(starter/'input.txt').write_text('frozen')
        prompt=self.root/'prompt.txt';prompt.write_text('Write result.txt and verify it.')
        criteria=self.root/'grading.json';criteria.write_text('{"acceptance":"result.txt"}')
        self.cli('artifact_benchmark.py','plan','--out',self.out,'--starter',starter,'--prompt',prompt,
                 '--grading-spec',criteria,'--models','good',MODEL,'--claude-models',MODEL,'--effort','low')
        self.cli('artifact_benchmark.py','run','--out',self.out,'--codex',self.codex,
                 '--claude',self.claude,'--max-calls',2)
        run=json.loads((self.out/'runs.json').read_text())['runs'][1]
        self.assertEqual(run['status'],'completed')
        self.assertEqual((self.out/run['workspace']/'result.txt').read_text(),'implemented')
        self.assertEqual(run['tool_events'][0]['host_tool'],'Bash')

    def test_builtin_catalog_is_disclosed_but_custom_plugins_are_invalid(self):
        (self.root/'builtin').touch();self.plan_text();self.run_text()
        self.cli('codex_benchmark.py','report','--out',self.out)
        result=json.loads((self.out/'results.json').read_text())
        self.assertEqual(result['models'][MODEL]['accuracy'],1)
        run=json.loads((self.out/'runs.json').read_text())['runs'][1]
        self.assertEqual(run['native_builtin_plugins'][0]['name'],'cc-plugin-privacy')
        self.out=self.root/'custom-run';(self.root/'custom-plugin').touch();self.plan_text();self.run_text()
        self.cli('codex_benchmark.py','report','--out',self.out)
        result=json.loads((self.out/'results.json').read_text())
        self.assertIsNone(result['models'][MODEL]['accuracy'])

    def test_native_inventory_session_and_server_search_are_checked(self):
        markers=['untrusted-inventory','wrong-session','server-search','server-usage','wrong-mode','api-source']
        for marker in markers:
            with self.subTest(marker=marker):
                for old in markers:(self.root/old).unlink(missing_ok=True)
                self.out=self.root/(marker+'-run');self.plan_text();flag=self.root/marker;flag.touch()
                self.run_text();self.cli('codex_benchmark.py','report','--out',self.out)
                result=json.loads((self.out/'results.json').read_text())
                self.assertIsNone(result['models'][MODEL]['accuracy'])
                self.assertEqual(next(r for r in result['trials'] if r['model']==MODEL)['status'],'control_violation')
                flag.unlink()

    def test_claude_native_audit_cannot_be_bypassed_by_removing_host(self):
        self.plan_text();self.run_text()
        path=self.out/'runs.json';data=json.loads(path.read_text());data['runs'][1].pop('host')
        path.write_text(json.dumps(data))
        self.cli('codex_benchmark.py','report','--out',self.out,ok=False)


if __name__=='__main__':unittest.main()
