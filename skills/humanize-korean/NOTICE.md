# Upstream provenance

- Source: https://github.com/epoko77-ai/im-not-ai
- Commit: b37e0206d31fffd9149bf57168d4d62eb2086bee (2026-10-12)
- Upstream package version: 2.3.2. Rulebook annotations have their own versions.
- Checked: 2026-10-21
- License: MIT; see LICENSE.txt.

The entry point adapts the upstream Codex skill for the existing shared Codex/Claude
Code package. It adapts runtime wording and the status banner, and adds local execution
guards: preserve a raw original and previous chunk outputs before reruns, and
accept only self-generated manifests whose resolved paths stay inside RUN_DIR. The references
are copied from skills/humanize-korean/references with trailing whitespace removed
from one rulebook line. The nine runtime scripts are
materialized from the upstream install.sh RUNTIME_SCRIPTS list, rather than copying
repository-relative Codex launchers. The skill therefore runs after standalone
copy installation and does not depend on the upstream checkout.

The root skills/humanize-korean directory mirrors the plugin skill. Both copies
must be updated together. No global installer or shell hooks are run.
