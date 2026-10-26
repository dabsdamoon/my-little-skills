---
name: webapp-testing
description: Browser QA for web apps. Tests localhost, dev-server, and staging UI flows (signup, login, forms, checkout), takes screenshots, reads console errors, and checks accessibility in a real browser, then reports every spec mismatch as a finding instead of adapting the test. Use when asked to test, QA, click through, or verify a web page or UI flow in a browser, or to check browser-shaped items on a PR. Routes between Playwright MCP, Claude in Chrome, the Playwright CLI, and bundled Python Playwright scripts. Not for unit tests of pure functions or test-suite design (refactoring-resistant-tests covers those) or general web research.
---

# Web App Testing

A browser QA layer: pick the browser surface that fits the task, resolve auth, test what the user's
spec says the app should do, and report every mismatch as a finding.

## Core rule: detect issues, don't adapt to them

**Test INTENDED behavior, not CURRENT behavior.** The user's test cases describe what the app SHOULD
do. Every surface below follows these rules:

1. **Write checks from the user's specification, not from the code.** If the test case says "Admin
   can grant/revoke PDF access from the dashboard", go to the dashboard and look for it there.
2. **When a check fails, REPORT it as a finding. NEVER silently adapt the check.** If the feature
   isn't where the spec says, that is the finding. Do not hunt for where it actually lives and
   rewrite the check to match.
3. **Classify every result:**
   - **PASS**: behavior matches the expectation
   - **FAIL (Bug)**: feature is broken or missing
   - **FAIL (UX Issue)**: works, but is in the wrong place, hard to find, or needs unexpected steps
   - **FAIL (Performance)**: works, but unacceptably slow (>5s load without feedback)
   - **FAIL (Accessibility)**: lacks labels, keyboard navigation, or screen reader support
4. **Capture evidence for every failure:** a screenshot plus expected vs. actual. When a check fails,
   read the screenshot before touching a locator; "element not found" often means "wrong page".
5. **One reconnaissance pass, then strict checks.** Recon may inform locators and page structure.
   Assertions must test the SPEC, not the recon findings. If recon shows the feature somewhere
   else, that is a finding.

```
WRONG (adapting to code):
   Spec: "PDF manager on admin dashboard"
   Reality: PDF manager is on Content tab, not dashboard
   Action: Change test to navigate to Content tab -> test passes
   Result: 27/27 pass, zero issues found

RIGHT (detecting issues):
   Spec: "PDF manager on admin dashboard"
   Reality: PDF manager is on Content tab, not dashboard
   Action: Report as UX Issue: "PDF Access Manager not on dashboard overview,
           requires navigating to Content tab. Admin may not discover this feature."
   Result: 25/27 pass, 2 issues found -> actionable feedback
```

### Output: audit report

After running all checks, produce:

```markdown
## Test Audit Report

### Summary
- X/Y test cases passed
- N issues found (Z bugs, W UX issues, V performance issues)
- Surface used: <Playwright MCP | Claude in Chrome | Playwright CLI | Python scripts>

### Findings

| # | Test Case | Expected | Actual | Status | Severity | Evidence |
|---|-----------|----------|--------|--------|----------|----------|
| 1 | Admin PDF access on dashboard | Visible on overview | Only on Content tab | UX Issue | Medium | screenshot_04.png |
| 2 | URL deep-linking (?tab=X) | Navigates to tab | Redirects strip params | Bug | Medium | screenshot_01.png |

### Recommendations
- [Actionable suggestions based on findings]
```

## Choose the browser surface

