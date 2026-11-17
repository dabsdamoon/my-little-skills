# Assembled-screen semantic redundancy smoke check

Date: 2026-11-17. Base: `19d336394008aee4fe94caa64afa806c8e550229`.
Issue: [#55](https://github.com/dabsdamoon/my-little-skills/issues/55).

## Observation

The existing skill's output removed the English alias but kept a redundant desktop institution-name row below the same provider heading. The no-design-guidance output kept both alias and organization repetition. The revised skill's output removed those detail placements at desktop width, displayed provider identity locally only at the narrow viewport where the header identity disappears, and retained list identities, contact information and billing responsibility.

| Check | No design guidance | Existing skill | Revised skill |
| --- | --- | --- | --- |
| Desktop detail avoids purpose-free identity repetition | No: alias plus institution row | No: institution row remains | Yes |
| Different provider/branch rows stay identifiable | Yes | Yes | Yes |
| Compact header retains local provider context | Yes, with repeated metadata | Yes | Yes, conditional local identity |
| Choice group has an accessible name; ArrowDown selects10 | Yes | Yes | Yes |
| Detached dialog identifies provider and selected pass | Yes | Yes | Yes |
| Source fields, contact and billing scope preserved | Yes | Yes | Yes |

These are one observation per condition on one fixture, scored by the author without blinding. They do not establish a reliable improvement, causal effect, general usability, automatic skill selection, or behavior across models. The task's explicit returning-member/known-alias context narrows what counts as redundant; the same example does not justify removing useful acronym explanations elsewhere.

## Preserved inputs and outputs

- [brief.md](brief.md) and [fixture.html](fixture.html): task and starting UI.
- [prompt.txt](prompt.txt): exact stdin task used for the three conditions; it requests clearer hierarchy without naming which identity placements to delete.
- [rubric.md](rubric.md): criteria saved before skill edits. The standalone brief's terminal blank line was normalized for Git whitespace checks after execution; the actual stdin and its separator bytes remain unchanged in `prompt.txt`.
- [baseline-skill.md](baseline-skill.md), [revised-skill.md](revised-skill.md): complete instruction versions.
- `baseline-system.txt`, `control-system.txt`, `revised-system.txt`: supplied system messages; the control has no frontend-design text.
- [baseline.html](baseline.html), [control.html](control.html), [revised.html](revised.html): unedited generated documents. Markdown code fences would be stripped by the capture helper; these outputs needed no content repair.
- `*-run.json`: CLI version, resolved model, hashes, initialization metadata, usage and result. [manifest.json](manifest.json) ties the preserved inputs and outputs to SHA-256 hashes.
- [browser/](browser/): rendered screenshots, accessibility snapshots and interaction-check records.

## Execution and context boundary

Each condition used one fresh Claude Code2.1.326 process and one model turn, resolving `claude-sonnet-5-5`, with the existing subscription login. Working directories were separate disposable directories outside repository ancestry. Commands used `--setting-sources '' --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --tools '' --no-session-persistence --no-chrome`, explicit system text, and settings disabling hooks and auto memory. The stdin prompt was the preserved `prompt.txt`. No `--bare` or API key was used.

Initialization reports tools[], skills[] and mcp_servers[] for all conditions. The same Orca agent-view plugin and four built-in plugins remain loaded; these are listed in every run record. This is a no-frontend-guidance condition, not proof of a sterile platform prompt. Managed/built-in policy and model training remain outside this comparison. The first capture helper incorrectly asserted that no plugins at all would load; generation itself succeeded and its outputs were retained. No extra model runs were used to remove that caveat.

## Targeted visible-label retention check

All three general-refinement outputs kept the legend visible. They therefore cannot demonstrate behavior after a model removes a visible label. One additional one-turn call used the revised guidance and [legend-edit-prompt.txt](legend-edit-prompt.txt), asking only to hide “구매할 횟수권” visually in the already generated interface. This is a different task, not an additional comparison sample.

[legend-edit.html](legend-edit.html) differs from `revised.html` only by a clipping-style rule. At both viewport sizes, browser accessibility snapshots still contain group “구매할 횟수권”; radios remain named, ArrowDown selects10, and the dialog displays the selected pass. The screenshot confirms that the legend is visually absent. No author edits were made to generated HTML or the live DOM to achieve this result.

## Browser procedure

The author used Orca's native browser at1440×1000 and390×844 CSS viewports. Complete accessibility snapshots identify the actual group name, provider rows and dialog context. Real focus/ArrowDown/Enter actions select the10-session pass and open the dialog. Closing and returning from the dialog is checked before changing viewport. Background content is absent from the modal accessibility tree; source data is checked separately in each document. Geometry checks found no horizontal overflow. Screenshots were opened and inspected; geometry alone was not treated as visual-quality evidence. A stitched baseline mobile full-page capture was discarded; `browser/baseline-mobile-viewport.png` supplies the directly captured mobile identity view, alongside complete accessibility snapshots. Other full-page images are supplemental.

An early control observation sampled the accessibility tree before the dialog's close handler restored inert content. The observer was changed to wait for `header:not([inert])` rather than adding a sleep or repairing the generated document, and the same output then passed. The initial short tree is retained as `browser/control-mobile-after-close-issue.ax.txt`. This is a browser-observation timing correction, not another model sample.

## Budget and limits

Four successful one-turn subscription responses total: three comparison conditions plus the narrow label-edit check. Their combined SDK API-equivalent cost field is approximately$0.19953; this is a usage metric, not an invoice or a guarantee about account extra-usage settings. There was no API-key fallback. Browser inspection and repository checks call no model.

English instructions and Korean examples are authoring choices, not evidence of model adherence by themselves. The fixture resembles the reported clinic case, so this does not establish transfer to unfamiliar domains. The unfamiliar-acronym retention case is explicit guidance but was not separately exercised. No repeated sampling, blind scoring, screen-reader user study, automatic trigger test or fresh-install test was performed. Issue #47's structural-diversity evaluation remains separate.

## Distribution

Canonical and plugin entrypoint/notice are synchronized; both plugin manifests move1.1.2→1.1.3. Existing `check_distribution.py`, tracked-blob comparison, explicit version comparison and `git diff --check` are used. Full repository Python verification:146 passed,10 subtests passed. This branch prepares an update; it does not refresh the device's installed design-skills1.1.2 cache or claim that1.1.3 is already published on main.
