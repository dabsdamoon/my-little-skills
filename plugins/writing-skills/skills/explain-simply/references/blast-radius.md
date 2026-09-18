# Blast-radius patterns by domain

Load when classifying items from a work summary. The point is not to define these
terms — the reader can look up a definition. The point is to know **which ones
carry a consequence the summary probably did not mention**.

Each entry: the thing you'll see in a summary → the consequence to surface.

## Tier 1 — 되돌릴 수 없음 / 데이터 손실

**Data / DB**
- `ON DELETE CASCADE` added → deleting one parent row now silently deletes
  children. Ask what code paths delete the parent, and whether any admin tool or
  script does it in bulk.
- Index dropped (`DROP INDEX`, btree → BRIN/GIN swap) → any query that relied on
  the old index's access pattern gets slower, possibly by orders of magnitude. The
  new index usually serves *one* access pattern well. Ask what else queries that
  table.
- Column or table dropped, type narrowed (`text` → `varchar(n)`, `bigint` → `int`)
  → data that doesn't fit is gone on write, or the migration fails mid-way.
- Migration without a down path, or `TRUNCATE`/destructive backfill → there is no
  rollback. Ask whether a snapshot exists.
- Partition dropped or retention shortened → historical rows are gone, and reports
  over long windows silently change shape.

**Infra / storage**
- Bucket lifecycle rule, `force_destroy`, volume recreate in Terraform plan →
  state loss on apply.
- Secret rotated or removed → anything still holding the old value breaks at its
  next call, not at deploy.

**ML / DL**
- Checkpoint overwritten rather than versioned, or artifact path reused → the
  previous model is unrecoverable and the comparison baseline is gone.
- Training data filtered or deduplicated in place → the old dataset cannot be
  reconstructed, so no future run is comparable.

## Tier 2 — 외부에 보이는 동작 변경

- Response schema, field removed or renamed, status code changed, pagination
  changed → every existing client breaks, including the mobile app you cannot
  redeploy and the partner integration you forgot about.
- Auth, session lifetime, permission check, CORS, rate limit → either locks out
  real users or opens something up. Both are silent in tests that use an admin
  fixture.
- Pricing, tax, discount, refund, invoice rounding → produces wrong money.
  Retroactive effects are the dangerous part.
- Email, push, webhook triggers → a loop or a backfill can fan out thousands of
  real messages to real people.
- Public URL, redirect, canonical tag, robots directive → SEO and inbound links.

## Tier 3 — 안전장치 해제

**Backend**
- Strict/eager-loading guard disabled (Rails `strict_loading`, Django
  `select_related` assertions, N+1 detectors) → the query count is now free to
  grow with no alarm. Scoping it to one endpoint is legitimate; the risk is that
  the endpoint later gets reused.
- Isolation level lowered, lock removed, `SKIP LOCKED` introduced → changes *which*
  rows a worker sees and in what order. `SKIP LOCKED` itself is a standard,
  usually-safe queue pattern, but it abandons FIFO ordering. Surface that only if
  ordering matters to the domain.
- FK, unique, or `NOT NULL` constraint dropped → duplicates and orphans become
  possible, and they accumulate silently until a report is wrong.
- Retry, timeout, circuit breaker, idempotency key removed → one slow dependency
  becomes an outage, or one retry becomes a double charge.
- Validation moved from server to client → it is now advisory.

**Data pipeline**
- `depends_on_past` / `wait_for_downstream` off → runs no longer serialize. Great
  for backfills, wrong for any model whose today depends on its yesterday
  (running totals, state machines, SCD2, session stitching).
- dbt `full-refresh` → `incremental` with `merge` → late-arriving or corrected
  source rows may never be picked up, depending on the `is_incremental` filter.
  Ask what the filter's watermark is.
- `on_schema_change: append_new_columns` → a *renamed* or *retyped* column is not
  handled; only additions are.
- Freshness/volume test removed or thresholds relaxed → the pipeline stops telling
  you when it silently produced nothing.

**CI / tests**
- Test skipped, `continue-on-error`, coverage gate lowered, lint rule disabled →
  the gate that would have caught the next mistake is off.

## Tier 4 — 측정 방법 변경 (숫자 비교가 끊긴다)

This tier exists because of a specific, recurring reading error: the reader sees a
metric move and assumes performance moved. Say explicitly when the *ruler*
changed.

**ML / DL**
- Random split → temporal holdout (or grouped/stratified split) → the metric
  usually gets *worse*, and that is usually *correct*: the old split leaked future
  or same-entity information. The old number was optimistic, not the new one
  pessimistic. Never report this as a regression.
- Eval set regenerated, decontaminated, or reweighted → same effect.
- Metric definition changed (macro vs micro average, top-k, tokenizer change
  affecting perplexity, different loss reduction) → not comparable to any logged
  history.
- Prompt or judge model changed in an LLM eval → the scale itself moved.

**Product / analytics**
- Attribution window, session timeout, bot filter, deduplication key, active-user
  definition → every dashboard's history changes meaning at the cutover date.
- Sampling rate or aggregation grain changed → percentiles especially. p99 over a
  sampled stream is not p99.

## Tier 5 — 성능·내부 리팩터 (part 3에 둔다)

These are worth explaining but rarely need a decision.

- Cache added, `staleTime`/TTL raised, `refetchOnWindowFocus` off → fewer
  requests, and up to that window of stale data on screen. Only escalate if the
  screen is one where staleness is harmful (live ops, payments, inventory).
- Server components / SSR boundary moved, `Suspense` streaming → perceived load
  time. Escalate only if it changes what is rendered for logged-out users or
  crawlers.
- Bundle size, code splitting, image optimization → does not change behavior.
- Index *added*, query rewritten, connection pool tuned → same results, less time.
- bf16/fp16 mixed precision, gradient checkpointing, grad accumulation, batch
  size traded against accumulation steps → same effective math, different memory
  and speed. Note when effective batch was *preserved* versus actually changed,
  since a changed effective batch does move results.
- LR schedule swap (cosine → WSD and similar) → affects results but is a research
  choice, not a risk. Explain what the shape is; do not escalate.

## The one pattern worth memorizing

A summary reports **what was done**. The consequence lives in **what was removed**
to do it. Scan any summary for removals first: dropped, disabled, off, relaxed,
skipped, unset, `--no-`, `false`. That is where tiers 1 through 3 hide.
