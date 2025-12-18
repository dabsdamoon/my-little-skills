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
- [ ] Kakao SSO on web browser - still works (regression test)
- [ ] Profile completion form displays correctly
- [ ] Profile completion submits successfully

---

## Why Web Worked But Mobile Didn't

| Issue | Web | Mobile |
|-------|-----|--------|
| URL Scheme | `https://` (standard) | `looktake://` (not handled) |
| WebView | N/A | Stayed on Kakao page |
| API Email Param | Included | Missing |
| Navigation | Stays on URL | Lost params |

---

## Notes for Reviewers

- Parts 1-2 are iOS native (Swift) issues
- Parts 3-4 are frontend code divergence issues where native components weren't kept in sync with web
- Consider adding shared utilities to prevent web/native divergence in the future
