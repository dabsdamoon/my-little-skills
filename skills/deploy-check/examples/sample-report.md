# Example: Deploy Safety Report

This is a sample output from the deploy-check skill.

---

## Deploy Safety Report

**Risk Level:** CAUTION
**Branch:** `dev` → `main`
**Date:** 2026-04-03
**Files Changed:** 11 (2 new, 8 modified, 1 deleted)
**Commits:** 5

---

### Findings

| # | Category | Finding | Severity | File | Action Required |
|---|----------|---------|----------|------|-----------------|
| 1 | DB Schema | New column `matching_label` added to `user_profiles` — nullable, no migration file | CAUTION | `app/lib/db/schema.ts` | Verify `db:push` was run on production DB |
| 2 | API Contract | Loader return in `schedule.tsx` changed `formatMeetingDate` function — same output but different implementation | SAFE | `app/routes/schedule.tsx` | Verified: getUTC* produces identical result on UTC server |
| 3 | Env/Config | No new environment variables | SAFE | — | — |
| 4 | Data Integrity | Cron schedule unchanged, notification templates unchanged | SAFE | — | — |
| 5 | Auth/Security | No auth changes, no secrets in diff | SAFE | — | — |
| 6 | External | `formatKST` re-exported from new shared module — all existing callers use same import path | SAFE | `app/lib/admin/format-date.ts` | — |

---

### Changed File Classification

| File | Category | Risk |
|------|----------|------|
| `app/lib/format-kst-wallclock.ts` | New utility | SAFE |
| `app/components/home/formatMeetingDate.ts` | Behavior change | SAFE (verified) |
| `app/lib/admin/format-date.ts` | Re-export refactor | SAFE |
| `app/routes/schedule.tsx` | Display logic | SAFE |
| `app/components/admin/user-detail/DebriefSection.tsx` | Bug fix (admin) | SAFE |
| `app/routes/admin/meetings/$id.tsx` | New page | SAFE |
| `app/routes/admin/meetings/index.tsx` | Row click | SAFE |
| `app/routes.ts` | Route registration | SAFE |
| `tests/**` (3 files) | Tests only | SAFE |

---

### Pre-Deploy Checklist

- [x] All CI tests passing (1569 unit + 12 integration)
- [x] Typecheck passing
- [x] No secrets in diff
- [ ] Verify `matching_label` column exists in production DB
- [ ] Inform admin team: meeting times on home page now display correctly (was +9h off)

---

### Rollback Plan

**Reversibility:** Fully reversible

> Revert the merge commit. No data migrations or one-way operations. The timezone fix changes display only — no data is modified. The new admin meeting detail page can be removed by reverting without side effects.

---

### Impact Summary

**User-facing changes:**
- Meeting time on home page now displays correctly (was showing +9 hours ahead)

**Admin-facing changes:**
- New meeting detail page with timeline view
- Debrief "만남일" now shows correct time (was +9h)

**Background/cron changes:**
- None
