---
name: web-security-checklist
description: "Security review checklist for Next.js, Supabase, Python, and Go apps: secrets, SQL injection, RLS and server-side auth, CSP nonces, CSRF, cookies, uploads, rate limits. Use when asked for a security review or audit of a branch, or when changing auth, sessions, payments, secrets, or file uploads."
---

# Web Security Checklist

Two uses:

- **Review a diff or branch.** Run the procedure below and report findings with file and line.
- **Write security-sensitive code** (auth, sessions, payments, secrets, uploads). Follow the rules by topic.

Target stack: Next.js App Router on Vercel, Supabase/Postgres, and Python or Go services on Cloud Run. This checklist does not replace a scanner or a penetration test. During a review, do not change code unless the user asks.

## Diff review procedure

### 1. Scope the change

```bash
git diff --name-only origin/main...HEAD
git diff --name-only --diff-filter=A origin/main...HEAD
```

`A...B` diffs from the merge base, so only this branch's changes appear. Fetch first so `origin/main` is current.

### 2. Run the greppable checks

Each check prints only lines the branch adds. A hit is a lead, not a finding: open the file and read the context before you classify it.

```bash
# Works in bash and zsh: d passes extra arguments (e.g. "-- path") through.
d() { git diff origin/main...HEAD "$@"; }

# Hardcoded secrets and committed env files
d | grep -nE '^\+.*(-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{20,}|sk_live_[A-Za-z0-9]{10,})'
d | grep -niE "^\+.*(api[_-]?key|secret|token|passw(or)?d)[[:space:]]*[:=][[:space:]]*['\"][^'\"]{8,}"
git diff --name-only --diff-filter=A origin/main...HEAD | grep -E '(^|/)\.env($|\.)' | grep -v '\.example$'

# Secrets reaching the browser, logs, or the shell
d | grep -nE '^\+.*NEXT_PUBLIC_[A-Z0-9_]*(SECRET|SERVICE_ROLE|PRIVATE)'
d | grep -niE '^\+.*(console\.(log|info|warn|error)|print\(|log\.Print|fmt\.Print).*(secret|token|password|api_?key|authorization)'
d | grep -nE '^\+.*(echo|printf).*\$\{?[A-Z_]*(KEY|SECRET|TOKEN|PASSWORD)'
d | grep -nE '^\+[[:space:]]*export [A-Z_]*(KEY|SECRET|TOKEN|PASSWORD)='
d | grep -nE '^\+.*gcloud secrets versions access'

# SQL built from strings
d | grep -nE '^\+.*\.(query|execute|raw|unsafe)\([[:space:]]*`[^`]*\$\{'
d | grep -nE "^\+.*\.execute\([[:space:]]*(f['\"]|['\"][^'\"]*['\"][[:space:]]*(%|\.format|\+))"
d | grep -nE '^\+.*(Query|QueryRow|Exec)(Context)?\(.*fmt\.Sprintf'

# Server entry points that need auth and ownership checks
git diff --name-only --diff-filter=AM origin/main...HEAD | grep -E '(^|/)(route|proxy|middleware)\.(ts|js)$'
git diff --name-only --diff-filter=AM origin/main...HEAD | xargs grep -lE "^['\"]use server['\"]" 2>/dev/null
d | grep -nE '^\+.*auth\.getSession\('

# Supabase privileged key outside server code, and new tables without RLS
d -- '*.tsx' '*.jsx' | grep -niE '^\+.*(service_role|secret_key|SERVICE_ROLE_KEY)'
d -- supabase/migrations | grep -niE '^\+.*create table'
d -- supabase/migrations | grep -niE '^\+.*(enable row level security|create policy)'

# XSS and code-execution sinks
d | grep -nE '^\+.*(dangerouslySetInnerHTML|\.innerHTML[[:space:]]*=|document\.write\(|eval\(|new Function\(|child_process.*exec\(|os\.system\(|pickle\.loads?\()'

# Cookies, CORS, uploads
d | grep -nE '^\+.*(Set-Cookie|cookies\(\)|set_cookie\(|http\.Cookie\{)'
d | grep -niE '^\+.*(Access-Control-Allow-Origin|allow_origins|AllowedOrigins).*\*'
d | grep -niE '^\+.*(formData\(\)|multipart|UploadFile|FormFile)'

# Dependencies and CI
git diff --name-only origin/main...HEAD | grep -E '(package\.json|package-lock\.json|pnpm-lock\.yaml|yarn\.lock|requirements[^/]*\.txt|pyproject\.toml|uv\.lock|go\.mod|go\.sum)$'
d -- .github/workflows | grep -nE '^\+.*uses: [^@]+@[^[:space:]]+' | grep -vE '@[0-9a-f]{40}'
d -- .github/workflows | grep -nE '^\+.*permissions:'
```

### 3. Check each hit against the rules below

For every new route handler, Server Action, or proxy, answer three questions. Who is the caller? Is it verified server-side? Do they own the resource? Every new table in an exposed Supabase schema needs `enable row level security` and at least one policy in the same migration. Every changed dependency goes through the package-safety review in section 10.

### 4. Report

Use the same ratings as the PR skills: `CLEAR` (nothing found), `NOTE` (worth a look, not exploitable as written), `CONCERN` (exploitable or a policy violation). One row per finding:

| Rating | Rule | Location | Why it matters | Fix |
|---|---|---|---|---|
| CONCERN | Server-side auth | `app/api/orders/[id]/route.ts:14` | Uses `getSession()`; the cookie can be forged | Use `getClaims()` and check `order.user_id` |

If nothing is found, say `CLEAR` and list the checks you ran.

## Rules by topic

### 1. Secrets (Google Secret Manager)

- No secrets in code, fixtures, PR bodies, or logs. Do not commit `.env*` files other than an `.env.example` with placeholders.
- Locally and in agent sessions, the repo's `scripts/with-secrets.sh` fetches secrets from Google Secret Manager on demand. It exports them only into the child process it runs:

  ```bash
  scripts/with-secrets.sh npm run dev
  scripts/with-secrets.sh -- uv run pytest
  scripts/with-secrets.sh sh -c 'psql "$DATABASE_URL" -c "select 1"'
  ```

  Keep the variable reference inside single quotes so the child shell expands it after hydration.
- Never `export` a secret in a shell profile, never `echo` or print one, and never run `gcloud secrets versions access` directly in an agent session, because the value lands in the transcript.
- Cloud Run gets secrets as Secret Manager references, not copied values. The service identity needs `roles/secretmanager.secretAccessor`. Pin a version rather than `latest` for env-var secrets, because they are resolved when an instance starts:

  ```bash
  gcloud run deploy SERVICE --image IMAGE_URL \
    --update-secrets=DATABASE_URL=myapp--DATABASE_URL:3
  # replace every secret reference on an existing service
  gcloud run services update SERVICE \
    --set-secrets="DATABASE_URL=myapp--DATABASE_URL:3"
  ```

- Next.js sends any variable prefixed `NEXT_PUBLIC_` to the browser. Keep secret keys unprefixed, and read `process.env` only in server-only modules (`import 'server-only'`).

### 2. SQL injection

- Prefer the query builder (supabase-js, Prisma, Drizzle) to raw SQL.
- For raw SQL, values go in parameters, never in the query string:
  - **node-postgres:** numbered placeholders (a dollar sign followed by the position) in the text, with the values array as the second argument.
  - **psycopg (Python):** `cur.execute("SELECT * FROM users WHERE email = %s", (email,))`. Use `psycopg.sql.Identifier` for dynamic table or column names, never `%`, `+`, or f-strings.
  - **Go:** pass values as query arguments. Never build query text with `fmt.Sprintf`.
- Map dynamic sort columns or table names through an allowlist; never pass them through from the request.

<!-- Do not write a literal dollar-sign-digit placeholder in this file. Claude Code
     substitutes those when a skill is invoked with arguments, which would turn the
     node-postgres example into concatenated SQL. Describe the placeholder in prose. -->

### 3. Supabase auth and RLS

- In server code (proxy, route handlers, Server Actions), protect pages and data with `supabase.auth.getClaims()`. Use `getUser()` when you need a fresh user record. Never trust `supabase.auth.getSession()` on the server: it reads the cookie without revalidating it, and cookies can be forged.
- On Next.js 16 the session refresh lives in `proxy.ts`. On Next.js 15 and earlier it lives in `middleware.ts`, and a `proxy.ts` is never called.
- Enable RLS on every table in an exposed schema. Write policies with `to authenticated` and `(select auth.uid())`. An `UPDATE` policy needs `using`, `with check`, and a matching `SELECT` policy. Put RLS and grants in the same migration; the `database-migrations` skill covers the mechanics.
- The secret key (or legacy `service_role` key) bypasses RLS. It stays server-side and never goes into a `NEXT_PUBLIC_` variable or a Client Component.
- Do not force `HttpOnly` on Supabase auth cookies. Supabase says it is not necessary, and the browser client needs the refresh token. The compensating controls are the CSP below and server-side `getClaims()`.

### 4. Authorization

- Server Actions can be called by a direct POST. Check authentication and resource ownership inside each action, or in the server-only data access layer it calls. A page-level check does not cover them.
- Take the acting user's id from verified claims, never from the request body, params, or a hidden field.
- Return only the fields the client needs, not whole database records.

### 5. Input validation

Validate at the boundary with a schema. In Zod 4, use `z.email()` (the `z.string().email()` form is deprecated) and read failures from `error.issues`:

```ts
import { z } from 'zod'

const CreateUser = z.object({
  email: z.email(),
  name: z.string().min(1).max(100),
})

let body: unknown
try {
  body = await req.json()
} catch {
  return Response.json({ error: 'invalid_json' }, { status: 400 })
}
const result = CreateUser.safeParse(body)
if (!result.success) {
  return Response.json({ error: 'validation_error', issues: result.error.issues }, { status: 422 })
}
```

### 6. XSS and Content Security Policy

- React escapes text by default. Avoid `dangerouslySetInnerHTML`. If user HTML must render, sanitize it with DOMPurify and an allowlist (`ALLOWED_TAGS`, `ALLOWED_ATTR`). On the server DOMPurify needs a DOM: use jsdom, or the isomorphic-dompurify project that the DOMPurify README points to.
- A static `script-src 'self'` header in `next.config.js` breaks Next.js, because the framework emits inline scripts. Use the per-request nonce from the Next.js CSP guide, set in `proxy.ts` (`middleware.ts` on Next.js 15 and earlier):

```ts
// proxy.ts
import { NextRequest, NextResponse } from 'next/server'

export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')
  const isDev = process.env.NODE_ENV === 'development'
  const csp = `
    default-src 'self';
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ''};
    style-src 'self' 'nonce-${nonce}';
    img-src 'self' blob: data:;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    upgrade-insecure-requests;
  `.replace(/\s{2,}/g, ' ').trim()

  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-nonce', nonce)
  requestHeaders.set('Content-Security-Policy', csp)

  const response = NextResponse.next({ request: { headers: requestHeaders } })
  response.headers.set('Content-Security-Policy', csp)
  return response
}
```

