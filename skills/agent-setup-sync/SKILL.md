---
name: agent-setup-sync
description: Keeps Claude Code and Codex skills and plugins the same on every machine by recording decisions in the dotfiles baseline (agents/baseline.json) and applying them with agent-sync. Use when asked to turn a skill or plugin on or off for good, set up agents on a new machine, sync or audit the agent setup, clean up duplicate or stale skills, or find out why a skill is not being picked up. Not for writing a new skill (skill-creator) or moving one repository's .claude config to another (claude-config-migrator).
---

# Agent Setup Sync

One file decides what Claude Code and Codex load: `agents/baseline.json` in the user's dotfiles repository (`~/.dotfiles`; `$AGENT_BASELINE` overrides). `agent-sync`, which the dotfiles installer links into `~/.local/bin`, compares this machine with the baseline and applies the difference.

Change the baseline, not the machine. A change made only through `/plugin`, `codex plugin`, `skillOverrides`, or by moving skill folders lasts until the next machine or reinstall.

## Before starting

Check that `command -v agent-sync` succeeds and the baseline file exists. If either is missing, the dotfiles are not installed on this machine: tell the user to clone them and run the installer. Do not recreate the script or the baseline from memory.

## Workflow

1. **Audit.** Run `agent-sync audit` (`--json` for parsing). Exit code 0 means no drift.
2. **Explain the drift** in plain words. Each line has a kind:

   | Kind | Meaning |
   |---|---|
   | `claude-marketplace`, `codex-marketplace` | A marketplace the baseline needs is not registered |
   | `claude-install`, `codex-install` | A baseline plugin is not installed |
   | `claude-enable`, `codex-enable` | A plugin's on/off state differs from the baseline |
   | `claude-skill-override` | A non-plugin skill's `skillOverrides` value differs |
   | `codex-pinned-skill` | A third-party skill is missing or not at the pinned commit |
   | `codex-legacy-skill` | A folder in `~/.codex/skills`, which Codex no longer documents |
   | `*-duplicate` | A loose skill, or a command symlink in `~/.claude/commands`, duplicates one an enabled plugin already provides |
   | `project-rule` | A project matches a rule (such as Vercel) but lacks its local plugin setting |

   Lines marked `[manual]` need a person, such as a `.claude/settings.local.json` that the project tracks in git. Notes list things enabled here that the baseline does not mention; ask whether to add them to the baseline or turn them off. Plugins from a marketplace on a local path are left out of the notes: they exist only on this machine and cannot go in the baseline.

3. **Record decisions in the baseline** when the user wants a lasting change:
   - Claude plugin: `claude.plugins["name@marketplace"]` set to `true` or `false`. Keep `false` rather than deleting the key when a project rule may enable the plugin locally.
   - Claude skill that is not from a plugin (gstack and similar): `claude.skillOverrides[name]` set to `"off"`, `"user-invocable-only"`, or `"name-only"`. Plugin skills cannot be overridden this way; turn off the plugin instead.
   - Codex plugin: `codex.plugins["name@marketplace"]`.
   - Third-party skill published only as a folder: `codex.skills[name] = {"repo", "ref", "path"}`. Pin `ref` to a full commit SHA (`gh api repos/<repo>/commits/<tag> -q .sha`), never a branch.
   - Rule by project type: an entry in `projects.rules` with `ifAnyExists` markers and the `claudeLocalPlugins` to enable.
   - Skills another tool installs and updates itself (gstack, Orca): list them in `externalSkills` so agent-sync leaves them alone.

   Show the baseline diff to the user before applying.
4. **Dry run.** `agent-sync apply` prints the plan without changing anything. Anything it replaces moves to `~/.local/state/agent-sync/backup/<timestamp>/`, along with a copy of each settings file before its first edit; the only deletions are symlinks that duplicate a plugin skill or command.
5. **Apply** with `agent-sync apply --yes` once the user agrees, then run `agent-sync audit` again. `--yes` first refreshes the marketplaces and updates installed baseline plugins (`claude plugin marketplace update`, `claude plugin update`, `codex plugin marketplace upgrade`), then recomputes the plan, so it can do more than the dry run showed. It does not update a plugin whose `package.json` lists dependencies, because `claude plugin update` would install those npm packages; it prints the plugin instead. Review the packages under the user's package-safety rule before running that update by hand. A plugin's skills are only visible after it is installed, so a second pass can reveal duplicates.
6. **Say when changes take effect.** Claude Code loads plugins at session start (`/reload-plugins` in an open session). Codex reads its config when it starts.
7. **Hand back the commit.** The baseline is in a git repository. Do not commit or push unless asked; name the changed file and suggest committing it so other machines pick it up.

## Judgment agent-sync cannot make

Check these when asked to clean up, or when a skill is not picked up or misbehaves:

- **Collisions.** Two enabled skills claim the same request, for example two TDD or PR skills, or a description that says "use this instead of ...". Keep one per job, preferring the one that agrees with the user's own rules.
- **Description budget.** Claude Code fits skill descriptions into about 1% of the context window (`skillListingBudgetFraction`) and drops the descriptions of rarely used skills first. Codex uses 2% (`skills.max_context_tokens`). `/skill-doctor` in Claude Code shows truncation. A large plugin that is rarely used is the usual cause.
- **Staleness.** `apply --yes` updates plugins, but a pinned skill stays at its `ref` until the baseline moves it. Compare a pinned `ref` with upstream (`gh api repos/<repo>/commits/<branch> -q .commit.committer.date`, release notes) and read what changed before moving the pin.
- **Quality before adding.** Read a third-party skill in full before it goes into the baseline. Look for discouraged APIs, mocks of project-owned modules, coverage quotas, automatic commits, and instructions that contradict the user's CLAUDE.md. When a skill needs changes, vendor a fixed copy into the user's marketplace instead of pinning it.

## Facts this skill relies on

- Codex reads user skills from `~/.agents/skills`; `~/.codex/skills` is not in its documented locations, so agent-sync moves everything except `.system` out of it.
- Listing a plugin in `enabledPlugins` does not download it; agent-sync runs `claude plugin install` and `codex plugin add` for missing plugins.
- agent-sync never runs a package manager itself. Its network use is marketplace refreshes, plugin installs and updates, and downloading pinned skills from `codeload.github.com`.
- `claude plugin install` and `claude plugin update` install the npm packages a plugin's lockfile lists, with install scripts disabled (`bun install --frozen-lockfile --ignore-scripts` or `npm ci --ignore-scripts`, read from Claude Code 2.1.310). Before approving a dry run that installs a new plugin, check the plugin's `package.json`.
