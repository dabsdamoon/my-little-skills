# Expanded low-effort comparison — 2026-11-18

The earlier 24-case text pilot measured answers and code comprehension. This run
adds actual implementation and reproducible data-analysis artifacts. It still does
not establish a general model ranking or comprehensive autonomous-research ability.

| Dimension | GPT-6.1 Sol | GPT-6.2 Sol | Evidence type |
|---|---:|---:|---|
| GPQA Diamond subset, 8 unique questions | 8/8 twice | 8/8 twice | Exact-answer, closed book |
| Ledger implementation | 13/13 | 13/13 | Frozen hidden behavioral acceptance tests |
| Code structure and invariant handling | 5/6 | 6/6 | One identity-blinded LLM rubric, subjective |
| Research execution/reproducibility | 7/7 | 7/7 | Original + reordered/gapped/scaled/constant data, saved output, report present |
| Research interpretation | 6/6 | 6/6 | One identity-blinded LLM rubric, subjective |

The functional/code-research tasks each have **one attempt per model**, not a
repeatability estimate. GPQA repeats share the same eight questions. No aggregate
score combines objective checks with subjective opinions.

## Tasks and success criteria

**Hard questions.** A deterministic, domain-balanced sample of eight GPQA Diamond
items: physics 3, chemistry 3, biology 2. Record IDs, option permutations and source
revision are recorded in [gpqa-selection.json](gpqa-selection.json) and
[PROTOCOL.md](PROTOCOL.md). Public-benchmark contamination is possible. This batched
subset is not an official full GPQA score. Question text and raw keys remain in the
local experiment output; the public evidence preserves selection IDs/hashes.

**Implementation.** An original small multi-file Python ledger, informed by the
issue-to-working-patch approach used in SWE-bench, not a SWE-bench instance. Models
implemented exact money, tenant-local sequence, idempotency with original receipts,
atomic rollback across tenants and iterator failures. The unchanged starter passes
3/13 hidden checks; both submitted implementations pass 13/13. Public tests alone
were insufficient. Real code, additional candidate tests and DESIGN.md are preserved
under [artifacts](artifacts). The reviewer judged responsibilities, invariants and
proportionate maintainability, rather than counting files or functions.

**Research.** A task adapted from DiscoveryBench's real World Bank education/income
dataset. Models had to inspect the data, implement a generic analysis CLI, produce
actual results and write a supported report. A separate pinned Docker execution
checked original data, row reversal, missing-year gaps, scaled values, constant
predictors, saved-result consistency and report presence. All passed, and original
CSV/metadata hashes remained unchanged. The original numerical key uses Python's
statistics.correlation/linear_regression independently of contestant code.

Both reports identify that the data use **GNI per capita** and education expenditure
as a percentage of GNI, despite GDP/budget wording in metadata/questions. They
distinguish association from causal impact and disclose the tiny SSF sample (five
level observations / four annual differences). Both reproduce:

| Group | Level n / r | Difference n / r |
|---|---|---|
| SSF | 5 / −0.966421 | 4 / −0.455752 |
| LMC | 41 / −0.480538 | 40 / +0.078761 |

This measures bounded observational-data analysis, not novel scientific discovery,
live literature retrieval, GPU experimentation or full paper replication.

## Blinded review and exploratory edge case

The fixed reviewer, `gpt-6.2-astra`, saw anonymous A/B artifacts, common tasks and
objective results. Mapping was withheld until its scores were saved. It is from
the same provider, so blinding does not establish an unbiased human judgment.
[judge-scores.json](judge-scores.json) contains criterion scores and code/report
references; [judge-mapping.json](judge-mapping.json) reveals identities afterward.

The one-point structure/invariant difference came from a **post-hoc exploratory**
case: a valid 5,001-digit amount under the task's uncapped decimal-string contract.
GPT-6.1 Sol's integer-string conversion hit Python's default 4,300-digit limit;
GPT-6.2 Sol's implementation returned the exact balance. We independently reproduced
this in the same pinned Python Docker environment. This was not one of the frozen
13 acceptance tests; their 13/13 scores remain unchanged. It is a narrow edge-case
observation, not evidence of a general architectural or production advantage.

## Controls, cost and observed time

Eight contestant CLI launches: four question runs, two implementation runs and
two research runs, plus one anonymous artifact-review agent. All contestants used
`low`, native Codex 0.170.0 and ChatGPT subscription login. No separately billed
provider API adapter/SDK was selected. These consume subscription quota; call count
does not bound CLI-internal turns or exact token usage.

| Task | GPT-6.1 Sol wall time | GPT-6.2 Sol wall time |
|---|---:|---:|
| GPQA subset, mean of two | 26.390 s | 14.821 s |
| Implementation, one attempt | 69.581 s | 68.558 s |
| Research, one attempt | 78.643 s | 87.569 s |

Observed wall time includes queue/network, native tools and local tests. Cache
usage differed. These times do not establish intrinsic speed or effort causality.
Requested model IDs are not independently attested immutable backend snapshots.

Starting sources/prompts, grading criteria and grader source hashes were frozen
before each track's submissions. Each contestant used an independent workspace;
native tools were allowed for artifacts, with network/apps/plugins/skills/other
agents disabled. Recorded commands showed no external model/network/grader access.
Native workspace-write sandboxing is not container isolation. Grading ran separately
inside a read-only, unprivileged, network-disabled Python container, image digest in
[grading-manifest.json](grading-manifest.json). Collected artifact hashes matched
before/after grading. No submitted code was repaired or rerun by another model.

The reusable collector subsequently received two tested freeze guards: reject added
starter files, and exclude ignored .git/cache directories when copying. Actual
frozen starters matched their planned file sets. The exact launch source is
preserved as [artifact-launcher-at-run.py](artifact-launcher-at-run.py); its helper
hash is recorded in the local plans and the unchanged text runner is in the skill.

## Reproduction and sources

See [evidence.json](evidence.json), [implementation-scores.json](implementation-scores.json),
[research-scores.json](research-scores.json), the public task starters and frozen
[graders](graders). Mount a selected artifact at `/workspace:ro` and these graders
at `/grader:ro` in the pinned Python image, then run `python -B
/grader/check_implementation.py` or `python -B /grader/check_research.py` with no
network, no credentials and an unprivileged user. The grader prints JSON checks.

- [GPQA source](https://github.com/idavidrein/gpqa/tree/56686c06f5e19865c153de0fdb11be3890014df7): dataset CC BY 4.0; code MIT. Both notices are retained in source-notices.
- [DiscoveryBench source](https://github.com/allenai/discoverybench/tree/c31fcf011e070f021a5f5b906896d0821f6880e8): ODC-By database notice is retained beside copied data and in source-notices.
- [SWE-bench methodology](https://www.swebench.com/original): reference for issue-resolution evaluation; its official benchmark was not run.

Own collector, fixtures and grader contributions remain MIT. Imported dataset
material keeps its own notices; there is no blanket MIT relicensing of these data.
