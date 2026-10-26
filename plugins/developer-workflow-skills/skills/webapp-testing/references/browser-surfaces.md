# Browser surfaces

Details behind the routing table in SKILL.md. Checked 2026-10-26 against:
the Playwright MCP README (github.com/microsoft/playwright-mcp), the Playwright CLI README
(github.com/microsoft/playwright-cli), code.claude.com/docs/en/chrome, playwright.dev/python/docs,
and OpenAI's Browser and browser-extension pages (learn.chatgpt.com/docs/browser,
learn.chatgpt.com/docs/chrome-extension). Re-check these pages before relying on a flag or limit.

Every surface follows the same rules: test the user's spec, report mismatches as findings, capture a
screenshot for each failure, and finish with the audit report.

## Playwright MCP

- **What it is:** an MCP server that exposes Playwright as `browser_*` tools. It acts on the page's
  accessibility tree (`browser_snapshot`), not on pixels. `browser_take_screenshot` is for evidence;
  the README says you can't act on a screenshot.
- **In Claude Code:** the `playwright` plugin from claude-plugins-official starts
  `npx @playwright/mcp@latest` with no extra flags, so the browser is **headed** and uses a
  **persistent profile** per workspace (`~/Library/Caches/ms-playwright/mcp-{channel}-{workspace-hash}`
  on macOS). A login done in that window stays signed in for that project. One browser can use a
  profile at a time; a second client needs `--isolated` or its own `--user-data-dir`.
- **Tools you will use:** `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`,
  `browser_fill_form`, `browser_wait_for`, `browser_take_screenshot`, `browser_console_messages`,
  `browser_network_requests`. Storage tools (`browser_storage_state`, `browser_set_storage_state`)
  need `--caps=storage` and assertion tools (`browser_verify_*`) need `--caps=testing`; the default
  plugin config enables neither.
- **Auth:** `--isolated --storage-state=<path>` loads a saved state into a clean context.
  `--extension` attaches to the user's running Chrome or Edge through the "Playwright Extension".
- **Cost:** tool schemas and snapshots take context. The README itself recommends the CLI for coding
  agents and positions MCP for long exploratory sessions. It also says MCP is not a security boundary.

## Claude in Chrome

- **What it is:** Claude Code driving the user's own Chrome (or Edge, Brave, Arc, Vivaldi, Opera)
  through the Claude in Chrome extension. It opens new tabs, shares the browser's login state, runs in
  a visible window, and pauses on login pages and CAPTCHAs for the user to handle.
- **Enable it:** start with `claude --chrome`, or run `/chrome` to check status, manage site
  permissions, reconnect, or turn on "Enabled by default". Requires a claude.ai login (`/login`);
  sessions using an API key or `claude setup-token` keep it off. Not supported in WSL.
- **Use it for:** flows that need the user's real account (SSO, OAuth, 2FA), checks the user wants to
  watch, console errors, network requests, and GIF recordings of a flow.
- **Cautions:** it acts as the user. Stay on the app under test. GIFs capture whatever is on screen,
  account details included, so review them before sharing. Do not read cookies, tokens, or storage
  through page JavaScript to reuse them elsewhere. A JavaScript `alert`/`confirm` blocks the extension
  until someone dismisses it.
- **Not for:** headless runs, repeatable suites, or CI.

## Playwright CLI (`playwright-cli`)

- **What it is:** the npm package `@playwright/cli`, a command-per-action CLI built for coding agents.
  Headless by default (`open --headed` to watch). The profile lives in memory unless you pass
  `open --persistent` or `--profile=<path>`.
- **Commands:** `open`, `goto`, `snapshot` (returns element refs), `click <ref>`, `fill <ref> <text>`,
  `screenshot`, `console`, `requests`, `state-save [file]`, `state-load <file>`,
  `attach --extension=chrome`, `attach --cdp=chrome`. `playwright-cli --help` lists the rest.
- **Install:** needs Node.js 18+. It is a package install, so vet it and pin a version first
  (package-safety rule). `playwright-cli install --skills` adds its own agent skill.
- **Use it for:** quick recon and interaction when context is tight, and saving storage state after a
  headed manual login.

## Bundled Python scripts

- **What it is:** this skill's venv (`scripts/ensure_playwright.sh`), the server manager
  (`scripts/with_server.py`), and Playwright scripts you write.
- **Use it for:** anything that must run again after a fix, multi-step suites, starting and stopping
  dev servers, reproducible evidence, and headless runs.
- **Browser:** the bootstrap installs only chromium's headless shell. For a headed window run
  `"$VENV/bin/playwright" install chromium` once.

## Codex

- **Browser plugin (`@Browser`):** bundled with Codex and drives the ChatGPT desktop app's in-app
  browser. It has its own profile (it does not share the user's tabs or session; the user can sign in
  inside it) and targets localhost and `file://` pages. OpenAI's docs say Browser isn't available in
  Codex CLI or the Codex IDE extension, and it can't automate file uploads.
- **`@Chrome` (ChatGPT browser extension):** works in the user's signed-in Chrome, Edge, Brave, Opera,
  or Vivaldi profile and asks before acting on each new site by default.
- **Playwright MCP:** Codex can also run it; the MCP README has a Codex section.
- **Routing:** in the desktop app, `@Browser` covers what Playwright MCP covers here and `@Chrome`
  covers what Claude in Chrome covers. In a Codex CLI session where `@Browser` isn't offered, use the
  bundled Python scripts.
