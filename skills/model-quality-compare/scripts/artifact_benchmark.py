#!/usr/bin/env python3
"""Collect controlled coding/research artifacts using native subscription CLIs.

Task-specific executable checks and blinded structural review are separate from
collection. Freeze their grading specification before launch. No universal score.
"""
import argparse
import difflib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import claude_subscription as native_claude

from codex_benchmark import (classify, load_plan, now, sha, strict_json,
                             subscription_env, validate_manifest, write_json)

IGNORED = {'.git', '__pycache__', '.pytest_cache'}
INSTRUCTIONS = """You are completing a bounded coding or research evaluation.
Work only inside the supplied working directory. Read its task files, implement
the requested deliverables, and run local checks. Do not read outside the working
directory, access other contestants or graders, use network, install packages,
invoke another model, or use external services. Tools are for this task only.
Use Python's standard library. Stop when the requested artifacts and checks are
complete; aim for at most 12 shell commands. Report real blockers and test results.
The final chat message is not a substitute for files in the working directory.
"""


def files(root):
    result = {}
    for p in root.rglob('*'):
        if any(x in IGNORED for x in p.relative_to(root).parts):
            continue
        if p.is_symlink():
            raise ValueError(f'symlink artifact unsupported: {p.name}')
        if p.is_file():
            result[str(p.relative_to(root))] = sha(p)
    return result


def plan(args):
    starter = args.starter.resolve()
    if args.out == starter or args.out.is_relative_to(starter):
        raise ValueError('experiment must be outside the source starter directory')
    original = files(starter)
    if not original or len(args.models) < 2 or len(set(args.models)) != len(args.models):
        raise ValueError('non-empty starter and at least two distinct models required')
    if not 1 <= args.trials <= 3:
        raise ValueError('trials must be 1..3; budget additional trials explicitly')
    providers = native_claude.host_map(args.models, args.claude_models)
    strict_json(args.grading_spec.read_text())
    args.out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(starter, args.out / 'starter', ignore=shutil.ignore_patterns(*IGNORED))
    shutil.copyfile(args.prompt, args.out / 'prompt.txt')
    shutil.copyfile(args.grading_spec, args.out / 'grading-spec.json')
    (args.out / 'instructions.txt').write_text(INSTRUCTIONS)
    schedule = []
    for trial in range(1, args.trials + 1):
        for model in (args.models if trial % 2 else list(reversed(args.models))):
            schedule.append({'index': len(schedule) + 1, 'model': model, 'trial': trial})
    names = ['prompt.txt', 'instructions.txt', 'grading-spec.json'] + ['starter/' + p for p in original]
    data = {'schema': 1, 'route': 'artifact', 'created_utc': now(), 'models': args.models,
            'providers': providers, 'host_adapter_sha256': sha(Path(native_claude.__file__)),
            'trials': args.trials, 'effort': args.effort, 'schedule': schedule,
            'runner_sha256': sha(Path(__file__)),
            'helper_sha256': sha(Path(__file__).with_name('codex_benchmark.py')),
            'hashes': {p: sha(args.out / p) for p in names},
            'limitations': ['native Codex workspace-write sandbox; host isolation is not a container',
                            'task-specific objective checks and subjective rubric must be reported separately',
                            'model IDs requested; immutable backend snapshot not independently verified',
                            'CLI-launch budget is not a hard token/turn/time budget']}
    write_json(args.out / 'plan.json', data)
    (args.out / 'plan.sha256').write_text(sha(args.out / 'plan.json') + '\n')
    print(json.dumps({'calls': len(schedule), 'out': str(args.out), 'effort': args.effort}))


def command(args, design, workspace, answer, model):
    controls = {'forced_login_method': 'chatgpt', 'model_provider': 'openai',
                'model_reasoning_effort': design['effort'], 'approval_policy': 'never',
                'model_instructions_file': str(args.out / 'instructions.txt'),
                'project_doc_max_bytes': 0, 'skills.include_instructions': False,
                'features.omit_skill_descriptions': True, 'features.skip_host_skill_discovery': True,
                'features.shell_tool': True, 'features.apps': False, 'features.plugins': False,
                'features.remote_plugin': False, 'features.multi_agent': False,
                'features.multi_agent_v2': False, 'features.view_image': False,
                'features.image_generation': False, 'features.in_app_browser': False,
                'features.hooks': False, 'features.skill_search': False, 'features.memories': False,
                'web_search': 'disabled', 'sandbox_workspace_write.network_access': False}
    cmd = [args.codex, 'exec', '--ignore-user-config', '--ignore-rules', '--ephemeral',
           '--skip-git-repo-check', '--sandbox', 'workspace-write', '--cd', str(workspace),
           '--json', '--output-last-message', str(answer), '--model', model]
    for k, v in controls.items():
        cmd += ['-c', k + '=' + json.dumps(v)]
    return cmd + ['-']


def diff(starter, workspace):
    before, after = files(starter), files(workspace)
    lines = []
    for name in sorted(before.keys() | after.keys()):
        if before.get(name) == after.get(name):
            continue
        a, b = starter / name, workspace / name
        try:
            lines.extend(difflib.unified_diff(a.read_text().splitlines(True) if a.exists() else [],
                                            b.read_text().splitlines(True) if b.exists() else [],
                                            fromfile='before/' + name, tofile='after/' + name))
        except UnicodeError:
            lines.append('Binary changed: ' + name + '\n')
    return ''.join(lines)


