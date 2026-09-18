---
name: explain-simply
description: >-
  Use when the user has just been handed a completed work summary, changelog, PR
  description, review, incident write-up, or research result and cannot act on it
  because it is dense with domain jargon — "쉽게 설명해줘", "이거 무슨 뜻이야",
  "방금 뭐 한 거야", "풀어서 설명해줘", "explain this simply", "break this down",
  "what does this actually mean", "ELI5 this summary". Also use when the user is
  reading someone else's technical artifact across a stack they do not live in
  every day (data, frontend, backend, infra, ML/DL research) and needs to know
  which parts require a decision from them. Not for teaching a standalone concept
  from scratch, and not for rewriting the user's own prose.
---

# Explain Simply

Decode a finished piece of technical work for the person who owns its
consequences.

The reader is competent. They are not stupid, and they are not a child. They are
usually a generalist — one person covering data, frontend, backend, and research —
who is not simultaneously deep in all of them. What blocks them is not
intelligence. It is that the summary was written by someone who already knew the
answer, so it reports *what was done* and never *what it means for the person who
has to live with it*.

Your job is that second thing.

## The balance (retained from upstream)

Every explanation fails in one of two directions:

- **Too technical** — correct but opaque. Jargon stacked on jargon. The reader
  nods and retains nothing.
- **Too simple** — accessible but hollow or wrong. So sanded-down that the
  mechanism is gone, or quietly false. The reader feels they understood and
  didn't.

The target is the middle: **keep the load-bearing technical truth, wrap it in
plain words.** Sand off the incidental complexity, never the part that matters.
If a simplification makes the idea *wrong*, back off.

## Output contract

Produce these four parts, in this order. Every part is required. A part with
nothing in it says so in one line — it is never silently dropped.

### 1. 한 줄

The single thing to remember if they forget everything else — the actual upshot,
in the reader's terms.

