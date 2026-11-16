# Product Context 0.1.0 verification

Verified locally on 2026-11-16. This is an offline development tool; no product
runtime, deployment, provider credentials or recurring generation was changed.

## Automated contracts

The new package has **18 passing public CLI tests**, exercising actual temporary
files and persisted state. Initial 13 tests failed before the CLI existed.
Recursive exclusion, empty scope, malformed input, packet provenance and external
URL regressions were also observed failing before their implementation/fix.

Contracts include read-only check/prepare, provider executable traps, exact
snapshot recording, question preservation/resolution, accepted vs proposed
supersession, reconsideration, immutable IDs, clone portability, changed/deleted
evidence, source/state symlinks, writer locks, byte bounds, local Markdown links,
and opt-in review freshness.

Combined verification:

```sh
uv run --no-project --with pytest python -m pytest \
  skills/product-context/tests plugins/fde-estimation-skills/tests \
  plugins/developer-workflow-skills/skills/dual-track-checklist-verifier/tests -q
```

Result on the current `main` base (`3c05d001`): **75 passed, 10 subtests passed**.
The checklist suite uses pytest. Pytest was isolated through uv; it is not a
runtime dependency of this plugin. Canonical and plugin
distribution bundles were compared byte-for-byte. Python syntax and plugin JSON
were checked, marketplace names were unique, and `git diff --check` passed.

## Read-only product pilots

| Product | Selected evidence files | Local structural findings | Provider/model calls |
|---|---:|---|---:|
| HoumDesk | 26 (273,934 bytes) | No missing configured source or inline local link target | 0 |
| smart-RPA | 21 | None in selected scope | 0 |
| Houm School | 8 | One missing local link target in the capability document | 0 |

Product Git statuses were compared before/after each pilot and remained unchanged.
These are existing-checkout inspections, not deployment or semantic-consistency
proof. HoumDesk's database-ownership question is surfaced as a review topic; the
tool does not claim to resolve the PRD/TDD difference automatically.

## Fresh consumer and final review

Before authoring, a fresh consumer could not discover a supported product-context
tool in the existing marketplace. After authoring, an independent consumer used
the reference and CLI help with a different layout (`handbook/architecture` and a
service contract). Snapshot rejection, questions, decision replacement, deletion,
branch drift and update preparation were exercised in a disposable product.

One independent final review found a packet omission: staging-only decision scope,
relationships and evidence provenance were not included. The omission was
reproduced by a failing public CLI test and fixed. A malformed external URL also
stopped the entire offline scan; a failing regression test preceded the fix.
The full 18-test suite and the combined 75-test suite passed after these changes.
No second model review was run.

## Limits

- No semantic conflict resolver, automatic AI generation, hosted API adapter,
  background trigger, CI rollout or global plugin installation is shipped.
- Existing agent usage is consumed when the skill or packet is read by a model.
- Local-link checking covers inline Markdown links outside fenced code; URL and
  fragment validation are outside its contract.
- Filesystem checks cover ordinary traversal and symlink cases. This tool is not
  a sandbox against a hostile process racing filesystem mutations.
- Review attribution is recorded text, not authenticated approval. A current
  evidence snapshot does not certify a production release or resolve questions.