- Nonces require dynamic rendering. Static generation, ISR, and Partial Prerendering stop working, and pages lose CDN caching. Add `connect-src` and third-party script hosts explicitly. If the app also refreshes Supabase sessions, do both in the same `proxy.ts`.
- If static rendering must stay, the options are Next.js's experimental SRI (`experimental.sri`), or a header CSP with `'unsafe-inline'`. Record the second as temporary security debt.

### 7. CSRF and cookies

- Server Actions accept only POST and compare `Origin` with `Host` (or `X-Forwarded-Host`). Behind a proxy, list trusted hosts in `serverActions.allowedOrigins` rather than turning the check off.
- A route handler (`route.ts`) that changes state using cookie auth needs its own defense. Verify `Origin` / `Sec-Fetch-Site` against the exact expected origin, and reject requests where both are missing or `Origin: null`. Add a synchronizer token, or a signed double-submit cookie. These are alternatives: pick one. OWASP discourages the naive unsigned double-submit.
- Never change state on GET.
- App-owned session cookies (not Supabase's):

  ```text
  Set-Cookie: __Host-session=<opaque id>; Secure; HttpOnly; Path=/; SameSite=Lax
  ```

  `SameSite` is defense in depth, not a CSRF fix. `Strict` also drops the cookie on inbound links from other sites, so use it only where that is acceptable.

### 8. File uploads (OWASP)

- Allowlist extensions after input validation, and validate the file type from its content. The `Content-Type` header and `file.type` / `file.name` from form data are client-supplied.
- Generate the stored filename server-side. Limit filename length and characters, and limit the size.
- Only authorized users may upload. Store files outside the web root, or on separate storage served through an id-to-file handler.
- Scan with antivirus or a sandbox, and run CDR on document types where available. CSRF-protect the upload endpoint.

### 9. Rate limiting

In-memory limiters (the Express `express-rate-limit` default store, a module-level `Map`) count per instance. Vercel functions and Cloud Run scale out, so the limit leaks. Use a shared limit:

- **Vercel WAF rate limiting:** a Firewall rule with the Rate Limit action, available on all plans. Counters are tracked per region.
- **Cloud Armor rate limiting:** enforced on the load balancer in front of Cloud Run.
- **App-level with a shared store,** e.g. `@upstash/ratelimit` on Redis. This adds a dependency, so do the package-safety review in section 10 first:

  ```ts
  import { Ratelimit } from '@upstash/ratelimit'
  import { Redis } from '@upstash/redis'

  const ratelimit = new Ratelimit({
    redis: Redis.fromEnv(),
    limiter: Ratelimit.slidingWindow(10, '10 s'),
  })

  const { success } = await ratelimit.limit(identifier)
  if (!success) return new Response('Too many requests', { status: 429 })
  ```

Key limits on the user id for authenticated routes and the IP for anonymous ones. Apply stricter limits to login, signup, password reset, OTP, and expensive endpoints.

### 10. Dependencies and CI

- Report-only checks: `npm audit` (`--audit-level` changes only the exit threshold) and `npm audit signatures`. Run `govulncheck ./...` if it is already installed.
- Do not run `npm audit fix`, `npm update`, or any `npm install`, `pip install`, `uv add`, or `go install` as part of a review. `npm audit fix` runs a full install and can jump outside declared ranges with `--force`. Any package that is new or bumped goes through the user's package-safety rule first: check for typosquatting, publisher, age, download count, known CVEs, install scripts, and transitive dependencies; pin the version; report before installing.
- Commit lockfiles. CI installs with `npm ci`.
- GitHub Actions: pin third-party actions to a full commit SHA. Keep the default `GITHUB_TOKEN` read-only and raise permissions per job. Dependabot's `cooldown` option delays adopting brand-new releases.

### 11. Errors and logging

- Clients get a generic message and a code. Stack traces, SQL errors, and internal ids stay in server logs.
- Never log passwords, tokens, secrets, session ids, or full card numbers. Do log failed logins and admin actions.

## Pre-merge checklist

- [ ] The secret, env-file, `NEXT_PUBLIC_`, echo/export, and `gcloud secrets` greps are clean, or each hit is explained.
- [ ] No raw SQL built by template literal, f-string, `%`, `+`, or `fmt.Sprintf`.
- [ ] Every new route handler, Server Action, and proxy verifies the caller with `getClaims()`/`getUser()` (or the service's equivalent) and checks ownership.
- [ ] No `getSession()` in server code.
- [ ] Every new table in an exposed Supabase schema has RLS enabled and policies in the same migration.
- [ ] No new `dangerouslySetInnerHTML`, `innerHTML`, `eval`, `new Function`, `child_process.exec`, `os.system`, or `pickle.load(s)` without a written justification.
- [ ] The CSP comes from a nonce in `proxy.ts` (or SRI); any `'unsafe-inline'` is recorded as debt.
- [ ] Cookie-authenticated state changes outside Server Actions check `Origin`/`Sec-Fetch-Site` and carry a CSRF token.
- [ ] Uploads: allowlisted extension, content-based type check, generated name, size limit, stored outside the web root.
- [ ] Rate limits use a shared counter (WAF, Cloud Armor, or a shared store), not process memory.
- [ ] New or bumped dependencies passed the package-safety review. Workflow actions are SHA-pinned with minimal `permissions`.

## Sources

Checked 2026-10-26.

- OWASP Top 10:2025: https://top10.owasp.org/2025
- OWASP File Upload Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- OWASP CSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP Session Management Cheat Sheet (cookie attributes, `__Host-`): https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- MDN Set-Cookie (`__Host-` prefix, SameSite default): https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie
- Next.js CSP guide (nonce in `proxy.ts`, dynamic rendering, SRI, header without nonce): https://nextjs.org/docs/app/guides/content-security-policy
- Next.js data security (Server Actions CSRF, `allowedOrigins`, auth inside actions, `NEXT_PUBLIC_`, `server-only`): https://nextjs.org/docs/app/guides/data-security
- Next.js route handlers (`Response.json`, `request.json()`, `request.formData()`): https://nextjs.org/docs/app/api-reference/file-conventions/route
- Supabase Next.js server-side auth (`getClaims()`, `getSession()` warning, `proxy.ts`): https://supabase.com/docs/guides/auth/server-side/nextjs?router=app
- Supabase SSR advanced guide (HttpOnly FAQ, cookie storage): https://supabase.com/docs/guides/auth/server-side/advanced-guide
- Supabase Row Level Security: https://supabase.com/docs/guides/database/postgres/row-level-security
- Cloud Run secrets (`--update-secrets`, `--set-secrets`, accessor role, version pinning): https://docs.cloud.google.com/run/docs/configuring/services/secrets
- Cloud Run deploy (`gcloud run deploy SERVICE --image IMAGE_URL`): https://docs.cloud.google.com/run/docs/deploying
- Secret Manager access: https://docs.cloud.google.com/secret-manager/docs/access-secret-version
- node-postgres parameterized queries: https://node-postgres.com/features/queries
- psycopg 3 parameters and `sql.Identifier`: https://www.psycopg.org/psycopg3/docs/basic/params.html
- Zod 4 changelog (`z.email()`, `.issues`) and basics (`safeParse`): https://zod.dev/v4/changelog, https://zod.dev/basics
- DOMPurify README: https://github.com/cure53/DOMPurify
- express-rate-limit configuration (`limit`, MemoryStore): https://express-rate-limit.mintlify.app/reference/configuration
- Vercel WAF rate limiting: https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting
- Cloud Armor rate limiting: https://docs.cloud.google.com/armor/docs/rate-limiting-overview
- Upstash ratelimit: https://github.com/upstash/ratelimit-js
- npm audit: https://docs.npmjs.com/cli/v11/commands/npm-audit
- govulncheck: https://go.dev/doc/tutorial/govulncheck
- GitHub Actions secure use (SHA pinning, token permissions): https://docs.github.com/en/actions/reference/security/secure-use
- Dependabot `cooldown`: https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file
- Claude Code skill argument substitution: https://code.claude.com/docs/en/skills
- Claude Code security-guidance plugin (sink list used in the XSS grep): https://code.claude.com/docs/en/security-guidance
- git diff (`A...B`, `--name-only`, `--diff-filter`): https://git-scm.com/docs/git-diff
- POSIX grep (`-E`, `-i`, `-n`, `-v`, `-l`): https://pubs.opengroup.org/onlinepubs/9799919799/utilities/grep.html

## Provenance

Adapted from the `security-review` skill in everything-claude-code (MIT). See `NOTICE.md` and `LICENSE.txt`.
