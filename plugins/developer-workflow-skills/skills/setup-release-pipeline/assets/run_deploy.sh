#!/usr/bin/env bash

# =============================================================================
# Production Release
#
# Opinionated workflow: the host (Vercel/Netlify/Render/etc.) watches the
# `production` branch. `main` is the canonical latest-code / release-candidate
# branch; it may be ahead of what users currently see. To release:
#   1. Verify local `main` is clean and equal to origin/main.
#   2. Verify origin/production is reachable from origin/main.
#   3. Show pending-release commits and file summary.
#   4. Move production to main HEAD with --force-with-lease.
#   5. Verify remote production moved, then create/push an annotated vX.Y.Z tag.
#
# The production branch movement triggers the host production deploy. The tag is
# release metadata unless this repo has separate tag-triggered automation.
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TAG_PREFIX="v"
TAG_VERSION="${1:-}"
TAG_PATTERN="v[0-9]*.[0-9]*.[0-9]*"

# Edit these two lines for your project. The script works without them but the
# closing banner will be less useful.
PROJECT_URL="{{PROJECT_URL}}"                 # e.g. https://myapp.vercel.app
HOST_DASHBOARD_URL="{{HOST_DASHBOARD_URL}}"   # e.g. https://vercel.com/<owner>/<project>/deployments

die() {
  echo -e "${RED}Error: $*${NC}" >&2
  exit 1
}

