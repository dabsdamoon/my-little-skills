#!/usr/bin/env bash

# Check release divergence for the production-pointer workflow.
# Safe to run locally or in CI. It does not push or modify refs.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

MAX_COMMITS="${MAX_COMMITS:-10}"
MAX_DAYS="${MAX_DAYS:-7}"

warn=0

echo -e "${BLUE}Fetching origin/main and origin/production...${NC}"
git fetch origin main --quiet
git fetch origin production --quiet 2>/dev/null || true

if ! git rev-parse --verify --quiet origin/main >/dev/null; then
  echo -e "${RED}origin/main not found.${NC}"
  exit 1
fi

if ! git rev-parse --verify --quiet origin/production >/dev/null; then
  echo -e "${YELLOW}origin/production not found yet.${NC}"
  echo "First release should create it from origin/main."
  exit 0
fi

MAIN_SHA="$(git rev-parse origin/main)"
PROD_SHA="$(git rev-parse origin/production)"

echo "origin/main:       ${MAIN_SHA:0:7}"
echo "origin/production: ${PROD_SHA:0:7}"

if ! git merge-base --is-ancestor "$PROD_SHA" "$MAIN_SHA"; then
  echo -e "${RED}Invariant violation: origin/production is not reachable from origin/main.${NC}"
  echo "A production hotfix may not have been back-ported to main. Investigate before releasing."
  exit 1
fi

echo -e "${GREEN}[OK] origin/production is reachable from origin/main.${NC}"

PENDING_COUNT="$(git rev-list --count origin/production..origin/main)"
echo "Pending commits from main to production: ${PENDING_COUNT}"

if [ "$PENDING_COUNT" -gt 0 ]; then
  echo ""
  echo "Pending commits:"
  git log --oneline --decorate origin/production..origin/main | head -50

  OLDEST_TS="$(git log --reverse --format=%ct origin/production..origin/main | head -1)"
  NOW_TS="$(date +%s)"
  AGE_DAYS="$(( (NOW_TS - OLDEST_TS) / 86400 ))"
  echo ""
  echo "Oldest unreleased commit age: ${AGE_DAYS} day(s)"

  if [ "$PENDING_COUNT" -gt "$MAX_COMMITS" ]; then
    echo -e "${YELLOW}Warning: pending commits (${PENDING_COUNT}) exceed MAX_COMMITS=${MAX_COMMITS}.${NC}"
    warn=1
  fi
  if [ "$AGE_DAYS" -gt "$MAX_DAYS" ]; then
    echo -e "${YELLOW}Warning: oldest pending commit age (${AGE_DAYS} days) exceeds MAX_DAYS=${MAX_DAYS}.${NC}"
    warn=1
  fi
else
  echo -e "${GREEN}[OK] production is up to date with main.${NC}"
fi

if [ "$warn" -eq 1 ]; then
  echo ""
  echo "Review whether main should be released or intentionally held."
fi
