# Implementation, structure and research outcomes

Text-answer accuracy and code comprehension do not measure whether a model can
change software or complete a research workflow. For a broad comparison, keep an
explicit coverage matrix and select tasks with observable deliverables. Report
each track separately; a small subset is diagnostic, not a universal ranking.

## Task and metric selection

| Dimension | Task evidence | Scoring |
|---|---|---|
| Hard reasoning | Pinned public questions, fixed split/rows, shuffled choices and private keys | Exact accuracy; subset size, contamination and batching disclosed |
| Implementation | Identical starter repo, issue/contract, working code and test commands | Hidden behavioral acceptance tests; regression and failure details |
| Structure | Actual changes, public boundaries and design rationale | Identity-blinded rubric with cited code evidence; subjective and separate from tests |
| Research goal | Frozen data/question, runnable analysis, numerical outputs and report | Re-execution and perturbation checks; supported conclusions and method/limits rubric |
| Efficiency/reliability | Complete trajectories, usage, times, repeated independent attempts | Coverage, errors and spread; no generic scalar across unrelated tracks |

Primary examples: [GPQA](https://github.com/idavidrein/gpqa),
[SWE-bench](https://www.swebench.com/original), and
[DiscoveryBench](https://github.com/allenai/discoverybench). Pin revisions and
preserve each dataset's own license. GPQA data is CC BY 4.0, distinct from its MIT
code. DiscoveryBench's database uses ODC-By. Research tasks such as
[RE-Bench](https://github.com/METR/RE-Bench) can require substantial hardware/time;
reading them does not mean this skill executed them or validated frontier R&D.

## Freeze before launch

Choose the objective, starter, immutable input data, executable acceptance checks,
review rubric, tool permissions, effort and call budget. Validate that the starter
fails checks it should fail. Validate trusted numerical keys independently. Freeze
grader source hashes separately or inside the grading specification; never edit
checks after seeing contestant outputs to prefer a model. Public-example tests
are not a substitute for held-out behavioral checks.

The reusable artifact collector uses Python 3.10+ and native Codex ChatGPT login:

```bash
python3 <skill-dir>/scripts/artifact_benchmark.py plan \
  --out output/implementation-low --starter /path/to/public-starter \
  --prompt /path/to/task.txt --grading-spec /path/to/grading.json \
  --models gpt-6.1-sol gpt-6.2-sol --effort low --trials 1
python3 <skill-dir>/scripts/artifact_benchmark.py run \
  --out output/implementation-low --max-calls 2
```

Each model gets its own writable copy. The collector preserves file hashes, diffs,
commands, events and usage. It permits shell/file tools in Codex's workspace-write
sandbox, disables network/apps/plugins/skills/other agents, checks ChatGPT login,
and uses the same OS-variable allowlist as the text runner. The final chat message
is not the deliverable. Transport failures are unavailable; unexpected external
tools invalidate that attempt. Resume never launches a recorded attempt again.

Native workspace-write isolation is not a container. Do not claim inaccessible
host files merely because instructions prohibit reading them. Inspect trajectories
for outside access. Keep grading material out of contestant starting context and
outside the workspace. Execute generated artifacts in a real isolated environment
with no credentials/network and read-only inputs. For Docker, pin the image digest,
run unprivileged, drop capabilities, bound memory/processes, and mount only the
artifact and trusted grader. Do not mount a Docker socket or home directory.

## Grade and interpret

Re-run frozen objective checks on the exact collected artifacts; verify hashes
before and after grading. Missing/corrupt artifacts or broken evaluation plumbing
are N/A, not model-quality zeros. A valid attempted implementation that fails its
acceptance tests is a functional failure. Record individual failed contracts.

For structure, judge cohesion, interfaces, centralized invariants, error semantics
and proportionality using an explicit rubric. File/function/line counts alone do
not establish maintainability. Blind identities and withhold mapping/trajectories
that reveal model IDs. Cite concrete code and label the result as judge opinion.

For research, require actual execution, output consistency, correct numerical
analysis and evidence-backed inference. Re-run on controlled data perturbations
to detect hardcoded answers and missing-data errors. Check correlation/causation,
source/variable mismatch, uncertainty and reproducibility. A fluent report is not
proof of achieving the goal. A small data-analysis task is not a full autonomous
science or paper-replication benchmark.

Show functional checks, structure opinions, numerical reproducibility and research
opinions separately, with attempted/completed counts. One attempt per artifact has
no variance estimate. Never extrapolate production maintainability or universal
research ability from one small repository and one dataset.
