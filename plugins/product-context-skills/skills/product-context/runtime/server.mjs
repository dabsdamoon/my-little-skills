import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { readFile } from 'node:fs/promises';
import { z } from 'zod';
import { beginGuard, context, exists, fail, lock, noWorkflow, readJson, recordReview, rootPath, safe, saveReceipt, subscription, wikiStatus } from './guard.mjs';

const host = process.argv[process.argv.indexOf('--host') + 1];
if (!['claude', 'codex'].includes(host)) throw new Error('Specify --host claude or --host codex');
const maxIndex = process.argv.indexOf('--max-pages');
const maxPages = maxIndex === -1 ? 3 : Number(process.argv[maxIndex + 1]);
if (!Number.isInteger(maxPages) || maxPages < 1 || maxPages > 30) throw new Error('--max-pages must be between 1 and 30');
const dependency = JSON.parse(await readFile(new URL('./node_modules/openwiki/package.json', import.meta.url), 'utf8'));
if (dependency.version !== '0.9.0') throw new Error('UNSUPPORTED_OPENWIKI: Install the pinned runtime with npm ci; this guard supports OpenWiki 0.9.0.');
process.env.OPENWIKI_TELEMETRY_DISABLED = '1';
process.env.DO_NOT_TRACK = '1';

const { HostSessionManager } = await import('openwiki/dist/integrations/core/session-manager.js');
const manager = HostSessionManager.create({ host, producerActor: host === 'claude' ? 'claude-code' : 'codex' });
let activeRoot = null;
let release = null;
let busy = false;
const plannedPages = new Set();
let claimIssuePages = [];
const pageKey = value => '/' + value.replace(/^\/+/, '');

const instructions = `Maintain product documents in the CURRENT subscription-authenticated host session. This MCP server calls no model/provider and has no API fallback or schedule. Read the product-context skill before generation. Write source specs/ADRs/decisions FIRST; preserve old evidence and distinguish accepted target, implemented behavior and proposals. Do not invent a rationale or human approval. Call openwiki_begin; existing wikis use update and interrupted runs resume. Plans are limited to ${maxPages} factual pages including quickstart. Consume the assigned page queue and sparse Claim decisions. A SOURCE_CHANGED error means pages may be saved but the workflow is incomplete: inspect sources and explicitly update again if needed, without init/reset. Finish must succeed without sourceChanged and with complete metadata. Then call product_context_status and product_context_record_review with the exact snapshot and an explicit questions array collected from documents AND existing open questions. Resolve questions only with answers. Do not use a raw CLI record to bypass a failed wiki completion. Existing API workflows are preserved and block generation until explicitly reviewed. Do not launch standalone OpenWiki, extra models or background jobs.`;
const server = new McpServer({ name: 'product-context', version: '0.3.0' }, { instructions });