Not a list of the areas touched. **Not a count of your own sections** ("판단해야
할 항목이 6개 있고…"): a tally is not an upshot, and it invites an off-by-one
against your own list. Name the thing that bites and the thing that was
misleading, and let the sections below do the counting.

### 2. 먼저 판단해야 할 것

The items that need a human decision, **ordered by blast radius** (ladder below),
worst first. Nothing else goes in this section. For each:

- **무엇이 바뀌었는지** — one line, plain words
- **왜 사람이 봐야 하는지** — the specific way this bites, not "주의가 필요해요"
- **무엇을 확인하면 되는지** — a concrete check the reader can actually run or look at

If genuinely nothing needs a decision, write `없음` and one line saying why. Do
not pad this section, and do not promote a performance tweak into it to make it
look non-empty.

### 3. 나머지 변경

Everything else from the source, one bullet each. Per item: what changed → what
it means in plain words → the cost it paid, if it paid one. Grouping by the
source's own section headers is allowed but not required; group by what the
reader cares about when that reads better.

**Every item in the source appears somewhere in part 2 or part 3.** Shortening
the output by deleting items is not shortening, it is hiding.

### 4. 확인 범위

One or two lines, always present:

- What you actually opened — files, diff, logs, test output — and what you found
- What is the source's own claim that you did not verify

## Blast-radius ladder

Rank by what happens when the change is wrong, not by how complicated it sounds.

| Tier | Class | Examples across the stack |
|---|---|---|
| 1 | **되돌릴 수 없음 / 데이터 손실** | `ON DELETE CASCADE`, 인덱스·컬럼·테이블 drop, 되돌릴 수 없는 마이그레이션, `TRUNCATE`, 파괴적 백필, S3/버킷 삭제 |
| 2 | **외부에 보이는 동작 변경** | API 응답 스키마·상태코드, 인증·권한, 과금·정산 로직, 공개 엔드포인트, 이메일·알림 발송 |
| 3 | **안전장치 해제** | 가드·검증 플래그 off, 락·제약·FK 제거, 격리 수준 완화, 재시도·타임아웃 제거, 테스트 skip, `depends_on_past` off, strict loading off |
| 4 | **측정 방법 변경** | eval split 교체, 지표 정의 변경, 샘플링·집계 방식 변경 — 이전 숫자와 비교가 끊긴다 |
| 5 | **성능·내부 리팩터** | 캐시, 번들, 인덱스 추가, 렌더링 경계 이동, 정밀도·배치 구성 |

**Tier 1–4 go in part 2. Tier 5 goes in part 3.** No exceptions to negotiate: a
change does not leave part 2 because the summary says it was scoped narrowly,
because it was deliberate, or because tests passed. Those are claims about
intent, and part 2 is about consequence.

Within part 2, order by tier, worst first. A narrowly-scoped tier-3 item sits at
the bottom of part 2 and its "왜 사람이 봐야 하는지" says the scope is narrow and
names what would widen it later — that is how a small risk gets reported small,
not by moving it out of sight.

Tier 4 is in part 2 whenever before/after numbers appear anywhere in the source,
because the reader will otherwise compare two numbers that are no longer
comparable.

**A tier-4 change makes the numbers around it incomparable.** Say that out loud.
"지표가 나빠졌다"와 "측정을 고쳤더니 이전 숫자가 거품이었다"는 정반대의 뜻이고,
독자가 혼자서는 구별할 수 없다.

## Verify before you explain

Explaining a claim makes the reader believe it harder. So when you have access to
the work, check the tier 1–3 items against it before you describe them.

- Read the diff for those items specifically — `git diff`, the migration file, the
  changed config. Not the whole repo. The candidates are named by the ladder.
- If what you find differs from the summary, the summary is wrong and you say so
  in part 2. That is the single most valuable thing this skill produces.
- If you have no access, part 4 says so plainly and every claim stays attributed
  to the source.

## Hard rules

These are the failures observed in testing. They are not style preferences.

**"테스트 통과", "CI 그린"은 안전의 증거가 아니다.** Do not convert it into a
verdict. Never write "안전하다", "병합해도 된다", "문제 없다", "기능적으로는
안전하게 들어갔다". A test suite asserts the behavior someone thought to assert;
cascade deletes, dropped indexes, and removed guards are exactly what it does not
cover. Report the green CI as a fact in part 4 and let part 2 stand.

**Do not invent causality.** Two changes sitting next to each other in a summary
are not cause and effect. If the source does not say A caused B, you do not say
it. A caching change does not shrink a bundle. Do not write "그 결과", "그 영향
으로", "그래서" across two items unless the source drew that arrow itself.

**Do not merge or drop items to get a cleaner narrative.** The urge to make it
read smoothly is the urge that deletes the destructive change. Rough and complete
beats smooth and short.

**Do not close by offering reassurance.** Close on part 4, or on nothing. No
"문제 없어 보여요", no "안전하게 들어간 변경들이에요".

## Craft (retained from upstream)

**Pay for your jargon.** Technical terms are not the enemy; leading with them is.
Give the plain idea first, then attach the real word: *"…이미 다른 워커가 잡은
행은 기다리지 않고 건너뜁니다 — 이게 `SKIP LOCKED`입니다."* Now the reader owns
both the intuition and the term, so they can search it, read the docs, and talk to
whoever wrote it. Dropping the term entirely leaves them stranded; leading with it
loses them.

**An analogy is a loan — map it, then pay it back.** Pick something the reader
understands viscerally (번호표 창구, 책 뒤의 색인, 장부). Map the parts
explicitly. Name where it breaks if the break could mislead. If no honest analogy
maps cleanly, don't force one — a concrete instance beats a strained metaphor.

**One analogy per item, not one per answer.** Upstream's "one running example,
reuse it throughout" is right when explaining a single concept and wrong here: a
work summary is many unrelated changes, and forcing one metaphor across all of
them is what produces invented connections. Keep each item's analogy local to that
item.

**Scale to the difficulty.** A three-line summary gets a three-line answer. Do not
run the full contract over something trivial — but parts 2 and 4 survive even in
the short form.

## Language

Answer in the language the user asked in. For Korean output, prefer the
`humanize-korean` skill afterward when the result will be read by someone else or
kept — this skill's output is functional prose and tends to read translated.

Keep identifiers, flags, file paths, metric names, and numbers verbatim. Never
localize a symbol the reader will have to grep for.

## Red flags — stop and re-read the contract

- About to write "안전" or "문제 없" anywhere
- Part 2 is empty and you did not check the ladder
- An item from the source is not in your output
- You wrote "그 결과" between two unrelated bullets
- You are explaining a tier-1 change without having opened the diff, while having
  the access to open it
- Your closing line reassures

## Provenance

Derived from [yash2002vardhan/explain-simply](https://github.com/yash2002vardhan/explain-simply).
See `NOTICE.md` for what was retained, what changed, and why. The blast-radius
ladder, the output contract, the verification step, and the hard rules are
additions from baseline testing; the two-sided failure frame and the jargon and
analogy craft are upstream's.

Domain-specific patterns for each ladder tier: `references/blast-radius.md`.
