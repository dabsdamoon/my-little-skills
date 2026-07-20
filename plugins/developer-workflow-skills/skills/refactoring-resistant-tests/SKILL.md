---
name: refactoring-resistant-tests
description: Use when writing, modifying, repairing, or reviewing automated tests of any kind, including unit, component, API, integration, and end-to-end tests. Also use when a feature needs coverage or tests broke after a refactor. Applies to Vitest, Jest, pytest, Testing Library, Playwright, SQLite fixtures, connector and parser tests, deployment scripts, selectors, assertions, fixtures, and mocking decisions.
---

# Refactoring-Resistant Tests

Make tests fail only when observable behavior changes. Couple tests to what a user or API consumer can observe, not to internal organization.

## Required workflow

1. Read the test, the production boundary it exercises, and nearby tests.
2. Run the narrowest relevant test before editing.
3. State the contract in one sentence: input, observable output, and required side effects.
4. Classify the change:
   - **Behavior-preserving refactor:** preserve expected values and effects; change only obsolete setup, wiring, or selectors.
   - **Intentional behavior change:** derive expectations from the request or domain contract, never from the implementation alone.
   - **Regression fix:** prove the old defect fails and the corrected behavior passes.
5. Choose the narrowest stable test boundary.
6. Make the smallest test change that proves the contract.
7. Run the focused test, then the appropriate broader checks.
8. Explain why any assertion changed.

If the contract is unclear, inspect callers, documentation, schemas, or fixtures. Do not copy the current output into an assertion merely to make the test pass.

## Choose a stable boundary

| Subject | Prefer asserting | Avoid coupling to |
|---|---|---|
| Pure logic | Return values and documented edge cases | Private helpers and intermediate values |
| Parsers and adapters | Normalized records, rejection rules, and idempotency | SDK call order and temporary parsing structures |
| Persistence | Public repository behavior using a temporary database | SQL text, live databases, and private query builders |
| Jobs and pipelines | Final status, persisted effects, stable error codes, and retry behavior | Incidental logs and process internals |
| UI | Roles, accessible names, stable test IDs, URLs, and user-visible outcomes | CSS classes, DOM depth, and generated bundle names |
| Executable scripts | Exit codes, resulting files or state, and coarse contract markers when execution is impractical | Whitespace, command construction details, and snapshots |

## The mocking rule: only fake what you do not own

**Allowed to fake** at external boundaries:

- Network and transport using MSW, respx, responses, or a `fetch` stub returning real `Response` objects
- Third-party SDKs such as payment, LLM, storage, and authentication providers
- Native or bridge modules, filesystem, clock, environment variables, stdin, and terminal
- The database driver level, though a real temporary database is usually better

**Do not module-mock internal collaborators:** project-owned hooks, contexts, components, services, repositories, query layers, utilities, or ORM code. Construct real collaborators through providers, constructor arguments, or dependency injection. When a real collaborator cannot run in a test, inject a fake at the composition boundary instead of mocking its module path.

## Recipe per layer

| Layer | Arrange | Act | Assert |
|---|---|---|---|
| React component | Render with real providers; fake network through MSW or `fetch` with real `Response` objects | Use `userEvent`; React Native may use its framework event API | Use role, name, text, visibility, enabled state, and stable outcomes |
| Backend API | Use the real service and repository with an in-memory, temporary, or test database; fake external APIs at transport | Exercise the HTTP entry point | Assert status and contractual response fields |
| Pure logic or hooks | Avoid mocks by design | Call the public function | Assert return values or observable state |
| End to end | Run the real app | Use real interactions | Prefer role, name, text, URL, and durable effects |

## Assertion design

- Do not weaken exact contractual values into truthiness, broad regular expressions, or mere existence.
- Use full object equality only when every field is part of the contract; otherwise assert the relevant fields.
- Derive expected values independently from the implementation under test.
- Use explicit timestamps or an injected clock for time-dependent behavior.
- Assert ordering only when ordering is contractual.
- Use isolated temporary databases and close all handles.
- In Playwright, use web-first assertions; do not use fixed sleeps such as `waitForTimeout` to hide synchronization problems.
- For regressions, record red-green evidence: the focused test must fail for the defect and pass with the fix.

## Existing bad tests are not a license

Match existing naming, file layout, and formatting, but do not copy coupling patterns. If older tests mock internal modules, use synthetic browser events, or query CSS classes, avoid spreading those patterns and note the existing risk briefly.

## Red flags

- `vi.mock`, `jest.mock`, `patch`, or `monkeypatch.setattr` targeting project-owned source modules
- `fireEvent` in a web test when realistic user interaction is available
- `container.querySelector`, `.closest()`, `toHaveClass`, CSS selectors, or DOM-structure assertions
- Snapshot assertions used in place of an explicit contract
- Calls to private methods or bypassing an existing public entry point
- Interaction assertions against mocks of project-owned modules
- Updating expected output solely because the current implementation produced it
- Broadening or deleting an assertion without identifying a changed requirement

## Example

```tsx
// Bad: mocks owned modules, fires a synthetic event, and asserts styling.
vi.mock("../../contexts/AuthContext", () => ({ useAuth: () => fakeUser }));
vi.mock("../../api/client", () => ({ apiFetch: apiFetchMock }));
fireEvent.click(container.querySelector(".bell__button")!);
expect(container.querySelector(".bell")).toHaveClass("bell--open");

// Good: uses real providers, fakes the external boundary, and proves a visible outcome.
vi.stubGlobal("fetch", async () =>
  Response.json({ notifications: [{ id: 1, message: "Deploy finished", read: false }] }));
render(
  <AuthProvider user={fakeUser}>
    <LanguageProvider><NotificationBell /></LanguageProvider>
  </AuthProvider>,
);
await user.click(screen.getByRole("button", { name: "Notifications" }));
expect(await screen.findByText("Deploy finished")).toBeVisible();
```

## Completion gate

Before finishing, answer all five questions:

1. Does the test describe behavior rather than implementation structure?
2. Would an internal refactor with identical behavior still pass?
3. Would a real behavior regression make it fail?
4. Are time, data, network, and persistence dependencies deterministic and isolated?
5. Did the focused test and the appropriate broader checks pass?

When a project has no test linting, offer deterministic enforcement once rather than silently installing it. Useful options include Testing Library lint rules and narrowly scoped restrictions on internal module mocks.
