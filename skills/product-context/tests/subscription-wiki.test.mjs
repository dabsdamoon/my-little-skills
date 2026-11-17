import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm, access, symlink, copyFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync, spawnSync } from 'node:child_process';
import { Client } from '../runtime/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import { StdioClientTransport } from '../runtime/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js';

const skill = fileURLToPath(new URL('../', import.meta.url));
const server = path.join(skill, 'runtime/server.mjs');

async function fixture(t, { host = 'codex', auth = 'subscription', authToStderr = false, authProvider = 'firstParty', confined = false } = {}) {
  const dir = await mkdtemp(path.join(tmpdir(), 'subscription-wiki-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const root = path.join(dir, 'product');
  const bin = path.join(dir, 'bin');
  await mkdir(path.join(root, 'src'), { recursive: true });
  await mkdir(path.join(root, 'docs'), { recursive: true });
  await mkdir(bin);
  await writeFile(path.join(root, 'README.md'), '# Synthetic product\n');
  await writeFile(path.join(root, 'src/policy.py'), 'RETENTION_DAYS = 14\n');
  await writeFile(path.join(root, 'docs/policy.md'), '# Policy\nAccepted retention is 14 days. Timezone is unknown.\n');
  await writeFile(path.join(root, '.product-context.json'), JSON.stringify({ schema_version: 1, product: 'synthetic', sources: ['README.md', 'docs/**/*.md', 'src/**/*.py'], exclude: [], topics: [] }));
  execFileSync('git', ['init', '-q', root]);
  execFileSync('git', ['-C', root, 'add', '.']);
  execFileSync('git', ['-C', root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Seed synthetic policy']);
  await writeFile(path.join(bin, 'codex'), `#!/bin/sh\nprintf '%s\\n' '${auth === 'subscription' ? 'Logged in using ChatGPT' : 'Logged in using an API key'}'${authToStderr ? ' >&2' : ''}\n`, { mode: 0o755 });
  await writeFile(path.join(bin, 'claude'), `#!/bin/sh\nprintf '%s\\n' '${JSON.stringify({ loggedIn: true, authMethod: auth === 'subscription' ? 'claude.ai' : auth === 'oauth' ? 'oauth_token' : 'api_key', apiProvider: authProvider })}'\n`, { mode: 0o755 });
  const env = { ...process.env, PATH: bin + path.delimiter + process.env.PATH, OPENWIKI_TELEMETRY_DISABLED: '1', DO_NOT_TRACK: '1' };
  for (const key of ['OPENAI_API_KEY', 'CODEX_API_KEY', 'ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'CLAUDE_CODE_OAUTH_TOKEN']) delete env[key];
  if (auth === 'oauth') env.CLAUDE_CODE_OAUTH_TOKEN = 'synthetic-subscription-token';
  if (confined) env.PRODUCT_CONTEXT_ALLOWED_ROOT = root;
  async function connect(extraArgs = []) {
    const client = new Client({ name: 'public-contract-test', version: '1' });
    const transport = new StdioClientTransport({ command: process.execPath, args: [server, '--host', host, ...extraArgs], env, stderr: 'pipe' });
    t.after(() => client.close());
    await client.connect(transport);
    return client;
  }
  return { root, client: await connect(), dir, connect };
}

test('official Claude subscription OAuth authentication can generate through the guarded MCP', async t => {
  const { root, client } = await fixture(t, { host: 'claude', auth: 'oauth' });
  const begin = await call(client, 'openwiki_begin', { root, mode: 'init' });
  assert.equal(begin.execution, 'subscription-host');
  assert.equal((await complete(client, root, begin, initialClaims)).status, 'complete');
});

test('a PR-bound MCP refuses a different repository before context or wiki mutation', async t => {
  const { root, dir, client } = await fixture(t, { confined: true });
  const other = path.join(dir, 'other');
  await mkdir(other);
  execFileSync('git', ['init', '-q', other]);
  await call(client, 'openwiki_begin', { root: other, mode: 'init' }, 'INVALID_ROOT');
  await assert.rejects(access(path.join(other, '.product-context')));
  assert.equal((await call(client, 'openwiki_begin', { root, mode: 'init' })).status, 'active');
});

async function call(client, name, args, expectedError) {
  const raw = await client.callTool({ name, arguments: args });
  const text = raw.content?.filter(x => x.type === 'text').map(x => x.text).join('\n') ?? '';
  if (expectedError) {
    assert.equal(raw.isError, true, text);
    assert.ok(text.includes(expectedError), text);
    return text;
  }
  assert.ok(!raw.isError, text);
  return raw.structuredContent ?? JSON.parse(text);
}

const page = '/openwiki/quickstart.md';
async function complete(client, root, begin, claims) {
  await call(client, 'openwiki_submit_plan', { runId: begin.runId, pages: [{ path: page, title: 'Synthetic policy', purpose: 'Explain verified runtime retention', seedPaths: ['src/policy.py'] }] });
  const next = await call(client, 'openwiki_next_page', { runId: begin.runId });
  await mkdir(path.join(root, 'openwiki'), { recursive: true });
  await writeFile(path.join(root, 'openwiki/quickstart.md'), '---\ntype: guide\ntitle: Synthetic policy\ndescription: Runtime retention and unresolved timezone\ntags: [retention]\n---\n\n# Synthetic policy\n\n## Runtime\nThe runtime policy constant is 14 days. The product timezone is unresolved.\n');
  await call(client, 'openwiki_submit_page', { runId: begin.runId, jobId: next.job.id, ...(claims ? { claims } : { confirmedClaimIds: (next.job.claimsRequiringAttention ?? []).map(x => x.id) }) });
  return call(client, 'openwiki_finish', { runId: begin.runId });
}
const initialClaims = [{ statement: 'The runtime retention constant is 14 days.', evidence: [{ resource: 'repo://src/policy.py' }] }];

test('subscription lifecycle creates a real wiki and records a guarded review without an API workflow', async t => {
  const { root, client } = await fixture(t);
  const begin = await call(client, 'openwiki_begin', { root, mode: 'init', language: 'en' });
  const finish = await complete(client, root, begin, initialClaims);
  assert.equal(finish.status, 'complete');
  await assert.rejects(access(path.join(root, '.github/workflows/openwiki-update.yml')));
  const metadata = JSON.parse(await readFile(path.join(root, 'openwiki/.last-update.json'), 'utf8'));
  assert.equal(metadata.status, 'complete');
  const status = await call(client, 'product_context_status', { root });
  assert.equal(status.wiki.status, 'current');
  await call(client, 'product_context_record_review', { root, snapshot: status.context.snapshot, note: 'Inspected source and wiki', questions: ['Which product timezone applies?'] });
  const after = await call(client, 'product_context_status', { root });
  assert.equal(after.context.review.status, 'current');
  assert.deepEqual(after.context.review.questions, ['Which product timezone applies?']);
});

test('an existing wiki uses update and keeps unchanged Claim IDs and open questions', async t => {
  const { root, client } = await fixture(t);
  await complete(client, root, await call(client, 'openwiki_begin', { root, mode: 'init' }), initialClaims);
  let status = await call(client, 'product_context_status', { root });
  await call(client, 'product_context_record_review', { root, snapshot: status.context.snapshot, note: 'Initial review', questions: ['Timezone?'] });
  const before = JSON.parse(await readFile(path.join(root, 'openwiki/.claims/quickstart.json'), 'utf8')).claims.map(x => x.id);
  await writeFile(path.join(root, 'docs/policy.md'), '# Policy\nAccepted retention is 14 days. Timezone is still unknown.\n');
  const update = await call(client, 'openwiki_begin', { root, mode: 'init', force: true });
  assert.equal(update.mode, 'update');
  await complete(client, root, update);
  const after = JSON.parse(await readFile(path.join(root, 'openwiki/.claims/quickstart.json'), 'utf8')).claims.map(x => x.id);
  assert.deepEqual(after, before);
  status = await call(client, 'product_context_status', { root });
  await call(client, 'product_context_record_review', { root, snapshot: status.context.snapshot, note: 'Updated evidence', questions: [] });
  assert.deepEqual((await call(client, 'product_context_status', { root })).context.review.questions, ['Timezone?']);
});

test('API-authenticated hosts are refused before generation mutates the product', async t => {
  for (const host of ['claude', 'codex']) {
    const { root, client } = await fixture(t, { host, auth: 'api' });
    await call(client, 'openwiki_begin', { root, mode: 'init' }, 'SUBSCRIPTION_REQUIRED');
    await assert.rejects(access(path.join(root, 'openwiki')));
    await assert.rejects(access(path.join(root, '.github')));
  }
});

test('an existing custom workflow remains unchanged and generation fails closed', async t => {
  const { root, client } = await fixture(t);
  await mkdir(path.join(root, '.github/workflows'), { recursive: true });
  const file = path.join(root, '.github/workflows/openwiki-update.yml');
  const custom = 'name: custom\non: workflow_dispatch\n# preserve user content\n';
  await writeFile(file, custom);
  await call(client, 'openwiki_begin', { root, mode: 'init' }, 'EXISTING_WORKFLOW');
  assert.equal(await readFile(file, 'utf8'), custom);
  await assert.rejects(access(path.join(root, 'openwiki')));
});

test('a source change during generation cannot produce a current wiki receipt or review', async t => {
  const { root, client } = await fixture(t);
  const begin = await call(client, 'openwiki_begin', { root, mode: 'init' });
  await call(client, 'openwiki_submit_plan', { runId: begin.runId, pages: [{ path: page, title: 'Policy', purpose: 'Retention policy' }] });
  const next = await call(client, 'openwiki_next_page', { runId: begin.runId });
  await writeFile(path.join(root, 'openwiki/quickstart.md'), '---\ntype: guide\ntitle: Policy\ndescription: Retention\ntags: [retention]\n---\n# Policy\nRetention is 14 days.\n');
  await call(client, 'openwiki_submit_page', { runId: begin.runId, jobId: next.job.id, claims: initialClaims });
  await writeFile(path.join(root, 'docs/policy.md'), '# Changed target\nThe target is now 90 days.\n');
  await call(client, 'openwiki_finish', { runId: begin.runId }, 'SOURCE_CHANGED');
  const status = await call(client, 'product_context_status', { root });
  assert.notEqual(status.wiki.status, 'current');
  await call(client, 'product_context_record_review', { root, snapshot: status.context.snapshot, note: 'must fail', questions: [] }, 'WIKI_NOT_CURRENT');
  await assert.rejects(access(path.join(root, '.product-context/review.json')));
});

test('source changes after completion invalidate the receipt and cannot overwrite a review', async t => {
  const { root, client } = await fixture(t);
  await complete(client, root, await call(client, 'openwiki_begin', { root, mode: 'init' }), initialClaims);
  await writeFile(path.join(root, 'docs/policy.md'), '# Changed target\n90 days proposed.\n');
  const status = await call(client, 'product_context_status', { root });
  assert.equal(status.wiki.status, 'stale');
  await call(client, 'product_context_record_review', { root, snapshot: status.context.snapshot, note: 'must fail', questions: [] }, 'WIKI_NOT_CURRENT');
});

test('the plan budget includes quickstart and rejects an oversized queue before persistence', async t => {
  const { root, client } = await fixture(t);
  const begin = await call(client, 'openwiki_begin', { root, mode: 'init' });
  const pages = [page, '/openwiki/a.md', '/openwiki/b.md', '/openwiki/c.md'].map(p => ({ path: p, title: 'Page', purpose: 'Verify policy' }));
  await call(client, 'openwiki_submit_plan', { runId: begin.runId, pages }, 'PAGE_LIMIT');
  await complete(client, root, begin, initialClaims);
});

test('workflow parent symlinks never write outside the product', async t => {
  const { root, client, dir } = await fixture(t);
  const outside = path.join(dir, 'outside');
  await mkdir(outside);
  await symlink(outside, path.join(root, '.github'));
  await call(client, 'openwiki_begin', { root, mode: 'init' }, 'UNSAFE_PATH');
  await assert.rejects(access(path.join(outside, 'workflows/openwiki-update.yml')));
});

test('Codex subscription status on stderr is accepted without exposing credentials', async t => {
  const { root, client } = await fixture(t, { authToStderr: true });
  const begin = await call(client, 'openwiki_begin', { root, mode: 'init' });
  assert.equal(begin.status, 'active');
});

test('wiki-only edits invalidate a completion receipt even outside the primary-source scope', async t => {
  const { root, client } = await fixture(t);
  await complete(client, root, await call(client, 'openwiki_begin', { root, mode: 'init' }), initialClaims);
  const pageFile = path.join(root, 'openwiki/quickstart.md');
  await writeFile(pageFile, (await readFile(pageFile, 'utf8')) + '\nWrong claim: 90 days are implemented.\n');
  const status = await call(client, 'product_context_status', { root });
  assert.equal(status.wiki.status, 'stale');
  await call(client, 'product_context_record_review', { root, snapshot: status.context.snapshot, note: 'must fail', questions: [] }, 'WIKI_NOT_CURRENT');
});

test('a new MCP connection resumes a durable init without replacing completed Claims', async t => {
  const { root, client, connect } = await fixture(t);
  const begin = await call(client, 'openwiki_begin', { root, mode: 'init' });
  await call(client, 'openwiki_submit_plan', { runId: begin.runId, pages: [{ path: page, title: 'Policy', purpose: 'Retention' }] });
  const job = await call(client, 'openwiki_next_page', { runId: begin.runId });
  await writeFile(path.join(root, 'openwiki/quickstart.md'), '---\ntype: guide\ntitle: Policy\ndescription: Retention\ntags: [retention]\n---\n# Policy\nRetention is 14 days.\n');
  await call(client, 'openwiki_submit_page', { runId: begin.runId, jobId: job.job.id, claims: initialClaims });
  const before = JSON.parse(await readFile(path.join(root, 'openwiki/.claims/quickstart.json'), 'utf8')).claims.map(x => x.id);
  await client.close();
  const next = await connect();
  const resumed = await call(next, 'openwiki_begin', { root, mode: 'update' });
  assert.equal(resumed.runId, begin.runId);
  assert.equal(resumed.mode, 'init');
  await call(next, 'openwiki_finish', { runId: resumed.runId });
  assert.deepEqual(JSON.parse(await readFile(path.join(root, 'openwiki/.claims/quickstart.json'), 'utf8')).claims.map(x => x.id), before);
});

test('a resumed queue cannot bypass a smaller configured page budget', async t => {
  const { root, client, connect } = await fixture(t);
  const begin = await call(client, 'openwiki_begin', { root, mode: 'init' });
  await call(client, 'openwiki_submit_plan', { runId: begin.runId, pages: [page, '/openwiki/policy.md'].map(p => ({ path: p, title: 'Policy', purpose: 'Retention' })) });
  await client.close();
  const bounded = await connect(['--max-pages', '1']);
  await call(bounded, 'openwiki_begin', { root, mode: 'init' }, 'PAGE_LIMIT');
});

test('an unsupported OpenWiki version is refused before loading its lifecycle implementation', async t => {
  const dir = await mkdtemp(path.join(tmpdir(), 'unsupported-openwiki-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const runtime = path.join(dir, 'runtime');
  await mkdir(path.join(runtime, 'node_modules/@modelcontextprotocol'), { recursive: true });
  await mkdir(path.join(runtime, 'node_modules/openwiki'));
  await writeFile(path.join(runtime, 'node_modules/openwiki/package.json'), JSON.stringify({ version: '9.0.0', type: 'module' }));
  await symlink(path.join(skill, 'runtime/node_modules/@modelcontextprotocol/sdk'), path.join(runtime, 'node_modules/@modelcontextprotocol/sdk'));
  await symlink(path.join(skill, 'runtime/node_modules/zod'), path.join(runtime, 'node_modules/zod'));
  await copyFile(server, path.join(runtime, 'server.mjs'));
  await copyFile(path.join(skill, 'runtime/guard.mjs'), path.join(runtime, 'guard.mjs'));
  const result = spawnSync(process.execPath, [path.join(runtime, 'server.mjs'), '--host', 'codex', '--self-check'], { encoding: 'utf8' });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /UNSUPPORTED_OPENWIKI/);
});

test('an external Claude provider is refused even when a subscription account is logged in', async t => {
  const { root, client } = await fixture(t, { host: 'claude', authProvider: 'external-provider' });
  await call(client, 'openwiki_begin', { root, mode: 'init' }, 'SUBSCRIPTION_REQUIRED');
  await assert.rejects(access(path.join(root, 'openwiki')));
});

test('automatically included stale Claim pages cannot expand a small plan beyond its budget', async t => {
  const { root, client, connect } = await fixture(t);
  await client.close();
  const large = await connect(['--max-pages', '4']);
  const begin = await call(large, 'openwiki_begin', { root, mode: 'init' });
  const pages = [page, '/openwiki/a.md', '/openwiki/b.md', '/openwiki/c.md'].map(p => ({ path: p, title: 'Policy', purpose: 'Retention' }));
  await call(large, 'openwiki_submit_plan', { runId: begin.runId, pages });
  for (let n = 0; n < 4; n++) {
    const next = await call(large, 'openwiki_next_page', { runId: begin.runId });
    await writeFile(path.join(root, next.job.path.replace(/^\//, '')), '---\ntype: guide\ntitle: Policy\ndescription: Retention\ntags: [retention]\n---\n# Policy\nRetention is 14 days.\n');
    await call(large, 'openwiki_submit_page', { runId: begin.runId, jobId: next.job.id, claims: initialClaims });
  }
  await call(large, 'openwiki_finish', { runId: begin.runId });
  await large.close();
  await writeFile(path.join(root, 'src/policy.py'), 'RETENTION_DAYS = 14\n# Documentation-only source clarification.\n');
  const bounded = await connect();
  const update = await call(bounded, 'openwiki_begin', { root, mode: 'update' });
  assert.equal(update.claimIssuePages.length, 4);
  await call(bounded, 'openwiki_submit_plan', { runId: update.runId, pages: [pages[0]] }, 'PAGE_LIMIT');
});

test('a premature finish keeps exclusive ownership while its pending run remains usable', async t => {
  const { root, client, connect } = await fixture(t);
  const begin = await call(client, 'openwiki_begin', { root, mode: 'init' });
  await call(client, 'openwiki_submit_plan', { runId: begin.runId, pages: [{ path: page, title: 'Policy', purpose: 'Retention' }] });
  await call(client, 'openwiki_finish', { runId: begin.runId }, 'pending');
  const other = await connect();
  await call(other, 'openwiki_begin', { root, mode: 'init' }, 'LOCKED');
  assert.equal((await call(client, 'openwiki_next_page', { runId: begin.runId })).status, 'pending');
});
