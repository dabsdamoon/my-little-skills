# Upstream provenance — visual-explainer

- Source: https://github.com/nicobailon/visual-explainer
- Revision: `9d5f880b7e8e0a9a80c890b8e1bb6918b68481ad` (release `v0.15.0`).
- Imported path: `plugins/visual-explainer/`.
- Checked: 2026-11-18.
- Upstream author and copyright holder: Nico Bailon.
- License: MIT; the upstream root `LICENSE` is copied here byte for byte.
- Bundled Pele and Lucide notices: `kit/vendor/PELE-LICENSE`, preserved byte for byte (MIT and ISC).

## Local integration

The upstream skill payload, including its nested upstream plugin manifest, is
unchanged. The enclosing `design-skills` plugin publishes this skill for Claude
Code and Codex. The nested upstream manifest records upstream identity; it does
not register another marketplace or plugin. Upstream command templates stay in
`commands/`; this import adds no separate slash-command registrations.

`package.json` is local packaging: upstream dependency ranges and optional
Playwright support, private package, and executable paths relative to this skill.
Core HTML rendering needs no package installation. Optional MCP, PPTX, video,
and browser-check dependencies are available through this package; they are not
installed, registered, or enabled by importing the skill. No model API or
background service is configured.

The canonical copy is `skills/visual-explainer/`; its published mirror is
`plugins/design-skills/skills/visual-explainer/`. Keep both copies identical.
The import file hashes are in `UPSTREAM-FILES.json`. For future edits, compare
against the revision above, preserve `LICENSE` and `kit/vendor/PELE-LICENSE`,
and record meaningful changes here. Bundled third-party notices also apply when
redistributing their code in generated output.
