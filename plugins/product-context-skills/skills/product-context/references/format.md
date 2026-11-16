# Configuration and records

All JSON uses `schema_version: 1`. Unknown configuration fields fail so a setting
such as a provider or command cannot silently enable execution.

```json
{
  "schema_version": 1,
  "product": "example",
  "sources": ["README.md", "docs/**/*.md", "db/migrate.mjs"],
  "exclude": ["docs/archive/**"],
  "topics": [{
    "id": "database-ownership",
    "question": "Do current decisions and implementation describe the same ownership boundary?",
    "sources": ["docs/PRD.md", "db/migrate.mjs"]
  }]
}
```

Sources/exclusions use product-relative forward-slash globs. Explicit missing
sources are structural findings; an entirely empty scope is rejected. Credential,
VCS, dependency and harness-state paths are excluded. Symlinks cannot lead
outside the product. Defaults bound scanning to 1000 files, 8 MiB total, 1 MiB per
file; `max_file_bytes` can explicitly select a per-file limit up to 10 MiB (the
8 MiB total remains). No partial successful review is produced after a limit.

Markdown checks cover inline local links outside fenced code blocks. Fragments
and network URLs are not fetched or validated. Outside-product filesystem links
are listed as unverified references. This is not a complete Markdown linter.

## Decisions

Write the input as a temporary JSON file, then call the `decision` command:

```json
{
  "id": "D-002",
  "title": "Delegate product schema changes",
  "status": "accepted",
  "reason": "The staging handoff verified independent migration and rollback boundaries.",
  "actor": "human:product-owner",
  "scope": "staging; production handoff remains open",
  "supersedes": ["D-001"],
  "evidence": ["docs/adr/schema-delegation.md", "db/migrate.mjs"]
}
```

Actor labels are recorded attribution, not authenticated identity or proof of
approval. Set them to the actual source; do not invent human approval.
Evidence paths must be selected current source files. The harness captures their
hashes. Decision IDs cannot be reused. Relationships point to earlier IDs, so
new records cannot create cycles. Original records remain unchanged.

Statuses: `proposed`, `accepted`, `reconsideration`. Only an `accepted` record
activates its `supersedes` relationships. A `reconsideration` identifies
`reconsiders: ["D-001"]`; the older choice appears `under-review`. An accepted
replacement can supersede both an earlier accepted decision and its proposal.
Effective status is derived while the recorded status and rationale are retained.
Changed historical evidence is surfaced, not automatically interpreted as a
revoked or invalid decision.

## Review snapshots

Run `check --json` or `prepare` and inspect its relevant sources. Then `record`
the exact snapshot with a note and actual actor. The fingerprint covers normalized
configuration, source hashes and decision records, excluding checkout location,
Git HEAD and the review record itself. Source changes in another branch therefore
make the review stale; a clean clone containing identical versioned state remains
current. State is isolated per product checkout.

Open questions survive new review records. Add one with `--question "..."` and
resolve an existing one with `--resolve-question "..."`. A current snapshot can
still have unresolved questions or structural findings; these remain visible.
`record` means evidence review was recorded, not that all findings were fixed.

State writes are atomic and guarded by `.product-context/.lock`. A concurrent
writer fails with `LOCKED`. Inspect a leftover lock after a crashed process;
the tool does not delete somebody else's lock. Corrupt or wrong-product state
fails closed instead of being silently reset.

## OpenWiki

OpenWiki is optional. `prepare` creates a packet for selective source reading and
does not call OpenWiki or configure credentials. Explicitly requested generation
can use the separate [subscription-host MCP](subscription-wiki.md). It retains a
guarded completion receipt in `.product-context/wiki-review.json`, containing the
primary context snapshot and a digest of wiki Markdown, Claims and metadata.
Changed source or generated wiki bytes invalidate that receipt. The MCP's guarded
record tool requires a current receipt and explicit open-question input.

Decision history, unanswered questions, intended versus implemented behavior, and
environment-specific verification remain review concerns. This offline CLI
contains no provider execution, scheduling, global installation or deployment.
