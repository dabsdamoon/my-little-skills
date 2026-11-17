#!/usr/bin/env python3
"""Product-aware subscription wiki setup and read-only readiness diagnosis."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

from context_core import ContextError, load_config
from github_setup import GitHub, Unavailable, check, repository_for, same_repository
from product_context import inspect
from pr_wiki import HARNESS, WORKFLOW, read_optional, require_publishable, workflow_revision
from setup_subscription_wiki import NAME, SKILL, VERSION, SetupError, files, inspect_registration, safe_destination, write_json

OPT_IN = '.product-context/automation.json'


def command(args, timeout=60):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        raise SetupError('COMMAND_UNAVAILABLE: A required tool could not run; no API fallback was attempted.') from None
    if result.returncode:
        raise SetupError('COMMAND_FAILED: A setup step failed; no credentials or raw command output were printed.')
    return result.stdout


def local_state(args):
    target = args.install_root.expanduser().absolute()
    server = target/'runtime/server.mjs'
    hosts = ('claude', 'codex') if args.host == 'both' else (args.host,)
    values = {}
    for host in hosts:
        checks = {}
        try:
            code = "const {subscription}=await import(process.argv[1]);console.log(JSON.stringify(subscription(process.argv[2])));"
            command(['node', '--input-type=module', '-e', code, (SKILL/'runtime/guard.mjs').as_uri(), host])
            checks['authentication'] = check('ready', 'LOCAL_SUBSCRIPTION_READY')
        except SetupError:
            checks['authentication'] = check('incomplete', 'LOCAL_AUTH_FAILED', f'Sign in to {host} with its subscription; API keys are not a fallback.')
        if not server.is_file() or not (target/'.installed.json').is_file():
            values[host] = check('missing', 'LOCAL_RUNTIME_MISSING', 'Run product_setup.py setup --write for the selected host.', checks=checks)
            continue
        try:
            safe_destination(target)
            receipt = json.loads((target/'.installed.json').read_text())
            if receipt.get('owner') != NAME or receipt.get('version') != VERSION:
                values[host] = check('incomplete', 'LOCAL_RUNTIME_OUTDATED', 'Install the current managed runtime version.', checks=checks)
                continue
            expected = files()
            if receipt.get('files') != expected:
                raise SetupError('LOCAL_RUNTIME_CHANGED: Managed runtime files differ from this release.')
            import hashlib
            for relative, digest in expected.items():
                installed = target/relative
                safe_destination(installed)
                if hashlib.sha256(installed.read_bytes()).hexdigest() != digest:
                    raise SetupError('LOCAL_RUNTIME_CHANGED: Managed runtime files changed.')
            if not (target/'runtime/node_modules/openwiki/package.json').is_file():
                raise SetupError('LOCAL_DEPENDENCIES_MISSING: Reinstall the managed dependencies.')
            version = command(['node', '--version']).strip().removeprefix('v').split('.')
            if tuple(map(int, version[:2])) < (22, 22):
                values[host] = check('incomplete', 'LOCAL_NODE_UNSUPPORTED', 'Use Node.js 22.22 or newer.', checks=checks)
                continue
            verified = json.loads(command(['node', str(server), '--host', host, '--self-check']))
            if not verified.get('ok') or verified.get('version') != VERSION:
                raise SetupError('LOCAL_RUNTIME_INVALID: The model-free runtime check failed.')
            checks['runtime'] = check('ready', 'LOCAL_RUNTIME_READY')
            registry = target.parent/'registrations.json'
            safe_destination(registry)
            owned = json.loads(registry.read_text()) if registry.exists() else {}
            if not inspect_registration(host, owned, server):
                values[host] = check('missing', 'LOCAL_REGISTRATION_MISSING', 'Run product_setup.py setup --write to register this host.', checks=checks)
                continue
            checks['registration'] = check('ready', 'LOCAL_REGISTRATION_READY')
            values[host] = check('ready', 'LOCAL_READY', authentication='subscription', runtime=str(target), checks=checks) if checks['authentication']['status'] == 'ready' else check('incomplete', 'LOCAL_AUTH_FAILED', checks=checks)
        except (SetupError, OSError, ValueError):
            values[host] = check('incomplete', 'LOCAL_RUNTIME_OR_REGISTRATION_FAILED', 'Repair the managed runtime or host registration; existing files were preserved.', checks=checks)
    return {'status': 'ready' if all(v['status'] == 'ready' for v in values.values()) else 'incomplete', 'hosts': values}


def profile_state(root):
    try:
        if read_optional(root/'.product-context.json') is None:
            return check('missing', 'PROFILE_MISSING', 'Use setup --profile REVIEWED_PROFILE --write, or initialize and review the product source profile.')
        report = inspect(root, load_config(root))
        if report['missing_sources'] or report['broken_links'] or any(p.startswith('openwiki/') for p in report['files']):
            return check('incomplete', 'PROFILE_FINDINGS', 'Repair source selection and local links; generated wiki pages cannot be primary sources.')
        require_publishable(root)
        return check('ready', 'PROFILE_READY', snapshot=report['snapshot'], source_count=len(report['files']))
    except (ContextError, SetupError, ValueError, OSError):
        return check('incomplete', 'PROFILE_INVALID', 'Review the source profile, managed paths, and generated-output ignore rules.')


def workflow_state(root):
    try:
        text = read_optional(root/WORKFLOW)
        if text is None:
            return check('missing', 'WORKFLOW_MISSING', 'Run setup --runtime-ref REVIEWED_FULL_SHA --write.')
        value = json.loads(text)
        # Only a known generated workflow can establish automated credential use.
        revision = workflow_revision(value)
        if not revision:
            return check('unknown', 'WORKFLOW_UNREVIEWED', 'Review the existing workflow explicitly; setup preserves custom workflows.')
        if revision['revision'] == 'legacy':
            return check('incomplete', 'WORKFLOW_LEGACY', 'Review setup --upgrade-workflow to add publication proof to the known previous workflow.', runtime_ref=revision['runtime_ref'])
        return check('ready', 'WORKFLOW_READY', runtime_ref=revision['runtime_ref'], base_branches='all', events=value['on']['pull_request']['types'])
    except (SetupError, ValueError, TypeError, OSError):
        return check('unknown', 'WORKFLOW_UNREVIEWED', 'Review the existing workflow and managed paths; no file was replaced.')


def cloud_state(root, github, local_workflow, base):
    values = {'profile': profile_state(root), 'workflow': local_workflow, 'oauth': github.oauth()}
    if local_workflow['status'] == 'ready':
        pin = local_workflow['runtime_ref']
        try:
            harness = GitHub(HARNESS)
            package = json.loads(harness.content('skills/product-context/runtime/package.json', pin))
            values['runtime_pin'] = check('ready', 'RUNTIME_PIN_READY', runtime_ref=pin) if package.get('version') == VERSION else check('incomplete', 'RUNTIME_PIN_OUTDATED', 'Review and pin a commit containing this released runtime version.')
        except (Unavailable, ValueError):
            values['runtime_pin'] = check('unknown', 'RUNTIME_PIN_UNVERIFIABLE', 'Check access to the pinned harness commit.')
    else:
        values['runtime_pin'] = check('incomplete', 'RUNTIME_PIN_REQUIRED', 'Install a reviewed pinned workflow.')
    try:
        default = github.api(f'repos/{github.repository}')['default_branch']
        ref = base or default
        matches = all(json.loads(github.content(path, ref)) == json.loads((root/path).read_bytes()) for path in ('.product-context.json', WORKFLOW))
        values['published'] = check('ready', 'CONFIG_PUBLISHED', ref=ref) if matches else check('incomplete', 'CONFIG_NOT_PUBLISHED', 'Commit and publish the reviewed profile and workflow; local files alone are not cloud configuration.', ref=ref)
    except Unavailable as error:
        values['published'] = check('incomplete' if error.status == 404 else 'unknown', 'CONFIG_NOT_PUBLISHED' if error.status == 404 else 'CONFIG_UNVERIFIABLE', 'Publish the product profile/workflow or restore repository inspection access.')
    except (KeyError, OSError, TypeError, ValueError):
        values['published'] = check('incomplete', 'CONFIG_NOT_PUBLISHED', 'Publish the product profile and workflow.')
    return {'status': 'ready' if all(v['status'] in {'ready', 'configured'} for v in values.values()) else 'incomplete', 'checks': values}


def doctor(root, args, github):
    local = local_state(args)
    view = workflow_state(root)
    pr = None
    if args.pr:
        try:
            pr = github.api(f'repos/{github.repository}/pulls/{args.pr}')
        except Unavailable:
            pass
    ref = args.ref or (pr.get('head', {}).get('sha') if pr else None)
    automation = cloud_state(root, github, view, ref)
    eligibility = event_eligibility(github, pr) if pr else check('unchecked', 'PR_REQUIRED', 'Supply --pr NUMBER to inspect the actual base branch and trigger.')
    verification = check('unverified', 'PR_EVIDENCE_REQUIRED', 'Supply --pr NUMBER after a real eligible PR run; local tests and skipped writers do not verify publication.')
    if args.pr:
        from github_setup import verify_publication
        verification = eligibility if eligibility['status'] == 'excluded' else verify_publication(github, args.pr)
        if verification['code'] == 'OAUTH_AUTHENTICATION_FAILED':
            automation['checks']['oauth'] = {**verification, 'authentication': 'rejected'}
            automation['status'] = 'incomplete'
    actions = [v['next_action'] for v in [*local['hosts'].values(), *automation['checks'].values(), verification] if v.get('next_action')]
    return {'schema_version': 1, 'repository': github.repository, 'local': local, 'automation': automation, 'eligibility': eligibility, 'verification': verification,
            'ready': local['status'] == automation['status'] == 'ready',
            'complete': local['status'] == automation['status'] == 'ready' and verification['status'] == 'verified',
            'next_actions': list(dict.fromkeys(actions)), 'model_calls': 0, 'provider_execution': False, 'api_fallback': False}


def event_eligibility(github, pr):
    base = pr.get('base', {}).get('ref')
    if not same_repository(pr.get('head', {}).get('repo', {}).get('full_name'), github.repository):
        return check('excluded', 'UNTRUSTED_PR', base_branch=base)
    if pr.get('draft'):
        return check('excluded', 'DRAFT_PR', base_branch=base)
    try:
        value = json.loads(github.content(WORKFLOW, pr['head']['sha']))
        trigger = value.get('on', {}).get('pull_request')
        if trigger is None:
            return check('excluded', 'PR_TRIGGER_MISSING', base_branch=base)
        if not isinstance(trigger, dict):
            return check('unknown', 'PR_TRIGGER_UNVERIFIABLE', base_branch=base)
        # Exact branch lists are unambiguous. Complex GitHub glob expressions
        # require review rather than approximating their semantics with fnmatch.
        included, excluded = trigger.get('branches'), trigger.get('branches-ignore', [])
        patterns = (included or []) + excluded
        if any(not isinstance(p, str) or re.search(r'[!*?+\[\]{}]', p) for p in patterns):
            return check('unknown', 'BASE_BRANCH_FILTER_UNVERIFIABLE', 'Review the workflow branch patterns against this PR base.', base_branch=base)
        if (included is not None and base not in included) or base in excluded:
            return check('excluded', 'BASE_BRANCH_EXCLUDED', base_branch=base)
        return check('eligible', 'BASE_BRANCH_ALLOWED', base_branch=base, events=trigger.get('types', 'default'))
    except (Unavailable, ValueError, KeyError, TypeError):
        return check('unknown', 'PR_TRIGGER_UNVERIFIABLE', 'Inspect the workflow at this PR head.', base_branch=base)


def setup(root, args):
    if not re.fullmatch(r'[a-f0-9]{40}', args.runtime_ref or ''):
        raise SetupError('UNPINNED_RUNTIME: Supply a reviewed full 40-character harness commit SHA.')
    if not args.write:
        return
    # Inspect both product destinations before changing local registration or files.
    for relative in ('.product-context.json', WORKFLOW, OPT_IN):
        safe_destination(root/relative)
    existing = workflow_state(root)
    if existing['status'] not in {'ready', 'missing'} and not (existing['code'] == 'WORKFLOW_LEGACY' and args.upgrade_workflow):
        return
    if existing['status'] == 'ready' and existing['runtime_ref'] != args.runtime_ref and not args.upgrade_workflow:
        raise SetupError('WORKFLOW_EXISTS: The existing pin was preserved; explicitly review a workflow upgrade.')
    receipt = {'schema_version': 1, 'repository': repository_for(root, args.github_repo), 'mode': 'pull_request', 'runtime_ref': args.runtime_ref}
    previous = read_optional(root/OPT_IN)
    if previous is not None and json.loads(previous) != receipt:
        prior = json.loads(previous)
        if not (args.upgrade_workflow and set(prior) == set(receipt) and all(prior[k] == receipt[k] for k in ('schema_version', 'repository', 'mode'))):
            raise SetupError('SETUP_EXISTS: Existing product opt-in was preserved; review it before migration.')
    require_publishable(root)
    try:
        package = json.loads(GitHub(HARNESS).content('skills/product-context/runtime/package.json', args.runtime_ref))
    except (Unavailable, ValueError):
        raise SetupError('RUNTIME_PIN_UNVERIFIABLE: Check access to the reviewed harness commit before installation.') from None
    if package.get('version') != VERSION:
        raise SetupError('RUNTIME_PIN_OUTDATED: The reviewed harness pin must contain this runtime version.')
    if (root/'.product-context.json').exists() and profile_state(root)['status'] != 'ready':
        raise SetupError('PROFILE_FINDINGS: Repair the existing source profile before installing product automation.')
    if not (root/'.product-context.json').exists():
        if not args.profile:
            raise SetupError('PROFILE_REVIEW_REQUIRED: Supply a reviewed product source profile with --profile before setup writes.')
        profile = load_config(root, args.profile)
        findings = inspect(root, profile)
        if findings['missing_sources'] or findings['broken_links'] or any(p.startswith('openwiki/') for p in findings['files']):
            raise SetupError('PROFILE_FINDINGS: Repair the reviewed profile before installing product automation.')
        write_json(root/'.product-context.json', profile)
    if not args.skip_local:
        command(['python3', str(SKILL/'scripts/setup_subscription_wiki.py'), '--host', args.host, '--install-root', str(args.install_root), '--install', '--json'], timeout=None)
    command(['python3', str(SKILL/'scripts/pr_wiki.py'), 'install', '--repo', str(root), '--runtime-ref', args.runtime_ref, '--write', *(['--upgrade'] if args.upgrade_workflow else [])])
    if previous is None or args.upgrade_workflow:
        (root/OPT_IN).parent.mkdir(exist_ok=True)
        write_json(root/OPT_IN, receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['doctor', 'setup', 'oauth'])
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--github-repo')
    parser.add_argument('--host', choices=['claude', 'codex', 'both'], default='both')
    parser.add_argument('--install-root', type=Path, default=Path.home()/'.local/share/product-context'/VERSION)
    parser.add_argument('--runtime-ref')
    parser.add_argument('--profile', type=Path)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--skip-local', action='store_true', help='Cloud-only setup; still reports local installation separately.')
    parser.add_argument('--upgrade-workflow', action='store_true', help='Explicitly upgrade only a recognized generated workflow and its product opt-in pin.')
    parser.add_argument('--ref', help='Inspect published configuration at this commit/ref, defaulting to the repository default branch.')
    parser.add_argument('--pr', type=int)
    parser.add_argument('--token-stdin', action='store_true', help='Explicit newly issued subscription token input; never read existing login credentials.')
    parser.add_argument('--replace', action='store_true', help='Explicitly rotate an inspectable existing Actions OAuth secret using a newly issued subscription token.')
    parser.add_argument('--json', action='store_true', help='Reports are always JSON.')
    args = parser.parse_args()
    root = args.repo.expanduser().resolve()
    if command(['git', '-C', str(root), 'rev-parse', '--show-toplevel']).strip() != str(root):
        raise SetupError('INVALID_ROOT: Use the product Git top-level.')
    github = GitHub(repository_for(root, args.github_repo))
    if args.command == 'oauth':
        oauth = github.register_oauth(args.token_stdin, args.replace)
        report = {'repository': github.repository, 'oauth': oauth, 'model_calls': 0, 'api_fallback': False}
        code = 0 if oauth['status'] == 'configured' else 1
    else:
        if args.command == 'setup':
            setup(root, args)
        report = doctor(root, args, github)
        report['mode'] = 'write' if args.command == 'setup' and args.write else 'diagnose'
        code = 0 if report['ready'] else 1
    print(json.dumps(report, ensure_ascii=False))
    return code


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (SetupError, ContextError) as error:
        code, _, message = str(error).partition(': ')
        if isinstance(error, ContextError):
            code, message = error.code, str(error)
        print(json.dumps({'error': {'code': code, 'message': message}, 'model_calls': 0}))
        raise SystemExit(2)
    except (OSError, ValueError, TypeError, KeyError):
        print(json.dumps({'error': {'code': 'SETUP_INSPECTION_FAILED', 'message': 'Inspect product configuration and tool availability; raw output was suppressed.'}, 'model_calls': 0}))
        raise SystemExit(2)
