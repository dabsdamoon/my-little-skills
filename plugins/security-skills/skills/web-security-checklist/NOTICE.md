# NOTICE — web-security-checklist

This skill is a derivative work of the `security-review` skill in
[everything-claude-code](https://github.com/affaan-m/everything-claude-code)
by Affaan Mustafa.

- Upstream: https://github.com/affaan-m/everything-claude-code
- Upstream path: `skills/security-review/SKILL.md`
- Vendored from commit `afa5651e9fcd082ebdc6e8e21189ab491bed7234` (2026-09-12)
- Upstream license: MIT. The upstream `LICENSE` text and copyright line are
  reproduced unchanged in `LICENSE.txt` next to this file.

## What was retained from upstream

- The topic list: secrets, input validation, SQL injection, authentication and
  authorization, Supabase RLS, XSS and CSP, CSRF, rate limiting, sensitive data
  in logs and errors, and dependency security.
- The paired "wrong / right" teaching style and a pre-deployment checklist.
- The note against literal dollar-digit placeholders, which Claude Code
  substitutes when a skill is invoked with arguments.

## What this fork changes, and why

Renamed from `security-review` to `web-security-checklist` so it is not
confused with Claude Code's built-in `/security-review` command. The
description was narrowed. Upstream triggered on any user input or API
endpoint, which matches almost every feature task. The fork triggers on
explicit security reviews and on changes to auth, sessions, payments,
secrets, and uploads.

Corrections (upstream text that was wrong, unsafe, or contradicted the
maintainer's rules):

- **Secrets:** upstream put all secrets in environment variables and hosting
  platforms. The fork uses Google Secret Manager on demand through each repo's
  `scripts/with-secrets.sh`, Secret Manager references with
  `--update-secrets` / `--set-secrets` on Cloud Run, and forbids printing or
  exporting secrets.
- **CSP:** upstream's "strict" `script-src 'self'; style-src 'self'` header in
  `next.config.js` breaks Next.js, which emits inline scripts. The fork uses the
  per-request nonce in `proxy.ts` from the Next.js CSP guide, and documents the
  dynamic-rendering cost.
- **File uploads:** upstream trusted the client-supplied MIME type and
  filename. The fork follows the OWASP File Upload Cheat Sheet.
- **CSRF and cookies:** upstream required `SameSite=Strict` on all cookies plus
  both tokens and double-submit. The fork follows OWASP (SameSite is defense in
  depth; token patterns are alternatives) and Next.js Server Actions' built-in
  Origin check.
- **Supabase:** upstream required httpOnly cookies, which Supabase says is
  unnecessary and which conflicts with its browser client. The fork adds
  server-side `getClaims()` (never `getSession()` on the server), `to
  authenticated` and `(select auth.uid())` in policies, and `with check` on
  updates.
- **SQL placeholders:** upstream's `?` example is wrong for node-postgres. The
  fork describes numbered placeholders in prose and adds psycopg examples.
- **Rate limiting:** upstream used in-memory `express-rate-limit` with the
  renamed `max` option. That does not work across Vercel or Cloud Run
  instances. The fork uses Vercel WAF, Cloud Armor, or a shared store.
- **Dependencies:** upstream ran `npm audit fix` and `npm update`. The fork
  keeps reviews report-only and sends any install through the maintainer's
  package-safety rule.
- **Zod:** updated to Zod 4 (`z.email()`, `error.issues`).

Removed: the Solana section (`@solana/web3.js` exports no `verify`), the
orphaned AWS-only `cloud-infrastructure-security.md`, and the Express-specific
examples.

Added: a diff-review procedure with greppable checks, a report format matching
the maintainer's PR skills (`CLEAR` / `NOTE` / `CONCERN`), Server Action
authorization guidance, and GitHub Actions pinning.

Every API, command, flag, and version in `SKILL.md` was checked against the
sources in its "Sources" section on 2026-10-26.