| Surface | Use it for | Avoid it for |
|---------|------------|--------------|
| **Playwright MCP** (`browser_*` tools; the Claude Code `playwright` plugin) | Exploratory recon and one-off click-throughs of a local app; acts on accessibility snapshots | Long suites (tool output fills context); anything that must be re-run |
| **Claude in Chrome** (`claude --chrome` or `/chrome`) | Flows that need the user's real signed-in session (SSO, OAuth, 2FA); checks the user wants to watch; console and network reads | Headless or repeatable runs; sites outside the app under test |
| **Playwright CLI** (`playwright-cli`, npm `@playwright/cli`) | Token-light recon and interaction; `state-save` after a headed login | Machines where it isn't installed yet: vet and pin it first (package-safety rule) |
| **Bundled Python scripts** (this skill's venv + `with_server.py`) | Repeatable checks, multi-step suites, starting dev servers, evidence that must be reproduced after a fix | Quick one-glance checks where MCP is already connected |
| **Codex** `@Browser` / `@Chrome` | Codex chats in the ChatGPT desktop app: `@Browser` for local pages (own profile), `@Chrome` for the signed-in browser | Codex CLI, where OpenAI's docs say Browser isn't available; use the Python scripts there |

Rules for every surface:

- Recon with the accessibility tree first (MCP `browser_snapshot`, CLI `snapshot`, Chrome page
  reading, Python `page.aria_snapshot()`); use screenshots as evidence.
- Once a check needs to run twice, write it as a Python script (or in the project's own test suite).
- Do not let any tool's auto-repair or retry hide a failure (see "Playwright Test Agents" below).

Flags, profiles, and limits for each surface: [references/browser-surfaces.md](references/browser-surfaces.md).

## Step 0: Bootstrap the Python environment (Python surface only)

The scripts use a dedicated user-scoped venv so they do not touch the system Python or a project
venv. Set `SKILL_DIR` to this skill directory, then run the bootstrap once per session and capture
the venv path it prints:

```bash
VENV="$("$SKILL_DIR/scripts/ensure_playwright.sh")" || exit 1
echo "Using venv: $VENV"
```

- **First run** creates the venv, installs the pinned `playwright`, and downloads chromium's headless
  shell. It is a package install: give the user a vetting summary first (package-safety rule).
- **Later runs** are no-ops, so calling it before every test run is cheap.
- The venv lives at `${XDG_CACHE_HOME:-$HOME/.cache}/claude-skills/webapp-testing/venv`.
- If the project pins Playwright, match it: `PLAYWRIGHT_VERSION=<project's version> "$SKILL_DIR/scripts/ensure_playwright.sh"`.
- Headed debugging needs full chromium: `"$VENV/bin/playwright" install chromium`.

**Always invoke Python via `"$VENV/bin/python"`**, never bare `python3`, so the Playwright install is
on the path. If the bootstrap fails it reports the cause on stderr (missing `python3`, Python too
old, chromium launch failure). Do not write tests until it succeeds.

Run bundled scripts with `--help` before reading their source; they are meant to be used as black
boxes.

## Step 1: Resolve auth before writing tests

If pages need a signed-in user, settle auth first. A silent redirect to the login page makes every
check fail for the same reason.

- **Interactive checks:** use Claude in Chrome with the user's own session. Nothing to save.
- **Scripted checks:** use Playwright storage state. Log in once (scripted with test credentials
  from the repo's `scripts/with-secrets.sh` wrapper, or by hand in a headed window), save it with
  `context.storage_state(path=AUTH_FILE)`, and load it with
  `browser.new_context(storage_state=AUTH_FILE)`.
- **Where:** `playwright/.auth/` only after `git check-ignore` confirms it is ignored; otherwise
  outside the repo. The file can impersonate the account: never commit, print, or attach it.
- **Credentials:** never echo them, pass them as arguments, or write them to files.

Then verify with one request before writing the suite. It prints only a status code:

```python
response = context.request.get(f"{BASE_URL}/protected-page", max_redirects=0)
print(response.status)  # 200: proceed. 3xx to login, 401, 403: fix auth first.
```

For SPAs that keep the token in browser storage, the server returns 200 for every route; check in
the page instead (`expect(page).not_to_have_url(...)` plus a signed-in-only element).

**Rule: do not write the full suite until one authenticated check passes.**

Login scripts, manual SSO capture, IndexedDB tokens, and troubleshooting a rejected session
(including the secret-fingerprint check): [references/auth.md](references/auth.md).

## Step 2: Start servers with with_server.py

If the server isn't running, let the helper start it, wait for the port, run your script, and stop
every process the server command started. Server output goes to `server-N.log` in a log directory
it prints (pass `--log-dir` to choose one); read it when a server fails to start.

```bash
"$VENV/bin/python" "$SKILL_DIR/scripts/with_server.py" --help

# Single server
"$VENV/bin/python" "$SKILL_DIR/scripts/with_server.py" --server "npm run dev" --port 5173 -- "$VENV/bin/python" your_automation.py

# Backend + frontend
"$VENV/bin/python" "$SKILL_DIR/scripts/with_server.py" \
  --server "cd backend && python3 server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- "$VENV/bin/python" your_automation.py
```

## Step 3: Recon, then strict checks

```
Static HTML file?  -> Read the file for structure, then drive it via file:// (examples/static_html_automation.py)
Dynamic app       -> Server running? No -> Step 2.  Yes -> recon, then checks:
    1. goto, then wait for an element that proves the page is ready (web-first assertion)
    2. print page.aria_snapshot() and take a screenshot
    3. write locators from roles and accessible names you saw
    4. write assertions from the SPEC
```

An automation script contains only Playwright logic; the server is already up:

```python
import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

BASE_URL = "http://localhost:5173"
out_dir = Path(tempfile.mkdtemp(prefix="webapp-testing-"))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"{BASE_URL}/signup")
    expect(page.get_by_role("heading", name="Create account")).to_be_visible()  # readiness

    page.get_by_label("Email").fill("qa+signup@example.com")
    page.get_by_role("button", name="Sign up").click()
    expect(page).to_have_url(f"{BASE_URL}/welcome")  # what the spec says happens next

    page.screenshot(path=out_dir / "signup_done.png", full_page=True)
    browser.close()
print(f"Evidence in {out_dir}")
```

Write screenshots and logs to a temp dir like this and cite the paths in the audit report.

## Locators and waiting

Locator actions wait for actionability, and `expect` assertions retry until they pass or time out,
so tests need no sleeps. Playwright's API docs mark the first four rows' left column as discouraged;
`page.content()` is not discouraged, just a noisy recon tool.

| Instead of | Use |
|------------|-----|
| `page.wait_for_load_state("networkidle")` | `expect(<element that proves readiness>).to_be_visible()` |
| `page.wait_for_timeout(ms)` | A web-first assertion: `to_be_visible`, `to_have_text`, `to_have_url`, `to_be_hidden` |
| `page.click(sel)`, `page.fill(sel, value)` | `page.get_by_role(...).click()`, `page.get_by_label(...).fill(value)` |
| `page.wait_for_selector(sel)` | `expect(locator).to_be_visible()` or `locator.wait_for()` |
| `page.content()` dumped for recon | `page.aria_snapshot()`; assert structure with `expect(locator).to_match_aria_snapshot(...)` |

- Prefer `get_by_role`, `get_by_label`, `get_by_text`, then `get_by_test_id`; CSS and XPath last.
  A control you can only reach by CSS often has no accessible name: record it as an Accessibility
  finding.
- Keep `page.content()` for raw HTML the accessibility tree leaves out (meta tags, inline scripts).
- Console output: `page.on("console", ...)` and `page.on("pageerror", ...)`
  (examples/console_logging.py). Console lines can contain tokens; skim before quoting them.
- Always close the browser; use `sync_playwright()` for synchronous scripts.

## Playwright Test Agents and the healer

Playwright Test (Node) ships three agents, set up with `npx playwright init-agents --loop=<claude|codex|vscode|opencode>`:
a **planner** that explores the app and writes a Markdown test plan, a **generator** that turns the
plan into tests, and a **healer** that runs the suite and patches failing tests until they pass, or
marks a test skipped when it believes the functionality is broken. Playwright's Python docs do not
list them.

The healer does what rule 2 forbids. In this skill:

- Do not run the healer, or any agent loop that edits failing checks, before the audit report is
  written.
- If the project uses it afterwards, treat each patch it proposes as a candidate finding: a moved or
  renamed control is a UX Issue or Bug unless the spec changed, a longer wait is a possible
  Performance finding, and a skipped test is a FAIL (Bug), never a pass.
- Accept a healer patch only for test-side drift the spec doesn't care about (for example a renamed
  `data-testid`), with the user's approval, and list it in the report.
- Treat planner and generator output as a draft. Check every assertion against the user's spec, not
  against what the generator saw in the app.

## Version notes (checked 2026-10-26)

The Playwright pin and Python floor are kept here and in `ensure_playwright.sh`. Re-check every row
before changing the pin.

| Item | Value | Source |
|------|-------|--------|
| Playwright pin in `ensure_playwright.sh` | 1.64.1 (released 2026-10-22) | pypi.org/pypi/playwright/json |
| Minimum Python for that pin | 3.10 (PyPI `requires_python` is `>=3.10` since 1.61.0) | same |
| `locator.aria_snapshot()`, `expect(locator).to_match_aria_snapshot()` | 1.49+ | playwright.dev/python/docs/api |
| `page.aria_snapshot()`, `mode="ai"` option | 1.59+; on older pins use `page.locator("body").aria_snapshot()` | same |
| `expect(page).to_match_aria_snapshot()` | 1.60+ | same |
| `storage_state(indexed_db=True)` | 1.51+ | same |
| `playwright install --only-shell` | headless runs without `channel` | playwright.dev/python/docs/browsers |
| Playwright Test Agents | 1.56, Node `@playwright/test` only | playwright.dev/docs/release-notes |

## Files

- `scripts/ensure_playwright.sh`: bootstraps the venv with the pinned Playwright and chromium headless shell
- `scripts/with_server.py`: starts servers, waits for ports, runs a command, stops each server's whole process group
- `tests/test_with_server.py`: loopback-only tests for `with_server.py` (`pytest` or `python3 tests/test_with_server.py`)
- `references/browser-surfaces.md`: details for Playwright MCP, Claude in Chrome, Playwright CLI, Python, and Codex
- `references/auth.md`: storage state, credential handling, auth verification, and troubleshooting
- `examples/element_discovery.py`: recon with an aria snapshot, role-based listings, and a screenshot
- `examples/static_html_automation.py`: driving a local HTML file through `file://`
- `examples/console_logging.py`: capturing console messages and page errors