section() {
  echo ""
  echo -e "${BLUE}$*${NC}"
  echo -e "${BLUE}$(printf '%*s' "${#*}" '' | tr ' ' '-')${NC}"
}

short() {
  git rev-parse --short "$1"
}

remote_ref_exists() {
  git rev-parse --verify --quiet "$1" >/dev/null
}

remote_tag_exists() {
  git ls-remote --exit-code --tags origin "refs/tags/$1" >/dev/null 2>&1
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Production Release${NC}"
echo -e "${BLUE}========================================${NC}"
echo "This workflow is simple but opinionated. Read the trade-offs before cutover."
echo ""

CURRENT_BRANCH="$(git branch --show-current)"
[ "$CURRENT_BRANCH" = "main" ] || die "releases must be cut from main. Current branch: ${CURRENT_BRANCH}"
echo -e "${GREEN}[OK] Current branch: main${NC}"

if [ -n "$(git status --porcelain)" ]; then
  git status --short
  die "working directory is not clean. Commit or stash changes before releasing."
fi
echo -e "${GREEN}[OK] Working directory clean${NC}"

echo -e "${BLUE}Fetching origin/main, origin/production, and tags...${NC}"
git fetch origin main --tags --quiet
git fetch origin production --quiet 2>/dev/null || true

LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_MAIN_SHA="$(git rev-parse origin/main)"

if [ "$LOCAL_SHA" != "$REMOTE_MAIN_SHA" ]; then
  echo "Local:  $(short HEAD)"
  echo "Remote: $(short origin/main)"
  die "local main is not up to date with origin/main. Run: git pull --ff-only origin main"
fi
echo -e "${GREEN}[OK] Up to date with origin/main ($(short origin/main))${NC}"

PRODUCTION_EXISTS=0
if remote_ref_exists origin/production; then
  PRODUCTION_EXISTS=1
  REMOTE_PROD_SHA="$(git rev-parse origin/production)"
  echo -e "${BLUE}origin/production: $(short origin/production)${NC}"
  echo -e "${BLUE}origin/main:       $(short origin/main)${NC}"

  if ! git merge-base --is-ancestor "$REMOTE_PROD_SHA" "$REMOTE_MAIN_SHA"; then
    echo -e "${RED}origin/production has commits that are not on origin/main.${NC}"
    echo -e "${RED}This violates the 'production must be reachable from main' rule.${NC}"
    echo -e "${RED}Likely cause: a hotfix was applied to production without being back-ported.${NC}"
    exit 1
  fi
  echo -e "${GREEN}[OK] origin/production is reachable from origin/main${NC}"
else
  REMOTE_PROD_SHA=""
  echo -e "${YELLOW}Note: origin/production does not exist yet. It will be created from main.${NC}"
fi

section "Release status"
if [ "$PRODUCTION_EXISTS" -eq 1 ]; then
  PENDING_COUNT="$(git rev-list --count origin/production..origin/main)"
  echo "Pending commits from main to production: ${PENDING_COUNT}"
  if [ "$PENDING_COUNT" -gt 0 ]; then
    OLDEST_PENDING="$(git log --reverse --format='%ci %h %s' origin/production..origin/main | head -1)"
    echo "Oldest pending commit: ${OLDEST_PENDING}"
  fi
else
  PENDING_COUNT="$(git rev-list --count origin/main)"
  echo "production branch does not exist; first release will publish origin/main."
  echo "Commits in origin/main: ${PENDING_COUNT}"
fi

section "Previous release tags"
TAGS="$(git tag -l "$TAG_PATTERN" --sort=-version:refname | head -10)"
if [ -z "$TAGS" ]; then
  echo -e "${YELLOW}No previous release tags found.${NC}"
  echo -e "${YELLOW}Suggested first tag: v0.1.0${NC}"
else
  echo "$TAGS"
  LATEST="$(echo "$TAGS" | head -1)"
  LATEST_VER="${LATEST#"$TAG_PREFIX"}"
  IFS='.' read -r MAJOR MINOR PATCH <<< "$LATEST_VER"
  SUGGESTED="${MAJOR}.${MINOR}.$((PATCH + 1))"
  echo ""
  echo -e "${YELLOW}Suggested next version: ${SUGGESTED}${NC}"
fi

if [ -z "$TAG_VERSION" ]; then
  echo ""
  echo -e "${YELLOW}To cut a release, run: ./run_deploy.sh <version>${NC}"
  echo "Example: ./run_deploy.sh 0.1.0"
  exit 0
fi

[[ "$TAG_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "invalid version format. Expected x.y.z, received: ${TAG_VERSION}"
FULL_TAG="${TAG_PREFIX}${TAG_VERSION}"

if git rev-parse --verify --quiet "refs/tags/${FULL_TAG}" >/dev/null; then
  die "local tag ${FULL_TAG} already exists. Choose another version or delete the local tag if it was created by a failed previous run."
fi
if remote_tag_exists "$FULL_TAG"; then
  die "remote tag ${FULL_TAG} already exists on origin. Choose another version."
fi
echo -e "${GREEN}[OK] Tag available: ${FULL_TAG}${NC}"

section "Release diff summary"
if [ "$PRODUCTION_EXISTS" -eq 1 ]; then
  RANGE="origin/production..origin/main"
  echo "Commit range: ${RANGE}"
else
  RANGE="origin/main"
  echo "First production release from origin/main"
fi

echo ""
echo "Commits to ship:"
if [ "$PRODUCTION_EXISTS" -eq 1 ]; then
  if [ "$(git rev-list --count "$RANGE")" -eq 0 ]; then
    echo -e "${YELLOW}No new commits between origin/production and origin/main.${NC}"
  else
    git log --oneline --decorate --no-merges "$RANGE" | head -50
  fi
else
  git log --oneline --decorate --no-merges origin/main | head -50
fi

echo ""
echo "Files changed since current production:"
if [ "$PRODUCTION_EXISTS" -eq 1 ]; then
  if [ "$(git rev-list --count "$RANGE")" -eq 0 ]; then
    echo -e "${YELLOW}No file changes; production already points at main.${NC}"
  else
    git diff --stat origin/production..origin/main
  fi
else
  git show --stat --oneline --summary origin/main | head -80
fi

section "Planned release actions"
echo "  1. Move origin/production → $(short origin/main) (main HEAD)"
echo "     This triggers the host's production deployment."
echo "  2. Verify origin/production now equals origin/main."
echo "  3. Create annotated tag: ${FULL_TAG}"
echo "  4. Push tag to origin and verify the remote tag."
echo ""
echo -e "${YELLOW}Note:${NC} The branch move is the deploy trigger. The tag is release metadata unless"
echo "this project also has separate tag-triggered automation."
echo ""

read -r -p "Proceed with release? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo -e "${YELLOW}Release cancelled.${NC}"
  exit 0
fi

echo ""
if [ "$PRODUCTION_EXISTS" -eq 1 ]; then
  echo -e "${BLUE}Moving origin/production to $(short origin/main)...${NC}"
  git push --force-with-lease=production:"$REMOTE_PROD_SHA" \
    origin "${REMOTE_MAIN_SHA}:refs/heads/production"
else
  echo -e "${BLUE}Creating origin/production from $(short origin/main)...${NC}"
  git push origin "${REMOTE_MAIN_SHA}:refs/heads/production"
fi

echo -e "${BLUE}Verifying remote production pointer...${NC}"
git fetch origin production --quiet
NEW_REMOTE_PROD_SHA="$(git rev-parse origin/production)"
if [ "$NEW_REMOTE_PROD_SHA" != "$REMOTE_MAIN_SHA" ]; then
  echo "Expected: ${REMOTE_MAIN_SHA}"
  echo "Actual:   ${NEW_REMOTE_PROD_SHA}"
  die "origin/production verification failed after push. Investigate before tagging."
fi
echo -e "${GREEN}[OK] origin/production now equals origin/main ($(short origin/main)) — host deploy triggered${NC}"

echo ""
echo -e "${BLUE}Creating tag ${FULL_TAG}...${NC}"
git tag -a "$FULL_TAG" -m "Release ${TAG_VERSION}"

echo -e "${BLUE}Pushing tag to origin...${NC}"
if ! git push origin "$FULL_TAG"; then
  echo -e "${RED}Tag push failed after production moved.${NC}"
  echo "Recovery options:"
  echo "  1. Retry: git push origin ${FULL_TAG}"
  echo "  2. If the local tag is wrong: git tag -d ${FULL_TAG}"
  echo "Production may already be deploying from $(short origin/main)."
  exit 1
fi

if ! remote_tag_exists "$FULL_TAG"; then
  die "remote tag verification failed for ${FULL_TAG}. Retry: git push origin ${FULL_TAG}"
fi
echo -e "${GREEN}[OK] Remote tag verified: ${FULL_TAG}${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Released: ${FULL_TAG}${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
if [ "$HOST_DASHBOARD_URL" != "{{HOST_DASHBOARD_URL}}" ] && [ -n "$HOST_DASHBOARD_URL" ]; then
  echo "Watch the host build:"
  echo "  $HOST_DASHBOARD_URL"
  echo ""
fi
if [ "$PROJECT_URL" != "{{PROJECT_URL}}" ] && [ -n "$PROJECT_URL" ]; then
  echo "Production URL (after build completes):"
  echo "  $PROJECT_URL"
fi
