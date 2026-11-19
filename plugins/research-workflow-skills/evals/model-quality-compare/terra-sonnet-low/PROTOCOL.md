# Terra 6.1 / Claude Sonnet 5.5, low, fresh sessions

Contestants: gpt-6.1-terra via native Codex ChatGPT login and claude-sonnet-5-5
via native Claude Code Claude.ai subscription. No API SDK/key fallback. Eight
contestant CLI launches total: GPQA eight frozen questions twice/model (ABBA),
implementation once/model, research once/model. No automatic retries or repairs.

Reuse exact prior GPQA question/option selection, common prompt/instruction bytes,
artifact starter files, grading specifications and frozen Docker graders. Verify
hash equality with the prior Sol experiment before execution. Each artifact track
uses a separate writable source copy; question runs start in empty temporary cwd.

Context controls: no resume/continue/history handoff. Codex exec ephemeral,
ignore-user-config/rules, project_doc_max_bytes=0, common replacement instructions,
skills/plugins/apps/hooks disabled, memories explicitly off (previous default off).
Claude fresh UUID, no-session-persistence, safe-mode/restricted, no setting sources,
strict empty MCP configuration, disabled slash commands/skills, common replacement
system text, exact available-model allowlist and no configured fallback. Never use
Claude --bare: local CLI documents API-only auth in that mode. Preserve native
credential locations; child OS env is allowlisted without API/auth/endpoint overrides.

Do not claim zero total context: core host/tool/managed policies can remain. Providers
use different native harnesses; low does not denote equal compute across providers.
Verify reported Claude model IDs, absent skills/plugins/MCP and native permission
denials. Preserve raw native and separately normalized events, cross-check hashes.
Unexpected model/context or infrastructure issues are N/A, not low-quality zeros.

Report objective GPQA/implementation/reproducibility results separately. Reuse the
subjective artifact rubric only with identity-blinded artifacts; disclose judge and
provider bias. The previously discovered 5,001-digit money case, if checked, remains
an exploratory diagnostic rather than a newly weighted acceptance criterion.

Historical Sol results are reference measurements, not simultaneous paired trials.
No vision/browser tasks are added for Terra; this tests the same text/code/data goals.
