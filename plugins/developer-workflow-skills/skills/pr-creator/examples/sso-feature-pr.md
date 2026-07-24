# Example PR: SSO Feature Implementation

This example demonstrates a well-structured PR for a complex feature involving multiple platforms (iOS, Android, Web).

---

# PR: Add Apple and Kakao SSO Login (Frontend)

**Branch:** `feat/apply_social_login` → `develop`
**Date:** 2025-12-12
**Total Files Changed:** 20 (2 new, 18 modified)

## Summary

This PR implements Apple Sign-in and Kakao Login using JavaScript SDK approach (not passport.js), following the same pattern as the existing Google SSO implementation.

**Key Features:**
- Apple Sign-in with popup-based authentication (Apple JS SDK)
- Kakao Login with redirect-based authentication (Kakao JS SDK)
- Native iOS/Android handlers for Kakao hybrid WebView support
- SSO profile completion flow with optional fullName field
- Provider tracking to correctly save `provider='apple'` or `provider='kakao'`

---

## Blast Radius

| File | Dependents | Radius | Notes |
|------|-----------|--------|-------|
| `client/src/hooks/use-auth.tsx` | 23 files | **CRITICAL** | Auth context for the entire web app. `CompleteSsoData` is a public type — changing it ripples to every consumer |
| `client/src/native/hooks/useAuth.ts` | 8 files | **HIGH** | Native equivalent of the above |
| `ios/App/App/AppDelegate.swift` | app entry | **HIGH** | Registers URL handlers on every launch |
| `android/.../MainActivity.java` | app entry | **HIGH** | Registers the WebViewClient on every launch |
| `client/src/components/login-modal.tsx` | 4 files | MEDIUM | Rendered from several entry points |
| `ios/App/App/Info.plist` | build config | MEDIUM | URL scheme registration; requires a native rebuild |
| `client/src/pages/explore-page.tsx` | 1 file | LOW | **Unrelated to SSO** — see Deviations |
| `client/public/config.js` | 0 files | LOW | Whitespace only |

**Overall Blast Radius:** CRITICAL — this PR modifies the auth layer on both web and native.

---

## Security Analysis

**Rating:** NOTE — appropriate for an auth change, but it warrants a careful review rather than a skim.

| Category | Finding | Severity | File |
|----------|---------|----------|------|
| Broken Auth | Apple `identityToken` is verified server-side, not trusted client-side | NOTE (correct) | `client/src/components/login-modal.tsx` |
| Sensitive Data | `VITE_`-prefixed env vars are bundled into the client bundle | NOTE | `.env` |
| Broken Auth | `(window as any).AppleID` bypasses type checking on an auth-critical path | NOTE | `client/src/components/login-modal.tsx` |

Detail:

- **Token verification is in the right place.** The client forwards `identityToken` and the backend verifies it. Flagged as a NOTE so a reviewer confirms the backend PR actually does this — the security of the whole flow rests on it.
- **`VITE_APPLE_CLIENT_ID` and `VITE_KAKAO_JS_KEY` are public by design** — both are client identifiers, not secrets. Called out so nobody later adds a real secret to that block by pattern-matching.
- **The `as any` casts are on the auth path.** Not exploitable, but it means an SDK shape change fails at runtime rather than at build time.

---

## Deviations from Spec

| Type | Item | Spec said | This PR does | Why |
|------|------|-----------|--------------|-----|
| Deviation | Auth mechanism | Follow the existing passport.js pattern used by Google SSO | Uses the Apple/Kakao JS SDKs instead | No server redirect needed, and both providers ship a first-party SDK. Means SSO providers now use two different patterns — accepted, and worth revisiting if a third is added |
| Deviation | `fullName` on registration | Required at registration | Optional for SSO | Apple returns the name only on **first** sign-in, so requiring it would hard-block returning users. Matches existing Google SSO behaviour |
| Deferred | Kakao availability | Available to all users | Shown only where `isKorea` is true | Kakao has negligible usage elsewhere. The gate is a display condition, not an entitlement check — do not rely on it for authorization |
| Scope creep | `explore-page.tsx` avatar handling | Not part of this feature | Included anyway | **Should have been a separate PR.** Called out so a reviewer does not assume it was reviewed as part of SSO |

---

## Major Changes

### 1. Apple Sign-in (Web + Native)

**Files Changed:**
- `client/src/components/login-modal.tsx`
- `client/src/native/components/login-modal/LoginModal.tsx`

**Why:**
- Apple Sign-in implemented using Apple JS SDK with popup-based authentication
- Removed legacy passport-apple approach in favor of JS SDK (simpler, no server redirect needed)
- Apple only provides user's full name on **first sign-in**, so fullName field is editable when not provided

**Key Implementation:**
```typescript
// Dynamically load Apple JS SDK
(window as any).AppleID.auth.init({
  clientId: APPLE_CLIENT_ID,
  scope: 'name email',
  redirectURI: window.location.origin,
  usePopup: true,
});
const response = await (window as any).AppleID.auth.signIn();
// Send identityToken to backend for verification
```

