---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

## CRITICAL: Testing Philosophy — Detect Issues, Don't Adapt to Them

**Your job is to test INTENDED behavior, not to confirm CURRENT behavior.**

When a user provides test cases, those describe what the app SHOULD do. Your tests must:

1. **Write tests from the user's specification, not from the code** — If the test case says "Admin can grant/revoke PDF access from the dashboard", test exactly that. Navigate to the dashboard and look for it there.

2. **When a test fails, REPORT it as a finding — NEVER silently adapt the test** — If the feature isn't where the spec says it should be, that's a finding. Don't go hunt for where it actually lives and rewrite the test to match.

3. **Classify every discrepancy** — Each test result must be one of:
   - **PASS**: Behavior matches the test case expectation
   - **FAIL (Bug)**: Feature is broken or missing
   - **FAIL (UX Issue)**: Feature works but is in the wrong place, hard to find, or requires unexpected steps
   - **FAIL (Performance)**: Feature works but is unacceptably slow (>5s load without feedback)
   - **FAIL (Accessibility)**: Feature lacks proper labels, keyboard nav, or screen reader support

4. **Capture evidence for every failure** — Screenshot + description of what was expected vs. what actually happened.

5. **Do ONE reconnaissance pass, then write strict tests** — You may do an initial recon to understand selectors and page structure. But once you write the actual test assertions, those must test the SPEC, not the recon findings. If recon reveals the feature is in a different place than the spec says, that's a finding.

```
❌ WRONG (adapting to code):
   Spec: "PDF manager on admin dashboard"
   Reality: PDF manager is on Content tab, not dashboard
   Action: Change test to navigate to Content tab → test passes
   Result: 27/27 pass, zero issues found

✅ RIGHT (detecting issues):
   Spec: "PDF manager on admin dashboard"
   Reality: PDF manager is on Content tab, not dashboard
   Action: Report as UX Issue — "PDF Access Manager not on dashboard overview,
           requires navigating to Content tab. Admin may not discover this feature."
   Result: 25/27 pass, 2 issues found → actionable feedback
```

### Output Format

After running all tests, produce an **Audit Report** summarizing:

```markdown
## Test Audit Report

### Summary
- X/Y test cases passed
- N issues found (Z bugs, W UX issues, V performance issues)

### Findings

| # | Test Case | Expected | Actual | Status | Severity | Evidence |
|---|-----------|----------|--------|--------|----------|----------|
| 1 | Admin PDF access on dashboard | Visible on overview | Only on Content tab | UX Issue | Medium | screenshot_04.png |
| 2 | URL deep-linking (?tab=X) | Navigates to tab | Redirects strip params | Bug | Medium | screenshot_01.png |

### Recommendations
- [Actionable suggestions based on findings]
```

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Step 0: Authentication Setup (before writing any tests)

If the app requires login/session to access pages, **resolve auth first** before writing Playwright scripts. Silent auth failures (redirect to login/signup) will cause every test to fail for the same reason.

### 1. Identify session mechanism
```bash
# Check for session/cookie/auth patterns in the codebase
grep -r "session\|SESSION_SECRET\|createCookie\|jwt" app/lib/ --include="*.ts" -l
```

### 2. Check ALL secret sources for mismatches
```bash
# These three can have DIFFERENT values — compare them:
grep SESSION_SECRET .env .env.local .env.development 2>/dev/null   # Vite loads these automatically
grep SESSION docker-compose.yml 2>/dev/null                         # Docker env vars
grep -r "SESSION_SECRET\|secrets:" app/lib/ --include="*.ts"        # Code defaults
```
**The #1 cause of silent auth failure is secret mismatch between `.env` and code defaults.** Vite auto-loads `.env` files, so the running app may use a different secret than the code's fallback value.

### 3. Generate a valid session cookie using the app's own runtime
```bash
# Use the ACTUAL running app to serialize a cookie (ensures correct secret)
docker exec <container> node -e "
  const { createCookie } = await import('react-router');
  const secret = process.env.SESSION_SECRET || '<code-default>';
  // ... serialize session with the real secret
"
```

### 4. Verify auth with curl BEFORE writing Playwright tests
```bash
# This takes 2 seconds vs. minutes of debugging Playwright failures
curl -s -o /dev/null -w "%{http_code}" \
  -H "Cookie: <session_cookie>" \
  http://localhost:PORT/protected-page
# Expected: 200. If 302 → auth is broken, fix before proceeding.
```

### 5. Only then proceed to Playwright
Once curl returns 200 on a protected page, use the cookie value in Playwright:
```python
context.add_cookies([{
    "name": "session_name",
    "value": cookie_value,
    "domain": "localhost",
    "path": "/",
    "httpOnly": True,
    "sameSite": "Lax",
}])
```

**Rule: Never write a full test suite until one authenticated curl request succeeds.**

---

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation