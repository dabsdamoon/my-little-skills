# Auth for browser tests

Read this when the app needs a signed-in user. SKILL.md has the short version.
API names checked 2026-10-26 against playwright.dev/python/docs (auth guide, BrowserContext,
APIRequestContext, PageAssertions).

## Contents

- Pick an approach
- Where the storage-state file lives
- Save storage state: scripted login
- Save storage state: manual login (SSO, 2FA)
- Reuse it
- Verify auth before writing tests
- If the session is rejected
- Never

## Pick an approach

| Situation | Approach |
|-----------|----------|
| Interactive check that needs the user's real account (SSO, 2FA, third-party login) | Claude in Chrome: the user's signed-in browser. Nothing is saved. |
| Scripted or repeated checks | Playwright storage state: log in once, save the context state, load it in every run. |
| Playwright MCP with the default plugin config | Log in once in the MCP window; the persistent per-workspace profile keeps the session. |

Do not build session cookies by signing them with the app's secret. It tests a cookie you made, not
the login the user gets, and it puts the secret in the transcript.

## Where the storage-state file lives

The file holds session cookies and tokens that can impersonate the account. Playwright's docs say to
keep it in `playwright/.auth` and add that directory to `.gitignore`.

```bash
AUTH_FILE=playwright/.auth/user.json
mkdir -p "$(dirname "$AUTH_FILE")"
git check-ignore -q "$AUTH_FILE" || echo "NOT IGNORED: $AUTH_FILE"
```

If it is not ignored, ask the user before editing `.gitignore`, or save outside the repo instead
(for example `${XDG_CACHE_HOME:-$HOME/.cache}/claude-skills/webapp-testing/auth/<repo>/user.json`).

## Save storage state: scripted login

Test credentials come from Google Secret Manager through the repo's `scripts/with-secrets.sh`
wrapper, which sets them for one child process. Read the wrapper to learn the variable names. Do not
echo the values, pass them as command-line arguments (they show up in `ps` and the transcript), or
write them to a file. Keep tracing and video off for this script so typed credentials are not
recorded.

```python
# save_auth.py
import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

BASE_URL = "http://localhost:5173"
AUTH_FILE = Path("playwright/.auth/user.json")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{BASE_URL}/login")
    page.get_by_label("Email").fill(os.environ["E2E_USER_EMAIL"])
    page.get_by_label("Password").fill(os.environ["E2E_USER_PASSWORD"])
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("button", name="Account")).to_be_visible()  # a signed-in-only element
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    context.storage_state(path=AUTH_FILE)
    browser.close()

print(f"Saved storage state to {AUTH_FILE}")
```

```bash
scripts/with-secrets.sh "$VENV/bin/python" save_auth.py
```

If the app keeps its auth token in IndexedDB (Firebase Auth does), call
`context.storage_state(path=AUTH_FILE, indexed_db=True)`. Storage state does not include
`sessionStorage`; Playwright's auth guide shows a manual workaround if the app needs it.

## Save storage state: manual login (SSO, 2FA)

The user signs in by hand in a headed window and the script saves the state once the app lands on a
signed-in page. Headed runs need full chromium: `"$VENV/bin/playwright" install chromium`.

```python
page.goto(f"{BASE_URL}/login")
page.wait_for_url(f"{BASE_URL}/dashboard**", timeout=300_000)  # five minutes for the user
context.storage_state(path=AUTH_FILE)
```

With the Playwright CLI installed: `playwright-cli open --headed <login-url>`, let the user sign in,
then `playwright-cli state-save "$AUTH_FILE"`.

## Reuse it

```python
context = browser.new_context(storage_state=AUTH_FILE)
```

Playwright MCP takes the same file with `--isolated --storage-state=<path>` in its server args.
Use the same host the state was saved from: cookies saved for `localhost` are not sent to
`127.0.0.1`.

## Verify auth before writing tests

One request takes seconds; a suite that silently runs against the login page wastes minutes. The
check prints only a status code.

Cookie sessions: request a protected route with the context's cookies and without following
redirects.

```python
response = context.request.get(f"{BASE_URL}/protected-page", max_redirects=0)
print(response.status)  # 200: proceed. 3xx to login, 401, 403: fix auth first.
```

Token-in-storage SPAs: the server answers 200 for every route, so the status proves nothing. Check in
the page instead.

```python
import re

page.goto(f"{BASE_URL}/protected-page")
expect(page).not_to_have_url(re.compile(r"/(login|signin)"))
expect(page.get_by_role("button", name="Account")).to_be_visible()
```

**Rule: do not write the full suite until one authenticated check passes.**

## If the session is rejected

1. Re-run the login script; sessions expire.
2. Confirm the base URL host matches the one used when saving.
3. Check for a secret mismatch between sources. The running app may use a different
   `SESSION_SECRET` than the code's fallback, because Vite and similar tools auto-load `.env` files.
   Compare fingerprints, never values; printing a secret puts it in the transcript.

```bash
# Print a short hash per source, not the secret:
for f in .env .env.local .env.development; do
  [[ -f "$f" ]] && printf '%s: %s\n' "$f" "$(sed -n 's/^SESSION_SECRET=//p' "$f" | shasum -a 256 | cut -c1-12)"
done
grep -l SESSION docker-compose.yml 2>/dev/null                 # which compose file sets it
grep -rl "SESSION_SECRET\|secrets:" app/lib/ --include="*.ts"  # which file has a code fallback
```

Different hashes mean the sources disagree. Report that as a finding; do not copy a value from one
source to another without the user.

## Never

- Commit, print, `cat`, paste, upload, or attach the storage-state file to a report or PR.
- Export credentials in the shell profile or write them into scripts, `.env`, or test data.
- Copy cookies or tokens out of the user's Chrome session into a Playwright context.
