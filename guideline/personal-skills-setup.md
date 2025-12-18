# Setting Up Personal Skills via Symlink

This document describes how to make the skills in this repository available as personal skills in Claude Code using the symlink approach.

## Overview

Claude Code looks for personal skills in `~/.claude/skills/`. By creating a symbolic link from this location to the `skills/` directory in this repository, all skills become available across all projects.

## Implementation

```bash
# Create symlink (run once)
ln -s /Users/dabsdamoon/projects/anthropic-skills/skills ~/.claude/skills
```

## Verification

```bash
# Check symlink exists
ls -la ~/.claude/skills
# Expected output:
# ~/.claude/skills -> /Users/dabsdamoon/projects/anthropic-skills/skills

# List available skills
ls ~/.claude/skills/
```

## Notes on Symlink Support

**Official documentation status**: As of December 2025, symlink support for skills directories is not explicitly documented in the official Claude Code documentation.

**Evidence of support**:
- Changelog v1.0.82: "Fixed an issue where skill files inside symlinked skill directories could become circular symlinks"

**Known issues**:
- GitHub Issue #764: Symlinked `~/.claude` directory may have detection issues
- GitHub Issue #1388: Symbolic links not indexed by file picker
- GitHub Issue #10573: Symlink support for slash commands broken in some versions

## Alternative Approaches

If the symlink approach doesn't work reliably:

### Option A: Direct Clone
```bash
git clone <repo-url> ~/.claude/skills
```

### Option B: Individual Symlinks
```bash
mkdir -p ~/.claude/skills
ln -s /path/to/repo/skills/pdf ~/.claude/skills/pdf
ln -s /path/to/repo/skills/xlsx ~/.claude/skills/xlsx
# ... repeat for each skill
```

### Option C: Copy with Sync Script
```bash
# Manual sync when needed
rsync -av /path/to/repo/skills/ ~/.claude/skills/
```

## Updating Skills

Since the symlink points to this repository, any changes made here are immediately available to Claude Code after restarting the CLI.

```bash
# Edit a skill
vim skills/pdf/SKILL.md

# Changes take effect on next Claude Code session
claude
```

## Removing the Setup

```bash
# Remove the symlink (does not delete the source files)
rm ~/.claude/skills
```
