# Licensing

This is a mixed-license collection. The maintainer's original skills listed
below are MIT licensed. Each skill carries its own `LICENSE.txt`, so the grant
travels with a standalone copy and the published plugin copy. Copyright notices
use the maintainer's public identity, `dabsdamoon`.

Original integration code in the first-party plugin packages that carry a root
`LICENSE.txt` is MIT licensed too. This grant covers only the maintainer's own
contributions. Third-party source, assets, fonts, marks, quotations, dependencies,
and their existing notices retain their respective terms. There is no blanket
relicensing of all material in this repository.

## Maintainer-authored skills

| Skill | Distributed directory or directories |
|---|---|
| `agent-setup-sync` | `plugins/config-skills/skills/agent-setup-sync`<br>`skills/agent-setup-sync` |
| `analytique` | `plugins/analysis-skills/skills/analytique` |
| `building-decision-reports` | `plugins/analysis-skills/skills/building-decision-reports`<br>`skills/building-decision-reports` |
| `building-health-evidence-reports` | `plugins/analysis-skills/skills/building-health-evidence-reports`<br>`skills/building-health-evidence-reports` |
| `capture-customer-outcomes` | `plugins/fde-estimation-skills/skills/capture-customer-outcomes` |
| `claude-config-migrator` | `plugins/config-skills/skills/claude-config-migrator`<br>`skills/claude-config-migrator` |
| `collect-as-built-evidence` | `plugins/fde-estimation-skills/skills/collect-as-built-evidence` |
| `debugging-retrospective` | `plugins/developer-workflow-skills/skills/debugging-retrospective`<br>`skills/debugging-retrospective` |
| `define-estimation-policy` | `plugins/fde-estimation-skills/skills/define-estimation-policy` |
| `deploy-check` | `plugins/developer-workflow-skills/skills/deploy-check`<br>`skills/deploy-check` |
| `docker-ram-checker` | `plugins/developer-workflow-skills/skills/docker-ram-checker`<br>`skills/docker-ram-checker` |
| `document-field-discovery` | `plugins/fde-estimation-skills/skills/document-field-discovery` |
| `dual-track-checklist-verifier` | `plugins/developer-workflow-skills/skills/dual-track-checklist-verifier` |
| `dual-track-pr-creator` | `plugins/developer-workflow-skills/skills/dual-track-pr-creator` |
| `dual-track-tdd` | `plugins/developer-workflow-skills/skills/dual-track-tdd` |
| `experiment-diagnosis` | `plugins/research-workflow-skills/skills/experiment-diagnosis` |
| `experiment-loop` | `plugins/research-workflow-skills/skills/experiment-loop` |
| `gcloud-direnv-setup` | `plugins/developer-workflow-skills/skills/gcloud-direnv-setup`<br>`skills/gcloud-direnv-setup` |
| `generate-estimate-package` | `plugins/fde-estimation-skills/skills/generate-estimate-package` |
| `generate-git-work-report` | `plugins/developer-workflow-skills/skills/generate-git-work-report` |
| `houm-refactoring` | `plugins/houmy-skills/skills/houm-refactoring`<br>`skills/houm-refactoring` |
| `houmlike-design` | `plugins/houmy-skills/skills/houmlike-design`<br>`skills/houmlike-design` |
| `make-llm-wiki-raw` | `plugins/llm-wiki-skills/skills/make-llm-wiki-raw`<br>`skills/make-llm-wiki-raw` |
| `model-quality-compare` | `plugins/research-workflow-skills/skills/model-quality-compare`<br>`skills/model-quality-compare` |
| `notion-dashboard-builder` | `plugins/notion-workspace-skills/skills/notion-dashboard-builder`<br>`skills/notion-dashboard-builder` |
| `pr-creator` | `plugins/developer-workflow-skills/skills/pr-creator` |
| `product-context` | `plugins/product-context-skills/skills/product-context`<br>`skills/product-context` |
| `prompt-optimizer` | `plugins/developer-workflow-skills/skills/prompt-optimizer`<br>`skills/prompt-optimizer` |
| `reconcile-scope-delta` | `plugins/fde-estimation-skills/skills/reconcile-scope-delta` |
| `refactoring-resistant-tests` | `plugins/developer-workflow-skills/skills/refactoring-resistant-tests` |
| `resume-formatter` | `plugins/resume-skills/skills/resume-formatter`<br>`skills/resume-formatter`<br>`resume-formatter` |
| `resume-project-summary` | `plugins/resume-skills/skills/resume-project-summary`<br>`skills/resume-project-summary` |
| `resume-translator` | `plugins/resume-skills/skills/resume-translator`<br>`skills/resume-translator` |
| `selecting-video-shorts` | `plugins/analysis-skills/skills/selecting-video-shorts`<br>`skills/selecting-video-shorts` |
| `setup-release-pipeline` | `plugins/developer-workflow-skills/skills/setup-release-pipeline` |
| `subagent-creator` | `plugins/developer-workflow-skills/skills/subagent-creator`<br>`skills/subagent-creator` |
| `system-prompt-creator` | `plugins/writing-skills/skills/system-prompt-creator`<br>`skills/system-prompt-creator` |
| `translate-book` | `plugins/translation-skills/skills/translate-book` |
| `update-houmy-notes` | `plugins/config-skills/skills/update-houmy-notes`<br>`skills/update-houmy-notes` |
| `update-notes` | `plugins/config-skills/skills/update-notes`<br>`skills/update-notes` |
| `wikify-raw` | `plugins/llm-wiki-skills/skills/wikify-raw`<br>`skills/wikify-raw` |

`houmlike-design/NOTICE.md` excludes the brand artwork, source brand book,
trademark rights, and separately licensed fonts from the maintainer's MIT grant.
Research skills retain their methodological acknowledgments; their `NOTICE.md`
limits the MIT grant to original instructions and examples, and records that the
referenced autoresearch README states MIT without a separate root license file.

## Upstream and adapted material

- `visual-explainer`: MIT, copyright Nico Bailon. Its bundled Pele code is MIT
  and the Lucide icon notice is ISC. Preserve `LICENSE`, `kit/vendor/PELE-LICENSE`,
  and the pinned revision in `UPSTREAM.md` in both distributed copies.
- Anthropic skills and local adaptations of them keep their existing notices.
  In particular, `docx`, `pdf`, `pptx`, and `xlsx` carry their own proprietary
  terms. Their licenses and instruction bodies are unchanged by this work.
- `database-migrations` and `web-security-checklist`: existing Affaan Mustafa
  MIT licenses and provenance notices are preserved unchanged.
- `humanize-korean`: existing epoko77-ai MIT license and notice are preserved.
- `layered-character-production`: existing maintainer MIT license and bundled
  generative-media-skills notice are preserved.
- `explain-simply`: the upstream attribution in `NOTICE.md` remains authoritative.
  Its upstream revision states MIT in its README but supplies no license file;
  this change does not manufacture an upstream notice or assign sole ownership
  to the maintainer.
- Third-party library and font notices in `THIRD_PARTY_NOTICES.md`, per-skill
  notices, and adjacent license files remain in effect.

For a new original skill, include a full MIT `LICENSE.txt` with the actual
copyright holder and year, add `license: MIT` to its frontmatter, and publish
the same notice in its plugin mirror. For an imported skill, preserve upstream
copyright, license text and source revision; record local adaptations separately.