async function unlock() {
  manager.active = null;
  activeRoot = null;
  plannedPages.clear();
  claimIssuePages = [];
  if (release) { const previous = release; release = null; await previous(); }
}
async function execute(name, input, native) {
  const generation = !['openwiki_list_workspaces', 'openwiki_list_wikis', 'openwiki_search', 'openwiki_read', 'product_context_status', 'product_context_subscription_status'].includes(name);
  if (generation && busy) fail('BUSY', 'Another wiki operation is in progress.');
  if (generation) busy = true;
  try {
    if (name === 'product_context_subscription_status') return { ...subscription(host), model_calls: 0, provider_execution: false, max_pages: maxPages };
    if (name === 'product_context_status') {
      const root = await rootPath(input.root);
      const report = await context(root);
      return { context: report, wiki: await wikiStatus(root, report), execution: { model_calls: 0, provider_execution: false, host, max_pages: maxPages } };
    }
    if (generation) subscription(host);
    if (name === 'product_context_record_review') {
      const root = await rootPath(input.root);
      const releaseReview = await lock(root);
      try { return await recordReview(root, input, host); } finally { await releaseReview(); }
    }
    if (generation && name !== 'openwiki_begin' && (!activeRoot || !release || !await release.owns())) {
      await unlock();
      fail('NO_ACTIVE_RUN', 'Call openwiki_begin to acquire this product before continuing.');
    }
    if (name === 'openwiki_begin') {
      const root = await rootPath(input.root);
      await context(root);
      if (activeRoot && activeRoot !== root) fail('ACTIVE_RUN', 'Finish the active product run before starting another.');
      if (!release) release = await lock(root);
      activeRoot = root;
      try {
        const pending = await readJson(root, 'openwiki/.run.json');
        const retainedPaths = [...(pending?.plan?.pages ?? []).map(page => page.path), ...(pending?.plan?.deletePages ?? [])].map(pageKey);
        if (new Set(retainedPaths).size > maxPages) fail('PAGE_LIMIT', `The durable queue exceeds this connection's ${maxPages}-page budget; configure an adequate explicit budget to resume it.`);
        for (const item of retainedPaths) plannedPages.add(item);
        const wiki = await safe(root, 'openwiki');
        const mode = pending?.mode ?? (await exists(wiki) ? 'update' : 'init');
        const result = await beginGuard(root, () => native.handle({ ...input, root, mode }));
        claimIssuePages = (result.claimIssuePages ?? []).map(pageKey);
        if (result.status === 'noop') {
          await saveReceipt(root, await context(root));
          await unlock();
        }
        return { ...result, requested_mode: input.mode, execution: 'subscription-host', max_pages: maxPages };
      } catch (error) { await unlock(); throw error; }
    }
    if (name === 'openwiki_submit_plan') {
      const paths = [...input.pages.map(page => page.path), ...(input.deletePages ?? []), ...(input.deferUnplannedClaimIssues ? [] : claimIssuePages)].map(pageKey);
      const combined = new Set([...plannedPages, ...paths]);
      if (input.pages.length > maxPages || combined.size > maxPages) fail('PAGE_LIMIT', `This run permits at most ${maxPages} pages including quickstart and deletions.`);
      const result = await native.handle(input);
      if (result.totalPages > maxPages) fail('PAGE_LIMIT', 'The expanded OpenWiki queue exceeds this run budget; reduce/defer the plan or configure an explicit larger budget.');
      for (const item of combined) plannedPages.add(item);
      return result;
    }
    if (['openwiki_next_page', 'openwiki_submit_page'].includes(name) && activeRoot) {
      const pending = await readJson(activeRoot, 'openwiki/.run.json');
      if ((pending?.plan?.pages?.length ?? 0) > maxPages) fail('PAGE_LIMIT', 'The expanded durable queue exceeds this connection budget.');
    }
    if (name === 'openwiki_finish') {
      const root = activeRoot;
      let finished = false;
      try {
        if (!root) fail('NO_ACTIVE_RUN', 'Call openwiki_begin first.');
        const result = await native.handle(input);
        finished = true;
        if (result.sourceChanged) fail('SOURCE_CHANGED', 'Pages were saved but sources changed during generation; inspect and update again. No current receipt was written.');
        await noWorkflow(root);
        const receipt = await saveReceipt(root, await context(root));
        return { ...result, review_snapshot: receipt.snapshot, execution: 'subscription-host', model_calls: 0 };
      } finally { if (finished) await unlock(); }
    }
    return native.handle(input);
  } finally { if (generation) busy = false; }
}

async function response(name, input, native) {
  try {
    const result = await execute(name, input, native);
    return { content: [{ type: 'text', text: JSON.stringify(result) }], structuredContent: result };
  } catch (error) {
    return { isError: true, content: [{ type: 'text', text: error.message?.slice(0, 2000) ?? 'WIKI_OPERATION_FAILED' }] };
  }
}

for (const tool of manager.tools()) {
  const readOnly = ['openwiki_list_workspaces', 'openwiki_list_wikis', 'openwiki_search', 'openwiki_read'].includes(tool.name);
  server.registerTool(tool.name, {
    description: tool.name === 'openwiki_begin' ? 'Start guarded subscription-host generation. Existing wikis always update; durable interrupted runs resume. No API workflow or provider is started.' : tool.description,
    inputSchema: tool.schema,
    annotations: { readOnlyHint: readOnly, destructiveHint: false, openWorldHint: false },
  }, input => response(tool.name, input, tool));
}
server.registerTool('product_context_status', {
  description: 'Inspect primary evidence and the guarded wiki receipt without model calls. Current evidence is not semantic approval.',
  inputSchema: z.object({ root: z.string().min(1) }).strict(),
  annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false },
}, input => response('product_context_status', input));
server.registerTool('product_context_subscription_status', {
  description: 'Check the host CLI subscription login without generating text or exposing credentials. This is a login check, not a billing receipt.',
  inputSchema: z.object({}).strict(),
  annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false },
}, input => response('product_context_subscription_status', input));
server.registerTool('product_context_record_review', {
  description: 'Record an inspected snapshot only after a clean, current wiki finish; explicitly carry source-document questions and existing open questions.',
  inputSchema: z.object({ root: z.string().min(1), snapshot: z.string().length(64), note: z.string().min(1), questions: z.array(z.string().min(1)), resolvedQuestions: z.array(z.string().min(1)).optional() }).strict(),
  annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false },
}, input => response('product_context_record_review', input));

const transport = new StdioServerTransport();
transport.onclose = async () => { await unlock(); };
for (const signal of ['SIGTERM', 'SIGINT']) process.once(signal, async () => { await unlock(); await server.close(); process.exit(0); });
if (process.argv.includes('--self-check')) {
  process.stdout.write(JSON.stringify({ ok: true, host, model_calls: 0, version: '0.3.0' }) + '\n');
} else if (process.argv.includes('--check-auth')) {
  process.stdout.write(JSON.stringify(subscription(host)) + '\n');
} else {
  await server.connect(transport);
}
