# Example PR: Bug Fix

This example demonstrates a well-structured PR for fixing bugs, particularly useful for debugging issues that span multiple layers (native, frontend, backend).

---

# PR: Fix Kakao SSO for iOS - Handle Deep Links and Profile Completion

**Branch:** `feat/kakao_sso_ios` → `develop`
**Date:** 2025-12-17
**Total Files Changed:** 6 (0 new, 6 modified)

## Summary

This PR fixes Kakao SSO login that worked on web but failed on iOS native app. The issue involved multiple problems: WebView not handling custom URL schemes, missing API parameters, and navigation losing URL query params.

**Key Fixes:**
- iOS WebView now intercepts `looktake://` deep links and redirects properly
- Fixed missing `email` parameter in profile completion API calls
- Fixed URL params being lost during page navigation

---

## Blast Radius

| File | Dependents | Radius | Notes |
|------|-----------|--------|-------|
| `capacitor.config.ts` | build config | **CRITICAL** | Changes the deployment server URL — affects every build, not just SSO. Verify the value is correct for the target environment before merge |
| `client/src/native/hooks/useAuth.ts` | 8 files | **HIGH** | Shared auth hook consumed across the native app |
| `ios/App/App/AppDelegate.swift` | app entry | **HIGH** | Every launch path goes through here |
| `ios/App/KakaoURLHandler.swift` | 1 file | MEDIUM | Only `AppDelegate` calls it |
| `client/src/native/components/login-modal/CompleteProfileScreen.tsx` | 2 files | MEDIUM | Rendered by login modal and profile page |
| `client/src/native/pages/CompleteProfilePage.tsx` | 0 files | LOW | Leaf route |

**Overall Blast Radius:** HIGH — a config file and a shared auth hook are both in scope.

---

## Security Analysis

**Rating:** CONCERN

| Category | Finding | Severity | File |
|----------|---------|----------|------|
| Sensitive Data | User email placed in a URL query string, where it lands in browser history, server logs, and `Referer` headers | **CONCERN** | `client/src/native/pages/CompleteProfilePage.tsx` |
| Sensitive Data | Email interpolated into an API URL unencoded — breaks on `+` in addresses and leaks PII to access logs | **CONCERN** | `client/src/native/components/login-modal/CompleteProfileScreen.tsx` |
| Misconfiguration | Deployment server URL changed | NOTE | `capacitor.config.ts` |

> **Action Required:** Both findings pass PII through URLs. The navigation fix already reaches for `encodeURIComponent`, which addresses correctness but not exposure. Prefer passing `email` through app state or a POST body. If a URL param is genuinely unavoidable here, say so explicitly in this section so the reviewer can accept the tradeoff deliberately rather than by omission.

---

## Deviations from Spec

The reference implementation for this flow is the working web client — "make native behave like web."

| Type | Item | Spec said | This PR does | Why |
|------|------|-----------|--------------|-----|
| Deviation | Param passing after profile completion | Web keeps `email`/`provider` in session state | Native passes them as URL query params | Native routing remounts the page and loses in-memory state. This is a workaround for the remount, not a chosen design — see the Security finding above |
| Deferred | Android deep-link handling | Both platforms should intercept `looktake://` | iOS only | Android was not reproducing the failure; deferring rather than shipping an untested handler |
| Spec defect | Deep-link scheme undocumented | No spec covers `looktake://` ownership | Surfaced only | The scheme is registered in two places with no doc. Not corrected here — needs an owner |

---

## Major Changes

### 1. iOS Deep Link Handling (Native)

**Files Changed:**
- `ios/App/KakaoURLHandler.swift`
- `ios/App/App/AppDelegate.swift`

**Why:**
The WebView couldn't handle `looktake://` custom URL scheme. When backend redirected to `looktake://register-incomplete?email=...`, the WebView failed silently.

