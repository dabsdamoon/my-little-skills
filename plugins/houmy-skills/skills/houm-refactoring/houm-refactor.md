---
description: Audit codebase for refactoring opportunities and execute safe, atomic refactorings with test verification. Use with optional target like "/refactor prompts" or "/refactor app/services/retrieval.py".
---

# Refactor Command

This command invokes the **houm-refactoring** skill to systematically refactor code.

## How It Works

1. **Audit** the target (or entire codebase if no target specified)
2. **Present findings** categorized by risk and impact
3. **Wait for user approval** before making changes
4. **Execute atomically** -- one refactoring at a time, tests after each
5. **Report** what changed and verify all tests pass

## Usage

```
/refactor                          # Audit entire codebase
/refactor prompts                  # Refactor prompt system
/refactor app/services             # Refactor service layer
/refactor app/routers/sources.py   # Refactor specific file
/refactor dead-code                # Find and remove dead code only
/refactor implicit                 # Find and fix implicit/magic patterns only
```

## Execution Steps

### If target is a file or directory:

1. Read the target files
2. Check file sizes, function sizes, nesting depth
3. Identify specific refactoring opportunities using the catalog (R1-R7)
4. Present plan with risk assessment
5. **WAIT for user confirmation**
6. Execute and verify

### If target is "dead-code":

1. Run detection:
   ```bash
   conda run -n houmy ruff check app/ --select F401,F841
   ```
2. Categorize as SAFE / CAUTION / DANGER
3. Present list
4. **WAIT for user confirmation**
5. Delete atomically, test after each

### If target is "implicit":

1. Search for implicit patterns:
   ```bash
   grep -rn "importlib\|vars(module)\|getattr.*(" app/ prompts/ --include="*.py"
   ```
2. For each finding, propose explicit replacement
3. **WAIT for user confirmation**
4. Replace and verify

## Verification

After every change:
```bash
conda run -n houmy pytest
cd web && npx tsc --noEmit  # if frontend files changed
```

## Integration

- Use `/plan` first for large-scale refactoring across many files
- Use `/code-review` after refactoring to catch quality issues
- Use `/refactor dead-code` as part of regular maintenance
