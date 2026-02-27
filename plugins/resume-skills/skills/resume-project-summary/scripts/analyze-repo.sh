#!/bin/bash
# Repository Analysis Script for Resume Project Summary
# Extracts key information from a codebase for project summary generation

set -e

REPO_PATH="${1:-.}"

echo "=== Repository Analysis for Resume Project Summary ==="
echo "Repository: $REPO_PATH"
echo ""

# Basic info
echo "## Basic Info"
echo ""

if [ -f "$REPO_PATH/package.json" ]; then
    echo "### package.json"
    echo "\`\`\`json"
    cat "$REPO_PATH/package.json" | head -50
    echo "\`\`\`"
    echo ""
fi

if [ -f "$REPO_PATH/requirements.txt" ]; then
    echo "### requirements.txt"
    echo "\`\`\`"
    cat "$REPO_PATH/requirements.txt"
    echo "\`\`\`"
    echo ""
fi

if [ -f "$REPO_PATH/pyproject.toml" ]; then
    echo "### pyproject.toml"
    echo "\`\`\`toml"
    cat "$REPO_PATH/pyproject.toml" | head -50
    echo "\`\`\`"
    echo ""
fi

# Documentation
echo "## Documentation"
echo ""

for doc in README.md CLAUDE.md docs/README.md; do
    if [ -f "$REPO_PATH/$doc" ]; then
        echo "### $doc"
        echo "\`\`\`markdown"
        cat "$REPO_PATH/$doc" | head -100
        echo "\`\`\`"
        echo ""
    fi
done

# Directory structure
echo "## Directory Structure"
echo "\`\`\`"
if command -v tree &> /dev/null; then
    tree -L 2 -d "$REPO_PATH/src" 2>/dev/null || tree -L 2 -d "$REPO_PATH" 2>/dev/null | head -50
else
    ls -la "$REPO_PATH/src" 2>/dev/null || ls -la "$REPO_PATH" | head -30
fi
echo "\`\`\`"
echo ""

# Git info
echo "## Git Info"
if [ -d "$REPO_PATH/.git" ]; then
    echo ""
    echo "### Recent Commits"
    echo "\`\`\`"
    git -C "$REPO_PATH" log --oneline -10 2>/dev/null || echo "Unable to read git log"
    echo "\`\`\`"
    echo ""

    echo "### Contributors"
    echo "\`\`\`"
    git -C "$REPO_PATH" shortlog -sn --all 2>/dev/null | head -10 || echo "Unable to read contributors"
    echo "\`\`\`"
fi
echo ""

# Tech stack detection
echo "## Detected Tech Stack"
echo ""

# Frontend detection
if [ -f "$REPO_PATH/package.json" ]; then
    echo "### Frontend"
    echo ""

    if grep -q '"react"' "$REPO_PATH/package.json" 2>/dev/null; then
        echo "- React"
    fi
    if grep -q '"vue"' "$REPO_PATH/package.json" 2>/dev/null; then
        echo "- Vue.js"
    fi
    if grep -q '"next"' "$REPO_PATH/package.json" 2>/dev/null; then
        echo "- Next.js"
    fi
    if grep -q '"vite"' "$REPO_PATH/package.json" 2>/dev/null; then
        echo "- Vite"
    fi
    if grep -q '"typescript"' "$REPO_PATH/package.json" 2>/dev/null; then
        echo "- TypeScript"
    fi
    if grep -q '"tailwindcss"' "$REPO_PATH/package.json" 2>/dev/null; then
        echo "- Tailwind CSS"
    fi
    if grep -q '"shadcn"' "$REPO_PATH/package.json" 2>/dev/null || grep -q '"@radix-ui"' "$REPO_PATH/package.json" 2>/dev/null; then
        echo "- shadcn/ui (Radix)"
    fi
    echo ""
fi

# Backend detection
echo "### Backend/Database"
echo ""
if grep -q '"@supabase"' "$REPO_PATH/package.json" 2>/dev/null; then
    echo "- Supabase"
fi
if grep -q '"firebase"' "$REPO_PATH/package.json" 2>/dev/null; then
    echo "- Firebase"
fi
if grep -q '"prisma"' "$REPO_PATH/package.json" 2>/dev/null; then
    echo "- Prisma ORM"
fi
if [ -f "$REPO_PATH/requirements.txt" ]; then
    if grep -q "fastapi" "$REPO_PATH/requirements.txt" 2>/dev/null; then
        echo "- FastAPI"
    fi
    if grep -q "django" "$REPO_PATH/requirements.txt" 2>/dev/null; then
        echo "- Django"
    fi
    if grep -q "flask" "$REPO_PATH/requirements.txt" 2>/dev/null; then
        echo "- Flask"
    fi
fi
echo ""

# Component count
echo "## Code Statistics"
echo ""

if [ -d "$REPO_PATH/src" ]; then
    tsx_count=$(find "$REPO_PATH/src" -name "*.tsx" 2>/dev/null | wc -l | tr -d ' ')
    ts_count=$(find "$REPO_PATH/src" -name "*.ts" -not -name "*.d.ts" 2>/dev/null | wc -l | tr -d ' ')
    py_count=$(find "$REPO_PATH/src" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')

    echo "- TSX files: $tsx_count"
    echo "- TypeScript files: $ts_count"
    echo "- Python files: $py_count"
fi

# Find routes/pages
echo ""
echo "## Routes/Pages (potential user personas)"
echo ""

if [ -d "$REPO_PATH/src/pages" ]; then
    echo "### src/pages/"
    ls -1 "$REPO_PATH/src/pages" 2>/dev/null | head -20
fi

if [ -d "$REPO_PATH/src/routes" ]; then
    echo "### src/routes/"
    ls -1 "$REPO_PATH/src/routes" 2>/dev/null | head -20
fi

# Dashboard components (user personas)
echo ""
echo "## Dashboard Components (user personas)"
echo ""
find "$REPO_PATH/src" -type d -iname "*dashboard*" 2>/dev/null | head -10

echo ""
echo "=== Analysis Complete ==="
