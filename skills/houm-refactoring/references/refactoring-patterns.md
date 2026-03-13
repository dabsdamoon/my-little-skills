# Refactoring Patterns Quick Reference

Based on refactoring.guru patterns, adapted for Python/FastAPI + React/Vite.

## Composing Methods

| Technique | When | Example |
|-----------|------|---------|
| Extract Method | Function >50 lines or doing multiple things | Pull nested loop into `_find_matching_documents()` |
| Inline Method | Wrapper adds no value | Remove `get_db_session()` that just calls `next(get_db())` |
| Replace Temp with Query | Temp variable used once for a computed value | `total = len(items)` -> use `len(items)` directly |

## Moving Features Between Objects

| Technique | When | Example |
|-----------|------|---------|
| Move Method | Method uses more data from another class | Move `format_response()` from router to service |
| Extract Class | Class has 2+ unrelated responsibilities | Split `RetrievalService` into `DocumentRetriever` + `ResponseGenerator` |
| Inline Class | Class does almost nothing | Merge thin wrapper into its only consumer |

## Organizing Data

| Technique | When | Example |
|-----------|------|---------|
| Replace Magic Number/String | Literal strings used as keys | `"acog_document"` -> `PromptVariant.ACOG_DOCUMENT` |
| Replace Type Code with Strategy | Behavior varies by string type field | `source_type` dispatch -> `SourceProcessor` protocol |
| Introduce Parameter Object | Same params repeated across 3+ functions | `(source_id, doc_id, db)` -> `DocumentRef` + `db` |

## Simplifying Conditionals

| Technique | When | Example |
|-----------|------|---------|
| Decompose Conditional | Complex `if` with long branches | Extract branches into named methods |
| Replace Nested Conditional with Guard Clauses | Deep nesting with early-exit conditions | `if not x: return` at top |
| Replace Conditional with Polymorphism | `if/elif` chain on type | Strategy pattern per type |

## Simplifying Method Calls

| Technique | When | Example |
|-----------|------|---------|
| Replace Parameter with Explicit Methods | String param selects behavior | `process(mode="embed")` -> `embed()` and `search()` |
| Preserve Whole Object | Passing 3+ fields from same object | Pass the object instead |
| Replace Error Code with Exception | Returning None/False for errors | Raise specific exceptions |

## Dealing with Generalization

| Technique | When | Example |
|-----------|------|---------|
| Pull Up Method | Same method in 2+ subclasses | Move to base class or mixin |
| Replace Inheritance with Delegation | Subclass only uses part of parent | Composition over inheritance |
| Collapse Hierarchy | Parent and child barely differ | Merge into one class |

## Python/FastAPI Specific

| Technique | When | Example |
|-----------|------|---------|
| Replace `**kwargs` with Pydantic model | Unknown params passed around | Define explicit `Config` model |
| Replace `getattr` dispatch with dict | Dynamic attribute access for routing | Explicit `HANDLERS: dict[str, Callable]` |
| Replace global state with Depends | Module-level singletons | FastAPI dependency injection |
| Replace `print()` with structlog | Debug prints left in code | `logger.info("event", key=value)` |

## React/TypeScript Specific

| Technique | When | Example |
|-----------|------|---------|
| Extract Custom Hook | Same `useState`+`useEffect` in 2+ components | `useDocumentFetch(docId)` |
| Replace inline fetch with hook | `fetch()` calls scattered in components | Shared `useApi()` hook |
| Stabilize callback refs | `useCallback` deps cause re-render loops | Move to `useRef` or extract outside |
| Replace prop drilling with context | Props passed through 3+ levels | Create focused context provider |
