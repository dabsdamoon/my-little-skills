#!/usr/bin/env python3
"""Install and verify PR-triggered wiki updates using Claude subscription OAuth."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from setup_subscription_wiki import SetupError, safe_destination, write_json

SKILL = Path(__file__).resolve().parents[1]
WORKFLOW = '.github/workflows/product-context-wiki.yml'
HARNESS = 'dabsdamoon/my-little-skills'
CHECKOUT = 'actions/checkout@11d5960a326750d5838078e36cf38b85af677262'
NODE = 'actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020'
CLAUDE = 'anthropics/claude-code-action@f3b070c88125d33dbae5653df5f143101d4ea9dc'
OUTPUTS = {'.product-context/review.json', '.product-context/wiki-review.json', '.openwikiignore', 'AGENTS.md', 'CLAUDE.md'}
RULES = {'.product-context/', '.product-context.json', '.github/workflows/openwiki-update.yml'}


def fail(code, message):
    raise SetupError(f'{code}: {message}')


def run(args, root=None):
    result = subprocess.run(args, cwd=root, capture_output=True, text=True)
    if result.returncode:
        fail('COMMAND_FAILED', f'{args[0]} failed; no model/API fallback is attempted.')
    return result.stdout


def status(root):
    code = "const g=await import(process.argv[1]);const root=await g.rootPath(process.argv[2]);const report=await g.context(root);console.log(JSON.stringify({context:report,wiki:await g.wikiStatus(root,report)}));"
    return json.loads(run(['node', '--input-type=module', '-e', code, (SKILL / 'runtime/guard.mjs').as_uri(), str(root)]))


def read_optional(path):
    safe_destination(path)
    if not path.exists():
        return None
    if path.stat().st_size > 1048576:
        fail('SOURCE_TOO_LARGE', 'Managed state or instruction file exceeds 1 MiB.')
    return path.read_text()


def fingerprint(path):
    value = read_optional(path)
    return None if value is None else hashlib.sha256(value.encode()).hexdigest()


def write_outputs(path, report):
    if path:
        with Path(path).open('a') as stream:
            stream.write('should_run=' + str(report['should_run']).lower() + '\n')


def prepare(root, args):
    event = json.loads(Path(args.event).read_text())
    pr = event.get('pull_request', {})
    repository = event.get('repository', {}).get('full_name')
    if (not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository or '')
            or pr.get('head', {}).get('repo', {}).get('full_name') != repository
            or pr.get('author_association') not in {'OWNER', 'MEMBER', 'COLLABORATOR'}):
        fail('UNTRUSTED_PR', 'Only same-repository PRs from trusted collaborators may use subscription credentials.')
    if pr.get('draft') or event.get('action') not in {'opened', 'synchronize', 'reopened', 'ready_for_review'}:
        return {'should_run': False, 'reason': 'Draft or unsupported PR event', 'model_calls': 0}
    head = pr.get('head', {}).get('sha', '')
    if not re.fullmatch(r'[a-f0-9]{40}', head) or run(['git', 'rev-parse', 'HEAD'], root).strip() != head:
        fail('HEAD_CHANGED', 'Checkout must match the triggering PR head exactly.')
    branch = pr['head'].get('ref', '')
    run(['git', 'check-ref-format', 'refs/heads/' + branch], root)
    view = status(root)
    report = view['context']
    if report['missing_sources'] or report['broken_links']:
        fail('CONTEXT_FINDINGS', 'Repair missing primary sources and broken local links before generation.')
    if any(p.startswith('openwiki/') for p in report['files']):
        fail('SELF_REFERENCE', 'Exclude generated openwiki files from primary context sources.')
    if report['review']['status'] == 'current' and view['wiki']['status'] == 'current':
        return {'should_run': False, 'reason': 'Primary sources and guarded wiki are current', 'model_calls': 0}
    state = {'schema_version': 1, 'root': str(root), 'head': head, 'branch': branch,
             'files': report['files'], 'profile': fingerprint(root / '.product-context.json'),
             'decisions': fingerprint(root / '.product-context/decisions.json'),
             'notes': {name: read_optional(root / name) for name in ['AGENTS.md', 'CLAUDE.md', '.openwikiignore']}}
    state_path = Path(args.state).absolute()
    if root == state_path or root in state_path.parents:
        fail('UNSAFE_STATE', 'Keep the trusted run state outside the product checkout.')
    write_json(state_path, state)
    mcp = {'mcpServers': {'product_context': {'command': 'node', 'args': [str(SKILL / 'runtime/server.mjs'), '--host', 'claude'],
             'env': {'OPENWIKI_TELEMETRY_DISABLED': '1', 'DO_NOT_TRACK': '1', 'PRODUCT_CONTEXT_ALLOWED_ROOT': str(root)}}}}
    write_json(state_path.parent / 'product-context-mcp.json', mcp)
    absolute = '/' + str(root)
    settings = {'permissions': {'allow': [f'Read({absolute}/**)', f'Read(/{SKILL}/**)', 'Glob', 'Grep',
                    f'Write({absolute}/openwiki/**)', f'Edit({absolute}/openwiki/**)', 'mcp__product_context__*'],
                    'deny': ['Bash', f'Read({absolute}/.git/**)', f'Read({absolute}/.env)', f'Read({absolute}/.env.*)']}}
    write_json(state_path.parent / 'product-context-settings.json', settings)
    return {'should_run': True, 'snapshot': report['snapshot'], 'state': str(state_path), 'model_calls': 0}


def strip_note(text):
    return re.sub(r'<!-- OPENWIKI:START -->.*?<!-- OPENWIKI:END -->', '', text or '', flags=re.S).strip()


def verify(root, args):
    safe_destination(Path(args.state))
    state = json.loads(Path(args.state).read_text())
    if state.get('schema_version') != 1 or state.get('root') != str(root):
        fail('INVALID_STATE', 'The trusted preflight state belongs to another checkout.')
    if run(['git', 'rev-parse', 'HEAD'], root).strip() != state['head']:
        fail('HEAD_CHANGED', 'The local checkout changed during generation.')
    view = status(root)
    report = view['context']
    if view['wiki']['status'] != 'current' or report['review']['status'] != 'current':
        fail('WIKI_NOT_CURRENT', 'A complete guarded wiki receipt and inspected review are required before publishing.')
    if fingerprint(root / '.product-context.json') != state['profile'] or fingerprint(root / '.product-context/decisions.json') != state['decisions']:
        fail('SOURCE_CHANGED', 'Primary configuration or decision history changed during generation.')
    before = {p: sha for p, sha in state['files'].items() if p not in {'AGENTS.md', 'CLAUDE.md'}}
    after = {p: sha for p, sha in report['files'].items() if p not in {'AGENTS.md', 'CLAUDE.md'}}
    if before != after:
        fail('SOURCE_CHANGED', 'Primary specification or implementation evidence changed during generation.')
    for name in ['AGENTS.md', 'CLAUDE.md']:
        if strip_note(read_optional(root / name)) != strip_note(state['notes'][name]):
            fail('SOURCE_CHANGED', 'Only the managed OpenWiki instruction block may change in agent rules.')
    old_ignore = (state['notes']['.openwikiignore'] or '').splitlines()
    new_ignore = (read_optional(root / '.openwikiignore') or '').splitlines()
    if new_ignore[:len(old_ignore)] != old_ignore or any(line not in RULES for line in new_ignore[len(old_ignore):]):
        fail('OUT_OF_SCOPE', 'Existing ignore rules must be preserved; only bridge exclusions may be appended.')
    changed = set(run(['git', 'diff', '--name-only', '-z', 'HEAD'], root).split('\0'))
    changed.update(run(['git', 'ls-files', '--others', '--exclude-standard', '-z'], root).split('\0'))
    changed.discard('')
    for name in changed:
        safe_destination(root / name)
        if name not in OUTPUTS and not name.startswith('openwiki/'):
            fail('OUT_OF_SCOPE', f'Generated work changed a non-document output: {name}')
    if (root / '.product-context/wiki.lock').exists() or (root / 'openwiki/.run.json').exists():
        fail('WIKI_NOT_CURRENT', 'An active or interrupted run cannot be published.')
    if args.commit and changed:
        run(['git', 'add', '--', *sorted(changed)], root)
        run(['git', '-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com', 'commit', '-m', 'docs: update product wiki for PR'], root)
    return {'verified': True, 'publish_paths': sorted(changed), 'branch': state['branch'], 'model_calls': 0}


def workflow(ref):
    tool = 'harness/skills/product-context/scripts/pr_wiki.py'
    state = '"$RUNNER_TEMP/product-context-state.json"'
    prompt = ('Read harness/skills/product-context/SKILL.md and harness/skills/product-context/references/subscription-wiki.md. '
              'This configured PR event authorizes one bounded wiki update. Product root is ${{ github.workspace }}/product. '
              'Inspect primary specs, decisions and implementation evidence, preserving all source documents and unanswered questions. '
              'Maintain at most three factual wiki pages including quickstart. Use the product_context MCP lifecycle; '
              'write page Markdown only under product/openwiki, submit sparse Claims, finish cleanly, then inspect status and record the exact review snapshot with explicit questions. '
              'Do not change source policies, approvals or code. Do not run git, install tools, call another model, reset the wiki, or bypass failed completion. '
              'A turn/page limit is a failure to finish: report it rather than declaring current.')
    steps = [
        {'uses': CHECKOUT, 'with': {'path': 'product', 'ref': '${{ github.event.pull_request.head.sha }}', 'fetch-depth': 0, 'persist-credentials': False}},
        {'uses': CHECKOUT, 'with': {'repository': HARNESS, 'ref': ref, 'path': 'harness', 'persist-credentials': False}},
        {'uses': NODE, 'with': {'node-version': '22.22.0'}},
        {'name': 'Check primary evidence before model execution', 'id': 'preflight', 'run': f'python3 {tool} prepare --repo product --event "$GITHUB_EVENT_PATH" --state {state} --github-output "$GITHUB_OUTPUT"'},
        {'name': 'Require subscription OAuth', 'if': "steps.preflight.outputs.should_run == 'true'", 'env': {'CLAUDE_OAUTH_TOKEN': '${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}'},
         'run': 'if [ -z "$CLAUDE_OAUTH_TOKEN" ]; then echo "::error::Set repository secret CLAUDE_CODE_OAUTH_TOKEN using claude setup-token. No API fallback is configured."; exit 1; fi'},
        {'name': 'Install pinned model-free MCP', 'if': "steps.preflight.outputs.should_run == 'true'", 'working-directory': 'harness/skills/product-context/runtime', 'run': 'npm ci --ignore-scripts --no-audit --no-fund'},
        {'name': 'Update wiki with Claude subscription', 'id': 'writer', 'if': "steps.preflight.outputs.should_run == 'true'", 'uses': CLAUDE,
         'with': {'github_token': '${{ github.token }}', 'claude_code_oauth_token': '${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}',
                  'prompt': prompt, 'claude_args': '--max-turns 16 --permission-mode default --strict-mcp-config --tools Read,Glob,Grep,Write,Edit --mcp-config "${{ runner.temp }}/product-context-mcp.json" --settings "${{ runner.temp }}/product-context-settings.json"'}},
        {'name': 'Verify completion and publish document changes', 'if': "steps.preflight.outputs.should_run == 'true'", 'env': {'GH_TOKEN': '${{ github.token }}', 'PR_BRANCH': '${{ github.event.pull_request.head.ref }}'},
         'run': f'python3 {tool} verify --repo product --state {state} --commit\ngh auth setup-git\ngit -C product push origin "HEAD:refs/heads/$PR_BRANCH"'},
    ]
    return {'name': 'Product context wiki (Claude subscription)',
            'on': {'pull_request': {'types': ['opened', 'synchronize', 'reopened', 'ready_for_review'], 'paths-ignore': ['openwiki/**', '.product-context/review.json', '.product-context/wiki-review.json', '.openwikiignore']}},
            'permissions': {'contents': 'read', 'pull-requests': 'read'},
            'concurrency': {'group': 'product-context-${{ github.event.pull_request.number }}', 'cancel-in-progress': False},
            'jobs': {'wiki': {'if': "github.event.pull_request.head.repo.full_name == github.repository && !github.event.pull_request.draft && contains(fromJSON('[\"OWNER\",\"MEMBER\",\"COLLABORATOR\"]'), github.event.pull_request.author_association)",
                              'runs-on': 'ubuntu-latest', 'permissions': {'contents': 'write', 'pull-requests': 'read'}, 'steps': steps}}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    for name in ['install', 'prepare', 'verify']:
        sub = subs.add_parser(name)
        sub.add_argument('--repo', type=Path, required=True)
        if name == 'install':
            sub.add_argument('--runtime-ref', required=True, help='Full reviewed commit SHA of the trusted harness.')
            sub.add_argument('--write', action='store_true')
        else:
            sub.add_argument('--state', required=True)
        if name == 'prepare':
            sub.add_argument('--event', required=True)
            sub.add_argument('--github-output')
        if name == 'verify':
            sub.add_argument('--commit', action='store_true')
    args = parser.parse_args()
    root = args.repo.resolve()
    if run(['git', 'rev-parse', '--show-toplevel'], root).strip() != str(root):
        fail('INVALID_ROOT', 'Use the product Git top-level.')
    if args.command == 'install':
        if not re.fullmatch(r'[a-f0-9]{40}', args.runtime_ref):
            fail('UNPINNED_RUNTIME', 'Use a reviewed full 40-character commit SHA, not a branch or tag.')
        safe_destination(root / '.product-context.json')
        if not (root / '.product-context.json').is_file():
            fail('CONTEXT_REQUIRED', 'Initialize and review the product-context source profile first.')
        destination = root / WORKFLOW
        safe_destination(destination)
        content = workflow(args.runtime_ref)
        if destination.exists():
            try:
                previous = json.loads(destination.read_text())
            except ValueError:
                previous = None
            if previous != content:
                fail('WORKFLOW_EXISTS', 'The existing workflow was preserved; review it explicitly before migration.')
        if args.write and not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            write_json(destination, content)
        report = {'mode': 'install' if args.write else 'plan', 'workflow': WORKFLOW, 'runtime_ref': args.runtime_ref,
                  'required_secret': 'CLAUDE_CODE_OAUTH_TOKEN', 'model_calls': 0, 'api_fallback': False}
    elif args.command == 'prepare':
        report = prepare(root, args)
        write_outputs(args.github_output, report)
    else:
        report = verify(root, args)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (SetupError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}))
        raise SystemExit(2)
