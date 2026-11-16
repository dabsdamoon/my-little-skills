import { lstat, mkdir, open, readFile, readdir, realpath, rename, unlink, writeFile } from 'node:fs/promises';
import { createHash, randomUUID } from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const skill = fileURLToPath(new URL('../', import.meta.url));
const marker = '# product-context subscription bridge: temporary workflow suppression\n';
const receiptName = '.product-context/wiki-review.json';
const hash = value => createHash('sha256').update(value).digest('hex');
export function fail(code, message) { throw new Error(`${code}: ${message}`); }
export async function exists(file) { try { await lstat(file); return true; } catch (error) { if (error.code === 'ENOENT') return false; throw error; } }

export async function safe(root, relative) {
  const parts = relative.split('/');
  if (path.isAbsolute(relative) || parts.some(part => !part || part === '..' || part === '.')) fail('UNSAFE_PATH', 'Expected a product-relative path.');
  let current = root;
  for (const part of parts) {
    current = path.join(current, part);
    if (await exists(current)) {
      const stat = await lstat(current);
      if (stat.isSymbolicLink()) fail('UNSAFE_PATH', `Symlinked managed path: ${relative}`);
      if (current !== path.join(root, relative) && !stat.isDirectory()) fail('UNSAFE_PATH', `Non-directory parent: ${relative}`);
    }
  }
  return current;
}

export async function rootPath(value) {
  if (!path.isAbsolute(value)) fail('INVALID_ROOT', 'Use the absolute Git top-level.');
  const root = await realpath(value);
  let top;
  try { top = execFileSync('git', ['-C', root, 'rev-parse', '--show-toplevel'], { encoding: 'utf8', timeout: 10000, stdio: ['ignore', 'pipe', 'pipe'] }).trim(); }
  catch { fail('INVALID_ROOT', 'The product must be a Git repository.'); }
  if (await realpath(top) !== root) fail('INVALID_ROOT', 'Use the Git top-level, not a subdirectory.');
  return root;
}

export function subscription(host) {
  const keys = host === 'codex' ? ['OPENAI_API_KEY', 'CODEX_API_KEY'] : ['ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN'];
  if (keys.some(key => process.env[key])) fail('SUBSCRIPTION_REQUIRED', 'API-key authentication is present; use a subscription-authenticated host.');
  try {
    if (host === 'codex') {
      const result = spawnSync('codex', ['login', 'status'], { encoding: 'utf8', timeout: 15000, stdio: ['ignore', 'pipe', 'pipe'] });
      const output = `${result.stdout ?? ''}\n${result.stderr ?? ''}`;
      if (result.status === 0 && /ChatGPT/i.test(output) && !/API key/i.test(output)) return { host, authentication: 'subscription' };
      fail('SUBSCRIPTION_REQUIRED', 'Codex must be signed in with ChatGPT.');
    }
    const output = JSON.parse(execFileSync('claude', ['auth', 'status', '--json'], { encoding: 'utf8', timeout: 15000, stdio: ['ignore', 'pipe', 'pipe'] }));
    if (output.loggedIn && output.authMethod === 'claude.ai' && output.apiProvider === 'firstParty') return { host, authentication: 'subscription' };
  } catch (error) {
    if (error.message?.startsWith('SUBSCRIPTION_REQUIRED:')) throw error;
  }
  fail('SUBSCRIPTION_REQUIRED', `Sign in to ${host} with your subscription; no API fallback is configured.`);
}

export async function context(root) {
  await safe(root, '.product-context.json');
  await safe(root, '.product-context');
  let output;
  try { output = execFileSync('python3', ['-B', path.join(skill, 'scripts/product_context.py'), 'check', '--repo', root, '--json'], { encoding: 'utf8', timeout: 15000, stdio: ['ignore', 'pipe', 'pipe'] }); }
  catch (error) { if (error.status === 1) output = error.stdout; else fail('CONTEXT_REQUIRED', 'Initialize product-context and repair invalid configuration/state before wiki generation.'); }
  return JSON.parse(output);
}

export async function noWorkflow(root) {
  const file = await safe(root, '.github/workflows/openwiki-update.yml');
  if (await exists(file)) fail('EXISTING_WORKFLOW', 'Review and remove or quarantine the existing openwiki-update.yml explicitly; it was left unchanged.');
}

export async function lock(root) {
  const directory = await safe(root, '.product-context');
  await mkdir(directory, { recursive: true });
  const file = await safe(root, '.product-context/wiki.lock');
  const token = randomUUID();
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const handle = await open(file, 'wx', 0o600);
      await handle.writeFile(JSON.stringify({ pid: process.pid, token }));
      await handle.close();
      const release = async () => {
        try { if (JSON.parse(await readFile(file, 'utf8')).token === token) await unlink(file); }
        catch (error) { if (error.code !== 'ENOENT') throw error; }
      };
      release.owns = async () => {
        try { return JSON.parse(await readFile(file, 'utf8')).token === token; }
        catch (error) { if (error.code === 'ENOENT') return false; throw error; }
      };
      return release;
    } catch (error) {
      if (error.code !== 'EEXIST') throw error;
      let previous;
      try { previous = JSON.parse(await readFile(file, 'utf8')); } catch { fail('LOCKED', 'Inspect the existing wiki.lock before retrying.'); }
      if (!Number.isInteger(previous.pid) || previous.pid <= 0) fail('LOCKED', 'Inspect the existing wiki.lock before retrying.');
      try { process.kill(previous.pid, 0); fail('LOCKED', 'Another subscription wiki process owns this product.'); }
      catch (alive) { if (alive.code !== 'ESRCH') throw alive; }
      await unlink(file);
    }
  }
  fail('LOCKED', 'The product wiki is busy.');
}