---

### 2. Kakao Login (Web + Native)

**Files Changed:**
- `client/src/components/login-modal.tsx`
- `client/src/native/components/login-modal/LoginModal.tsx`
- `ios/App/App/KakaoURLHandler.swift` (NEW)
- `ios/App/App/AppDelegate.swift`
- `ios/App/App/Info.plist`
- `android/app/src/main/java/io/looktake/app/KakaoWebViewClient.java` (NEW)
- `android/app/src/main/java/io/looktake/app/MainActivity.java`

**Why:**
- Kakao Login implemented using Kakao JS SDK with redirect-based authentication
- Kakao only shown for users in Korea (`isKorea` check based on region)
- Native apps (iOS/Android) require special URL handlers for hybrid WebView support per [Kakao Hybrid Guide](https://developers.kakao.com/docs/latest/ko/javascript/hybrid)

**Native Handlers:**
- **iOS:** `KakaoURLHandler.swift` - Handles `kakaolink://`, `kakaokompassauth://`, `kakaotalk://` URL schemes
- **Android:** `KakaoWebViewClient.java` - Handles `intent://` URIs for launching KakaoTalk

---

### 3. SSO Profile Completion Flow

**Files Changed:**
- `client/src/components/login-modal.tsx`
- `client/src/hooks/use-auth.tsx`
- `client/src/native/components/login-modal/CompleteProfileScreen.tsx`
- `client/src/native/hooks/useAuth.ts`

**Why:**
- When new user signs in via SSO, they need to complete profile (username, birthDate)
- **fullName is optional** for SSO (same as Google SSO behavior)
- Fixed bug where Apple SSO was saving `provider='google'` instead of `provider='apple'`

---

## All Files Changed

### SSO-Related Files (17 files)

| File | Change | Purpose |
|------|--------|---------|
| `client/src/components/login-modal.tsx` | Modified | Apple/Kakao JS SDK integration, provider tracking |
| `client/src/native/components/login-modal/LoginModal.tsx` | Modified | Apple/Kakao JS SDK integration for native |
| `client/src/native/components/login-modal/CompleteProfileScreen.tsx` | Modified | Add fullName input, pass provider to backend |
| `client/src/hooks/use-auth.tsx` | Modified | Add fullName/provider to CompleteSsoData type |
| `client/src/native/hooks/useAuth.ts` | Modified | Add fullName/provider to CompleteSsoData type |
| `ios/App/App/KakaoURLHandler.swift` | **NEW** | iOS Kakao URL scheme handler |
| `ios/App/App/AppDelegate.swift` | Modified | Register Kakao URL handlers |
| `ios/App/App/Info.plist` | Modified | Add Kakao URL schemes |
| `android/app/src/main/java/io/looktake/app/KakaoWebViewClient.java` | **NEW** | Android Kakao intent handler |
| `android/app/src/main/java/io/looktake/app/MainActivity.java` | Modified | Register Kakao WebViewClient |

### Non-SSO Files (3 files)

| File | Change | Purpose |
|------|--------|---------|
| `client/public/config.js` | Modified | Whitespace formatting only (no functional change) |
| `client/src/pages/explore-page.tsx` | Modified | Avatar URL handling utility (unrelated to SSO) |

---

## Environment Variables

```env
# Apple SSO
VITE_APPLE_CLIENT_ID=io.looktake.signin

# Kakao SSO
VITE_KAKAO_JS_KEY=your-kakao-javascript-key
```

---

## Testing Checklist

- [x] Google SSO login (existing) - still works
- [x] Apple SSO login - new user registration
- [x] Apple SSO login - existing user login
- [x] Kakao SSO login - new user registration
- [x] Kakao SSO login - existing user login
- [x] SSO profile completion with fullName (optional)
- [x] Provider correctly saved in database (google/apple/kakao)
- [ ] Native iOS app - Kakao login with KakaoTalk
- [ ] Native Android app - Kakao login with KakaoTalk

---

## Related PRs / Dependencies

- Backend PR in `looktake-v2-server` - Apple/Kakao token verification endpoints

---

## Not Included / Out of Scope

- **Backend token verification** — lives in the `looktake-v2-server` PR listed above. This PR is not functional without it; do not merge alone
- **Automated tests for the SSO flows** ⚠️ **automatable** — every item in the checklist below was verified by hand. At minimum the provider-tracking bug (`provider='apple'` being saved as `'google'`) deserves a unit test, since it was a silent data-correctness bug
- **Native Kakao testing on real devices** — simulator only so far; the two unchecked boxes below
- **Consolidating the two SSO patterns** — Google uses passport.js, Apple/Kakao use JS SDKs. Deliberately not unified here; a third provider should force the decision
- **`explore-page.tsx` avatar change** — unrelated to SSO, see Deviations

---

## Notes for Reviewers

- The native handlers (iOS/Android) are required for Kakao login to work in mobile apps
- Apple Sign-in only provides the user's name on first authentication - subsequent logins won't include it
- Kakao login button is only visible to users in Korea
