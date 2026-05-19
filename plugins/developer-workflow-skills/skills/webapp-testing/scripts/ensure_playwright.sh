#!/usr/bin/env bash
# Idempotently bootstrap a dedicated venv for the webapp-testing skill.
#
# Why: the skill needs Python's `playwright` package plus the chromium browser
# binary. We do NOT want to pollute the user's system Python, project venvs,
# or require the user to manually set things up — so we create a single
# user-scoped venv that any project on this machine can reuse.
#
# Output: prints the venv root path on stdout. Diagnostics go to stderr.
#
# Usage:
#   VENV="$(scripts/ensure_playwright.sh)" || exit 1
#   "$VENV/bin/python" your_test.py
#
# Environment overrides:
#   PLAYWRIGHT_VERSION   Pin a different playwright version (default: 1.49.1)
#   WEBAPP_TESTING_VENV  Override the venv path entirely
#   XDG_CACHE_HOME       Standard XDG cache root (default: $HOME/.cache)
#
# Idempotency:
#   - If the venv is present and has the requested playwright version
#     installed, this script exits in <100ms with no work done.
#   - First-run takes ~30-60s (pip install playwright + chromium download).
#   - Re-runs after a Python version upgrade trigger a full rebuild.

set -euo pipefail

PLAYWRIGHT_VERSION="${PLAYWRIGHT_VERSION:-1.60.0}"
CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
VENV="${WEBAPP_TESTING_VENV:-$CACHE_HOME/claude-skills/webapp-testing/venv}"

log() { printf '[ensure_playwright] %s\n' "$*" >&2; }

# 1. Python 3.9+ is required. We don't hard-cap the upper bound — pip's resolver
# decides whether the requested playwright version has a compatible wheel.
if ! command -v python3 >/dev/null 2>&1; then
  log "ERROR: python3 not found. Install Python 3.9+ before using this skill."
  exit 1
fi

py_version="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
py_major="$(python3 -c 'import sys; print(sys.version_info.major)')"
py_minor="$(python3 -c 'import sys; print(sys.version_info.minor)')"
if [ "$py_major" -lt 3 ] || { [ "$py_major" = "3" ] && [ "$py_minor" -lt 9 ]; }; then
  log "ERROR: Playwright requires Python 3.9+; found $py_version."
  exit 1
fi

# 2. Create the venv if it's missing or its python is broken/stale.
needs_create=0
if [ ! -x "$VENV/bin/python" ]; then
  needs_create=1
elif ! "$VENV/bin/python" -c 'import sys' >/dev/null 2>&1; then
  log "Existing venv at $VENV is broken; rebuilding."
  rm -rf "$VENV"
  needs_create=1
else
  # If the system python's minor version changed, the venv's symlinks are stale.
  venv_py_version="$("$VENV/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "")"
  if [ "$venv_py_version" != "$py_version" ]; then
    log "venv was built for Python $venv_py_version, host now has $py_version; rebuilding."
    rm -rf "$VENV"
    needs_create=1
  fi
fi

if [ "$needs_create" = "1" ]; then
  mkdir -p "$(dirname "$VENV")"
  log "Creating venv at $VENV"
  python3 -m venv "$VENV"
fi

# 3. Install playwright if the pinned version is missing or different.
current=""
if [ -x "$VENV/bin/pip" ]; then
  current="$("$VENV/bin/pip" show playwright 2>/dev/null | awk '/^Version:/{print $2}')" || true
fi

if [ "$current" != "$PLAYWRIGHT_VERSION" ]; then
  log "Installing playwright==$PLAYWRIGHT_VERSION (current: ${current:-none})"
  "$VENV/bin/pip" install --quiet --upgrade pip >&2
  "$VENV/bin/pip" install --quiet "playwright==$PLAYWRIGHT_VERSION" >&2
  log "Installing chromium browser (this may take a minute on first run)"
  "$VENV/bin/playwright" install chromium >&2
fi

# 4. Confirm chromium is actually launchable. If not, try install once more.
if ! "$VENV/bin/python" - <<'PY' >/dev/null 2>&1
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    b.close()
PY
then
  log "Chromium launch failed; re-running 'playwright install chromium'"
  "$VENV/bin/playwright" install chromium >&2
  if ! "$VENV/bin/python" - <<'PY' >/dev/null 2>&1
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    b.close()
PY
  then
    log "ERROR: chromium still cannot launch after reinstall. Check system dependencies."
    exit 1
  fi
fi

# Success. Emit the venv path on stdout for the caller.
echo "$VENV"