export async function beginGuard(root, task) {
  for (const file of ['openwiki', 'AGENTS.md', 'CLAUDE.md', '.openwikiignore', '.product-context']) await safe(root, file);
  const workflow = await safe(root, '.github/workflows/openwiki-update.yml');
  // A crashed bridge can leave only this inert marker. A custom file is never replaced.
  if (await exists(workflow)) {
    if (await readFile(workflow, 'utf8') === marker) await unlink(workflow);
    else await noWorkflow(root);
  }
  const ignore = path.join(root, '.openwikiignore');
  let rules = await exists(ignore) ? await readFile(ignore, 'utf8') : '';
  for (const rule of ['.product-context/', '.product-context.json', '.github/workflows/openwiki-update.yml']) {
    if (!rules.split(/\r?\n/).includes(rule)) rules += `${rules.endsWith('\n') || !rules ? '' : '\n'}${rule}\n`;
  }
  await writeFile(ignore, rules);
  await mkdir(path.dirname(workflow), { recursive: true });
  const handle = await open(workflow, 'wx', 0o600);
  await handle.writeFile(marker);
  await handle.close();
  try { return await task(); }
  finally {
    if (await exists(workflow)) {
      if (await readFile(workflow, 'utf8') === marker) await unlink(workflow);
      else fail('WORKFLOW_CHANGED', 'The reserved workflow changed during generation; it was preserved.');
    }
  }
}

export async function digestWiki(root) {
  const wiki = await safe(root, 'openwiki');
  if (!await exists(wiki)) return null;
  const files = [];
  async function collect(directory, prefix) {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const relative = `${prefix}/${entry.name}`;
      if (entry.isSymbolicLink()) fail('UNSAFE_PATH', 'Generated wiki paths must not be symlinks.');
      if (entry.isDirectory()) await collect(path.join(directory, entry.name), relative);
      else if (entry.name.endsWith('.md') || (entry.name.endsWith('.json') && entry.name !== '.run.json')) {
        files.push([relative, hash(await readFile(path.join(directory, entry.name)))]);
      }
    }
  }
  await collect(wiki, 'openwiki');
  return hash(JSON.stringify(files.sort((a, b) => a[0].localeCompare(b[0]))));
}

export async function readJson(root, relative) {
  const file = await safe(root, relative);
  if (!await exists(file)) return null;
  try { return JSON.parse(await readFile(file, 'utf8')); }
  catch { fail('INVALID_STATE', `Invalid JSON in ${relative}`); }
}

export async function wikiStatus(root, report) {
  const metadata = await readJson(root, 'openwiki/.last-update.json');
  const receipt = await readJson(root, receiptName);
  if (!metadata || !receipt) return { status: 'unreviewed', reason: 'No guarded completion receipt', metadata };
  const matches = metadata.status === 'complete' && receipt.snapshot === report.snapshot && receipt.wiki_digest === await digestWiki(root);
  return { status: matches ? 'current' : 'stale', reason: matches ? 'Completed wiki and inspected source versions match' : 'Source, wiki or completion state changed', metadata, receipt };
}

export async function saveReceipt(root, report) {
  const metadata = await readJson(root, 'openwiki/.last-update.json');
  if (metadata?.status !== 'complete') fail('WIKI_NOT_CURRENT', 'OpenWiki metadata is not complete.');
  if (report.missing_sources.length || report.broken_links.length) fail('CONTEXT_FINDINGS', 'Resolve missing sources and local link targets before recording the integrated workflow.');
  const file = await safe(root, receiptName);
  const temporary = `${file}.${randomUUID()}.tmp`;
  const receipt = { schema_version: 1, snapshot: report.snapshot, wiki_digest: await digestWiki(root), recorded_at: new Date().toISOString() };
  try { await writeFile(temporary, JSON.stringify(receipt, null, 2) + '\n', { flag: 'wx', mode: 0o600 }); await rename(temporary, file); }
  finally { if (await exists(temporary)) await unlink(temporary); }
  return receipt;
}

export async function recordReview(root, input, host) {
  await noWorkflow(root);
  const report = await context(root);
  if ((await wikiStatus(root, report)).status !== 'current') fail('WIKI_NOT_CURRENT', 'Finish a clean wiki update against the current sources first.');
  if (input.snapshot !== report.snapshot) fail('SNAPSHOT_CHANGED', 'Inspect the current snapshot again.');
  const args = ['-B', path.join(skill, 'scripts/product_context.py'), 'record', '--repo', root, '--snapshot', input.snapshot, '--actor', `agent:${host}`, '--note', input.note];
  for (const question of input.questions) args.push('--question', question);
  for (const question of input.resolvedQuestions ?? []) args.push('--resolve-question', question);
  try { return JSON.parse(execFileSync('python3', args, { encoding: 'utf8', timeout: 15000, stdio: ['ignore', 'pipe', 'pipe'] })); }
  catch { fail('REVIEW_REJECTED', 'Review changed or question resolution was invalid; inspect context again.'); }
}
