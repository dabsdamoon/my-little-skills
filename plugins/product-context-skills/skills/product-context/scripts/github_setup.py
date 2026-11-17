"""GitHub transport and subscription-secret setup. Never read secret values."""
from __future__ import annotations

import base64
import getpass
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from urllib.parse import quote

from setup_subscription_wiki import SetupError

SECRET = 'CLAUDE_CODE_OAUTH_TOKEN'
REPOSITORY = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+')


class Unavailable(Exception):
    def __init__(self, status=None):
        self.status = status


def check(status, code, next_action=None, **details):
    return {'status': status, 'code': code, **({'next_action': next_action} if next_action else {}), **details}


def same_repository(first, second):
    return isinstance(first, str) and isinstance(second, str) and first.casefold() == second.casefold()


class GitHub:
    def __init__(self, repository):
        if not REPOSITORY.fullmatch(repository):
            raise SetupError('INVALID_REPOSITORY: Use an explicit GitHub OWNER/REPO.')
        self.repository = repository.lower()

    def request(self, endpoint):
        try:
            result = subprocess.run(['gh', 'api', endpoint], capture_output=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            raise Unavailable() from None
        if result.returncode:
            match = re.search(rb'HTTP (\d{3})', result.stderr)
            raise Unavailable(int(match[1]) if match else None)
        if len(result.stdout) > 4 * 1024 * 1024:
            raise Unavailable()
        return result.stdout

    def api(self, endpoint):
        try:
            return json.loads(self.request(endpoint))
        except (ValueError, UnicodeError):
            raise Unavailable() from None

    def items(self, endpoint, key):
        found = []
        for page in range(1, 21):
            data = self.api(endpoint + ('&' if '?' in endpoint else '?') + f'per_page=100&page={page}')
            values = data.get(key)
            if not isinstance(values, list):
                raise Unavailable()
            found.extend(values)
            if len(values) < 100:
                return found
        raise Unavailable()

    def content(self, path, ref):
        data = self.api(f'repos/{self.repository}/contents/{quote(path, safe="/")}?ref={quote(ref, safe="")}')
        if data.get('type') != 'file' or data.get('encoding') != 'base64':
            raise Unavailable()
        try:
            return base64.b64decode(data['content'], validate=False)
        except (ValueError, KeyError, TypeError):
            raise Unavailable() from None

    def oauth(self):
        uncertain = False
        for source, suffix in (('repository', 'secrets'), ('organization', 'organization-secrets')):
            try:
                if any(value.get('name') == SECRET for value in self.items(f'repos/{self.repository}/actions/{suffix}', 'secrets')):
                    return check('configured', 'OAUTH_CONFIGURED', authentication='unverified', source=source)
            except Unavailable:
                if source == 'organization':
                    try:
                        if self.api(f'repos/{self.repository}').get('owner', {}).get('type') == 'User':
                            continue
                    except Unavailable:
                        pass
                uncertain = True
        if uncertain:
            return check('unknown', 'OAUTH_UNVERIFIABLE', 'Restore GitHub Actions secret-list permissions; do not replace an uninspectable secret.')
        return check('missing', 'OAUTH_MISSING', 'Run product_setup.py oauth for this repository after claude setup-token; subscription OAuth is required, not an API key.')

    def register_oauth(self, token_stdin=False, replace=False):
        existing = self.oauth()
        if existing['status'] != 'missing' and not (replace and existing['status'] == 'configured'):
            return existing
        if token_stdin:
            if sys.stdin.isatty():
                return check('incomplete', 'INTERACTIVE_LOGIN_REQUIRED', 'Issue a subscription token with claude setup-token; use oauth without --token-stdin for hidden input.')
            token = sys.stdin.read(4097).strip()
        elif sys.stdin.isatty():
            token = getpass.getpass('New Claude subscription OAuth token (hidden; use claude setup-token): ').strip()
        else:
            return check('incomplete', 'INTERACTIVE_LOGIN_REQUIRED', 'Run claude setup-token interactively, then product_setup.py oauth in a terminal; do not paste credentials into chat.')
        if len(token) > 4096 or not re.fullmatch(r'sk-ant-oat01-[A-Za-z0-9_-]+', token):
            raise SetupError('SUBSCRIPTION_TOKEN_REQUIRED: Supply a newly issued Claude subscription OAuth token through hidden input or stdin, never an API key.')
        try:
            result = subprocess.run(['gh', 'secret', 'set', SECRET, '--repo', self.repository, '--app', 'actions'], input=token+'\n', capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            raise SetupError('OAUTH_REGISTRATION_FAILED: Secret registration failed; credential output was suppressed.') from None
        finally:
            token = None
        if result.returncode:
            raise SetupError('OAUTH_REGISTRATION_FAILED: GitHub rejected secret registration; credential output was suppressed.')
        result = None
        return self.oauth()


def repository_for(root: Path, requested):
    result = subprocess.run(['git', '-C', str(root), 'remote', 'get-url', 'origin'], capture_output=True, text=True)
    remote = result.stdout.strip().removesuffix('.git')
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)', remote)
    if not match:
        raise SetupError('REPOSITORY_REQUIRED: Use a product with a canonical GitHub origin remote.')
    repository = match[1]
    if requested and requested.lower() != repository.lower():
        raise SetupError('REPOSITORY_MISMATCH: The explicit GitHub repository does not match this product origin; no writes were performed.')
    return repository.lower()


def verify_publication(github, number):
    """Trust a successful known workflow plus its exact-head publication evidence."""
    from pr_wiki import BOTS, WORKFLOW, workflow
    from setup_subscription_wiki import VERSION

    if number < 1:
        raise SetupError('INVALID_PR: Use a positive PR number.')
    try:
        pr = github.api(f'repos/{github.repository}/pulls/{number}')
        if (not same_repository(pr.get('head', {}).get('repo', {}).get('full_name'), github.repository)
                or (pr.get('author_association') not in {'OWNER', 'MEMBER', 'COLLABORATOR'} and pr.get('user', {}).get('login') not in BOTS)):
            return check('excluded', 'UNTRUSTED_PR', 'Forks and untrusted PR authors cannot receive subscription credentials.')
        if pr.get('draft'):
            return check('excluded', 'DRAFT_PR', 'Mark the PR ready for review to enable its configured workflow.')
        branch = quote(pr['head']['ref'], safe='')
        runs = github.items(f'repos/{github.repository}/actions/workflows/product-context-wiki.yml/runs?event=pull_request&branch={branch}', 'workflow_runs')
        for run in runs[:20]:
            if (run.get('status') == 'completed' and run.get('conclusion') == 'failure'
                    and run.get('event') == 'pull_request' and run.get('head_sha') == pr['head']['sha']):
                from pr_wiki import workflow_revision
                known = workflow_revision(json.loads(github.content(WORKFLOW, run['head_sha'])))
                if known:
                    jobs = github.items(f'repos/{github.repository}/actions/runs/{run["id"]}/jobs', 'jobs')
                    for job in jobs:
                        if (job.get('name') != 'wiki' or not job.get('id')
                                or not any(s.get('name') == 'Update wiki with Claude subscription' and s.get('conclusion') == 'failure' for s in job.get('steps', []))):
                            continue
                        # Inspect bounded transport data in memory; return a fixed
                        # code only, never a log line or credential-containing error.
                        log = github.request(f'repos/{github.repository}/actions/jobs/{job["id"]}/logs')
                        provider_error = rb'(?m)^(?:\d{4}-\d{2}-\d{2}T[\d:.]+Z[ \t]+)?(?:##\[error\])?(?:Error:[ \t]*)?API Error:[ \t]*401\b[^\r\n]{0,2000}(?:authentication_error|OAuth token[^\r\n]{0,100}(?:expired|invalid|revoked)|Invalid authentication credentials)'
                        if re.search(provider_error, log, re.I):
                            return check('failed', 'OAUTH_AUTHENTICATION_FAILED', 'Issue a new subscription token with claude setup-token, then explicitly run product_setup.py oauth --replace for this repository; existing secrets are preserved until requested.', run_url=run['html_url'], base_branch=pr['base']['ref'])
            if run.get('status') != 'completed' or run.get('conclusion') != 'success' or run.get('event') != 'pull_request':
                continue
            run_id = run['id']
            jobs = github.items(f'repos/{github.repository}/actions/runs/{run_id}/jobs', 'jobs')
            required = {'Update wiki with Claude subscription', 'Verify completion and publish document changes', 'Upload verified publication receipt'}
            if not any(job.get('name') == 'wiki' and job.get('conclusion') == 'success' and required <= {s.get('name') for s in job.get('steps', []) if s.get('conclusion') == 'success'} for job in jobs):
                continue
            artifacts = github.items(f'repos/{github.repository}/actions/runs/{run_id}/artifacts', 'artifacts')
            artifact = next((a for a in artifacts if a.get('name') == f'product-context-publication-{number}' and not a.get('expired')), None)
            if not artifact:
                continue
            try:
                with zipfile.ZipFile(io.BytesIO(github.request(f'repos/{github.repository}/actions/artifacts/{artifact["id"]}/zip'))) as archive:
                    entry = archive.getinfo('product-context-publication.json')
                    if entry.file_size > 16384 or len(archive.infolist()) != 1:
                        continue
                    proof = json.loads(archive.read(entry))
            except (ValueError, KeyError, zipfile.BadZipFile):
                continue
            if (proof.get('schema_version') != 1 or not same_repository(proof.get('repository'), github.repository)
                    or proof.get('pr_number') != number or proof.get('run_id') != run_id
                    or proof.get('source_head') != run.get('head_sha') or proof.get('published_commit') != pr['head']['sha']
                    or not re.fullmatch(r'[a-f0-9]{64}', proof.get('snapshot', ''))):
                continue
            generated = json.loads(github.content(WORKFLOW, proof['source_head']))
            pin = re.search(r'fetch --depth 1 origin ([a-f0-9]{40})', json.dumps(generated))
            if not pin or generated != workflow(pin[1]):
                continue
            package = json.loads(GitHub('dabsdamoon/my-little-skills').content('skills/product-context/runtime/package.json', pin[1]))
            if package.get('version') != VERSION:
                continue
            valid = True
            for path, digest in (('.product-context/wiki-review.json', 'wiki_receipt_sha256'), ('.product-context/review.json', 'review_receipt_sha256')):
                raw = github.content(path, proof['published_commit'])
                receipt = json.loads(raw)
                if hashlib.sha256(raw).hexdigest() != proof.get(digest) or receipt.get('snapshot') != proof['snapshot']:
                    valid = False
                if path.endswith('/review.json') and receipt.get('git_head') != proof['source_head']:
                    valid = False
            if valid:
                return check('verified', 'PR_PUBLICATION_VERIFIED', run_url=run['html_url'], source_head=proof['source_head'], published_commit=proof['published_commit'], snapshot=proof['snapshot'], base_branch=pr['base']['ref'])
        return check('unverified', 'PR_PUBLICATION_UNVERIFIED', 'Inspect the eligible PR workflow. A successful non-skipped writer, pushed current head, and matching publication artifact/receipts are required.', base_branch=pr['base']['ref'])
    except Unavailable:
        return check('unknown', 'PR_EVIDENCE_UNVERIFIABLE', 'Restore access to PR runs, artifacts and published repository content.')
    except (ValueError, KeyError, TypeError, AttributeError):
        return check('unverified', 'PR_EVIDENCE_INVALID', 'Inspect malformed or incomplete publication evidence; no success was inferred.')
