---
name: refactoring-resistant-tests
description: Use when writing or modifying automated tests of any kind — unit, component, API, integration, or e2e — including when a feature implementation needs tests, when asked to add test coverage, or when a test broke after a refactor. Especially use before imitating an existing test file's conventions. Works in both Claude Code and Codex (pure guidance, no runtime-specific tools). Triggers: write tests, add coverage, vitest, jest, pytest, testing-library, fireEvent, vi.mock, jest.mock, MagicMock, monkeypatch, MSW, TestClient, brittle tests, tests broken by refactoring.
---

# Refactoring-Resistant Tests

A test may fail only when observable behavior changes — never because internal structure changed. Tests couple to what the user or API consumer can see, not to how the code is organized. A test coupled to implementation becomes a false alarm on every refactor, and false alarms get deleted or blindly "fixed" until the suite protects nothing.

## The Mocking Rule: only fake what you don't own

**Allowed to fake** (external boundaries):
- Network/transport: MSW, respx, responses, or a `fetch` stub returning real `Response` objects
- Third-party SDKs (payment, LLM, storage, auth providers), native/bridge modules
- Filesystem, clock, env vars, stdin/terminal
- The DB driver level — or better, a real DB (in-memory repo, tmpdir, local container)

**Never module-mock** (internal collaborators): your project's own hooks, contexts, components, services, repositories, query layers, utils, or ORM. If an internal collaborator is hard to set up, construct the real one — providers take props, services take constructor args. If a real one truly can't run in a test, inject a fake at the composition seam (constructor/props/DI override); do not `vi.mock`/`patch` the module path.

## Recipe per layer

| Layer | Arrange | Act | Assert |
|---|---|---|---|
| React component | Render with **real** providers; fake network via MSW or `vi.stubGlobal("fetch", ...)` with real `Response`s | `userEvent` (never `fireEvent`; React Native's `fireEvent` is the exception — RNTL has no userEvent) | `screen.getByRole`/`getByText`; semantic matchers: `toBeVisible`, `toBeDisabled`, `toHaveTextContent` |
| Backend API | Real service + repo (in-memory/tmp/real DB); fake only external APIs at transport (respx/responses) or swap the gateway object at the composition seam | Through the HTTP entry point: `TestClient`, `app.inject`, supertest, `app.request` | Status code + the specific fields that matter; full-body equality only for small, intentional wire contracts |
| Pure logic / hooks | Nothing to mock by design | Call the public function directly | Return values / observable state |
| e2e (Playwright) | Real app | Real interactions | `get_by_role`/`get_by_text`, not CSS selectors |

## Existing bad tests are not a license

"Match the existing style" applies to naming, file layout, and formatting — **not** to coupling patterns. If the repo's existing tests mock internal modules, use `fireEvent`, or query CSS classes, do not propagate those patterns into new tests. Write the new test with the recipe above (it will coexist fine), and tell the user in one line that the older tests are implementation-coupled.

## Red flags — stop and rewrite the test

- `vi.mock`/`jest.mock`/`patch(...)`/`monkeypatch.setattr(...)` targeting a path inside your own `src/`/`app/`
- `fireEvent` in a web (non-React-Native) test
- `container.querySelector`, `.closest()`, `toHaveClass`, asserting CSS class names or DOM structure
- `toMatchSnapshot`
- Calling `_private` methods or reaching past an existing HTTP entry point
- `expect(myOwnModuleMock).toHaveBeenCalledWith(...)` — interaction asserts belong only on external-boundary fakes

## Rationalizations

| Excuse | Reality |
|---|---|
| "The existing tests do it this way" | Consistency covers style, not coupling. Bad patterns propagate exactly this way. |
| "Mocking the hook isolates the component" | The hook is the component's implementation. Render it real; fake the network instead. |
| "MSW isn't installed, so I'll mock our api module" | Stub `fetch` with real `Response` objects — same isolation, correct boundary. |
| "fireEvent is simpler" | `userEvent` is the same length and survives handler refactors. |
| "Asserting the class name proves it rendered" | Assert what a user sees: role, text, visibility, disabled state. |
| "Testing `_private` directly is more focused" | Privates change freely under refactoring. Test through the public caller. |

## One example (bad → good)

```tsx
// BAD: mocks own modules, fires synthetic events, asserts DOM structure
vi.mock("../../contexts/AuthContext", () => ({ useAuth: () => fakeUser }));
vi.mock("../../api/client", () => ({ apiFetch: apiFetchMock }));
fireEvent.click(container.querySelector(".bell__button")!);
expect(container.querySelector(".bell")).toHaveClass("bell--open");

// GOOD: real providers, boundary fake, user-level act, semantic assert
vi.stubGlobal("fetch", async () =>
  Response.json({ notifications: [{ id: 1, message: "Deploy finished", read: false }] }));
render(<AuthProvider user={fakeUser}><LanguageProvider><NotificationBell /></LanguageProvider></AuthProvider>);
await user.click(screen.getByRole("button", { name: "Notifications" }));
expect(await screen.findByText("Deploy finished")).toBeVisible();
```

## Guardrails (offer once per project)

When adding tests to a project with no test lint, offer — do not silently install — deterministic enforcement: `eslint-plugin-testing-library` (`prefer-user-event`, `no-node-access`, `no-container`) plus a `no-restricted-syntax` rule banning `vi.mock`/`jest.mock` outside a shared `test/mocks/` folder, so the mock whitelist becomes syntax, not judgment.