def run(args):
    design = load_plan(args.out)
    expected_starter = {name.removeprefix('starter/'): digest for name, digest in design['hashes'].items()
                        if name.startswith('starter/')}
    if files(args.out / 'starter') != expected_starter:
        raise ValueError('starter file set changed after freeze')
    if design['runner_sha256'] != sha(Path(__file__)) or design['helper_sha256'] != sha(Path(__file__).with_name('codex_benchmark.py')):
        raise ValueError('runner changed after freeze')
    if design.get('host_adapter_sha256') and design['host_adapter_sha256'] != sha(Path(native_claude.__file__)):
        raise ValueError('host adapter changed after freeze')
    if len(design['schedule']) > args.max_calls:
        raise ValueError('experiment exceeds --max-calls; no calls made')
    lock = args.out / '.run-lock'
    lock.mkdir()
    try:
        env = subscription_env()
        hosts, version = native_claude.preflight(args, design, env)
        manifest = args.out / 'runs.json'
        data = strict_json(manifest.read_text()) if manifest.exists() else {
            'plan_sha256': sha(args.out / 'plan.json'), 'cli_version': version, 'hosts': hosts, 'runs': []}
        validate_manifest(data, design)
        if data['plan_sha256'] != sha(args.out / 'plan.json') or data['cli_version'] != version:
            raise ValueError('plan/CLI changed since previous attempts')
        recorded = {r['index'] for r in data['runs']}
        artifacts = list(args.out.glob('run-*.*')) + list((args.out / 'workspaces').glob('run-*'))
        for p in artifacts:
            index = int(p.name.split('.')[0].removeprefix('run-'))
            if index not in recorded:
                raise ValueError('orphan artifact: refusing quota spending or overwrite')
        for item in design['schedule']:
            if item['index'] in recorded:
                continue
            host = design.get('providers', {}).get(item['model'], 'codex')
            r = dict(item, status='started', started_utc=now(), host=host)
            data['runs'].append(r)
            write_json(manifest, data)  # reserve attempt before invoking a model
            name = f"run-{item['index']:02d}"
            workspace = args.out / 'workspaces' / name
            shutil.copytree(args.out / 'starter', workspace, ignore=shutil.ignore_patterns(*IGNORED))
            r['workspace'] = str(workspace.relative_to(args.out))
            r['starter_hashes'] = files(workspace)
            answer_path = args.out / (name + '.answer.txt')
            cmd = (native_claude.command(args.claude, item['model'], design['effort'],
                                         (args.out/'instructions.txt').read_text(), artifact=True) if host=='claude'
                   else command(args, design, workspace, answer_path, item['model']))
            r['command'] = cmd
            print(f"Starting {name}: {item['model']} ({design['effort']})", flush=True)
            start = time.perf_counter()
            events_path = args.out / (name + '.events.jsonl')
            with events_path.open('w') as stdout, (args.out / (name + '.stderr.txt')).open('w') as stderr:
                process = subprocess.run(cmd, env=env, cwd=workspace, input=(args.out / 'prompt.txt').read_text(),
                                         text=True, stdout=stdout, stderr=stderr)
            r.update(returncode=process.returncode, wall_seconds=round(time.perf_counter() - start, 3),
                     finished_utc=now(), events_sha256=sha(events_path))
            try:
                events = [strict_json(x) for x in events_path.read_text().splitlines() if x.strip()]
                if host == 'claude':
                    native_path = args.out / (name + '.native.jsonl')
                    events_path.rename(native_path)
                    events, answer, metadata = native_claude.normalize(events, item['model'], artifact=True,
                        expected_session=cmd[cmd.index('--session-id')+1])
                    answer_path.write_text(answer)
                    events_path.write_text(''.join(json.dumps(e, ensure_ascii=False)+'\n' for e in events))
                    r.update(metadata, native_events_file=native_path.name, native_events_sha256=sha(native_path),
                             events_sha256=sha(events_path))
                allowed = {'command_execution', 'file_change', 'plan_update'}
                filtered = [e for e in events if e.get('type') != 'item.completed'
                            or e.get('item', {}).get('type') not in allowed]
                r.update(classify(filtered, process.returncode))
                r['tool_events'] = [e['item'] for e in events if e.get('type') == 'item.completed'
                                    and e.get('item', {}).get('type') in allowed]
            except (ValueError, KeyError, TypeError) as exc:
                r.update(status='unavailable', error_detail='event parse error: ' + str(exc))
            r['artifacts'] = files(workspace)
            (args.out / (name + '.diff')).write_text(diff(args.out / 'starter', workspace))
            write_json(manifest, data)
            print(f"Finished {name}: {r['status']}, {r['wall_seconds']}s", flush=True)
    finally:
        lock.rmdir()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='action', required=True)
    c = commands.add_parser('plan')
    for name in ('out', 'starter', 'prompt', 'grading-spec'):
        c.add_argument('--' + name, type=Path, required=True)
    c.add_argument('--models', nargs='+', required=True)
    c.add_argument('--claude-models', nargs='*', default=[])
    c.add_argument('--effort', choices=['low', 'medium', 'high'], default='low')
    c.add_argument('--trials', type=int, default=1)
    c.set_defaults(func=plan)
    c = commands.add_parser('run')
    c.add_argument('--out', type=Path, required=True)
    c.add_argument('--codex', default='codex')
    c.add_argument('--claude', default='claude')
    c.add_argument('--max-calls', type=int, default=2)
    c.set_defaults(func=run)
    args = p.parse_args()
    args.out = args.out.resolve()
    try:
        args.func(args)
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
