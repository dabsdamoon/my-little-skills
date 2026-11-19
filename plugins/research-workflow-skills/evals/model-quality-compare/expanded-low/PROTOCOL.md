# Expanded low-effort pilot (frozen design before contestant calls)

Models: gpt-6.1-sol and gpt-6.2-sol, low effort, ChatGPT subscription only.
Budget: 8 contestant CLI launches total, no automatic retries, plus at most one
fixed identity-blinded artifact reviewer. Quota rather than separate API billing.

1. GPQA Diamond: 8 questions, physics 3 / chemistry 3 / biology 2, selected by
   stable SHA256 order of `gpt-sol-low-v2|Record ID`, option shuffle seed 6000+i.
   Two fresh trials/model, sequential ABBA, closed book/tools disabled. Official
   primary Question/Correct Answer fields; exact option-letter accuracy. Pin
   repository 56686c06f5e19865c153de0fdb11be3890014df7; preserve CC BY 4.0 data notice.
   Batched subset: not the official full benchmark, possible contamination.
2. Implementation: original small multi-file ledger repo. One attempt/model.
   Freeze contract and hidden behavior checks before launch. Native coding tools,
   independent starter copies, no network/skills/other models. Re-execute hidden
   acceptance checks in read-only, network-disabled, unprivileged Python Docker.
   Report functional checks separately from blinded structure rubric.
3. Research: adapt one DiscoveryBench real World Bank data-analysis task, pinned
   c31fcf011e070f021a5f5b906896d0821f6880e8, ODC-By attribution preserved. One
   attempt/model. Deliver runnable standard-library analysis and evidence-backed
   report. Score numerical correctness on original and perturbed data, reproducible
   execution, defensible inference, disclosure of metadata/data mismatch and limits.

Structure rubric (subjective, 0..2 each): cohesive responsibilities/interfaces;
centralized invariants and failure semantics; proportionate change and maintainability.
Research rubric (subjective, 0..2 each): answers the question from actual results;
method/inference justified; uncertainty/limitations and provenance explicit.
Fixed judge sees anonymous artifacts/specs and objective execution results only,
never model identities. Judge opinions are not general accuracy. No composite rank.

Limits: 8 questions and 2 agent tasks are diagnostic examples, not comprehensive
software architecture or autonomous-science benchmarks. Single artifact attempts
have no repeatability estimate. No GPU, paid training, web-research agent, long
paper replication or production-system benchmark. Native CLI host context remains.