**Root Cause:**
```swift
// Before: Only Kakao schemes handled
static let kakaoSchemes = ["kakaolink", "kakaokompassauth", "kakaotalk"]

// After: Added looktake scheme
static let externalSchemes = ["kakaolink", "kakaokompassauth", "kakaotalk", "looktake"]
```

---

### 2. Frontend Missing Email Parameter

**Files Changed:**
- `client/src/native/components/login-modal/CompleteProfileScreen.tsx`
- `client/src/native/hooks/useAuth.ts`

**Why:**
Native app had diverged from web implementation. The API call was missing the required `email` parameter.

**Root Cause:**
```typescript
// Web (correct)
apiRequest("GET", `/api/sso/incomplete-profile?email=${email}`)

// Native (broken - missing email)
apiRequest("GET", '/api/sso/incomplete-profile')
```

---

### 3. URL Params Lost on Navigation

**Files Changed:**
- `client/src/native/pages/CompleteProfilePage.tsx`

**Why:**
Native `CompleteProfilePage` immediately navigated to `/explore`, losing the `email` and `provider` query params.

**Root Cause:**
```typescript
// Before: Navigates away, params lost
navigate("/explore");

// After: Preserve params
navigate(`/explore?email=${encodeURIComponent(email)}&provider=${provider}`);
```

---

## All Files Changed

### iOS Native (2 files)

| File | Change | Purpose |
|------|--------|---------|
| `ios/App/KakaoURLHandler.swift` | Modified | Handle `looktake://` scheme, redirect WebView |
| `ios/App/App/AppDelegate.swift` | Modified | Setup WebView navigation delegate |

### Frontend (3 files)

| File | Change | Purpose |
|------|--------|---------|
| `client/src/native/components/login-modal/CompleteProfileScreen.tsx` | Modified | Add email to API calls |
| `client/src/native/hooks/useAuth.ts` | Modified | Add email to CompleteSsoData interface |
| `client/src/native/pages/CompleteProfilePage.tsx` | Modified | Preserve URL params on navigation |

### Config (1 file)

| File | Change | Purpose |
|------|--------|---------|
| `capacitor.config.ts` | Modified | Update server URL for deployment |

---

## Environment Variables

> No new environment variables required.

---

## Testing Checklist

- [ ] Kakao SSO on iOS simulator - new user (incomplete profile)
- [ ] Kakao SSO on iOS simulator - existing user (direct login)
- [ ] Kakao SSO on TestFlight - new user
- [ ] Kakao SSO on TestFlight - existing user
- [ ] Kakao SSO on web browser - still works ⚠️ **automatable** — suggest an E2E regression test; this path is the one most likely to break silently
- [ ] Profile completion form displays correctly
- [ ] Profile completion submits successfully ⚠️ **automatable** — suggest a unit test asserting the `email` param is present in the API call, which is exactly the bug fixed here

---

## Why Web Worked But Mobile Didn't

| Issue | Web | Mobile |
|-------|-----|--------|
| URL Scheme | `https://` (standard) | `looktake://` (not handled) |
| WebView | N/A | Stayed on Kakao page |
| API Email Param | Included | Missing |
| Navigation | Stays on URL | Lost params |

---

## Not Included / Out of Scope

- **Android deep-link handling** — deferred, see Deviations. Android SSO still fails on the same class of bug
- **Shared web/native utility for the auth call** — the root cause of two of these three bugs is native code drifting from web. Nothing in this PR prevents it recurring
- **Regression test for the deep-link path** ⚠️ **automatable** — an integration test asserting `looktake://` resolves to the profile screen would have caught this before TestFlight
- **PII-in-URL fix** — the security findings above are documented but not resolved here; resolving them properly means reworking how native passes auth context between routes

---

## Notes for Reviewers

- Parts 1-2 are iOS native (Swift) issues
- Parts 3-4 are frontend code divergence issues where native components weren't kept in sync with web
- Consider adding shared utilities to prevent web/native divergence in the future
