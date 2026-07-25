# Contributing guide

## Purpose

- Contribute focused, maintainable changes that meet the requested need.

## Repository rules

- Think before coding and stay strictly within the prompt's scope.
- Never commit credentials, tokens, `.env`, or secret output.

## Simplicity first

Write the minimum code that solves the problem. Nothing speculative.

- Write the minimum code required to satisfy the user's request.
- No defensive error handling for impossible scenarios.
- No new external dependencies without explicit permission.
- If you write 200 lines and it could cleanly be 50, rewrite it.
- The test: *Can this be implemented with less code without breaking requirements?* If yes, simplify.

## Focused and modular design

Keep one responsibility per unit. Separate business logic from side effects.

- **Single responsibility:** Each function, class, or module must do one thing well and have only one reason to change.
- **Separation of concerns:** Keep core business rules isolated from I/O, database access, network calls, and UI/presentation.
- Avoid multi-purpose utility dumping grounds (`utils.py`) or "god" objects that handle unrelated tasks.
- Keep functions small and focused. If a function evaluates logic *and* performs side effects, split it.
- Separate concerns logically, but do not create unnecessary intermediate wrapper files or empty abstractions.

## Follow TDD workflow

Use red, green, refactor. Test behavior, not implementation.

- Write a failing behavioral test before writing implementation code.
- Every test must detect meaningful behavior that would regress if the code were wrong.
- Avoid asserting on internal implementation details or private methods.
- Mock only external boundaries (network, database, filesystem, third-party APIs).
- Use dependency injection to keep business logic easy to test.
- Omit obvious docstrings; use Google-style docstrings only for complex business logic.
- Update only the documentation artifact that owns the changed information.
- Bump the semantic version in the project manifest (`pyproject.toml`) after functional application changes.

## Surgical changes

Touch only what you must. Clean up only your own mess.

- Match existing style, formatting, and conventions, even if you'd write it differently.
- Don't "improve" or reformat adjacent code, comments, or styles.
- Don't refactor things that aren't broken or explicitly requested.
- **Self-created dead code:** Remove imports, variables, or functions that *your* changes made unused.
- **Pre-existing dead code:** Mention it in your text response. Do not delete or modify it.
- The test: *Every changed line must trace directly to the user's request.*

## Verification

Run the aggregate repository check:

```text
make check
```

Run `git diff --check` once on the final diff before handoff.
