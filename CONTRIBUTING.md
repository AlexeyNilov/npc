# Contributing

- Never commit credentials, tokens, `.env`, or secret output.
- Think before coding

## Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## Follow TDD workflow

- Inspect current Git state and preserve unrelated changes.
- For application behavior, write a failing behavioral test before implementation.
- Every test must detect meaningful project behavior that would regress if the code were wrong.
- Prefer a few high-signal scenarios and avoid implementation-detail assertions.
- Mock only external I/O, network, database, or service boundaries.
- Use dependency injection when it makes behavior easier to test.
- Use explicit type hints and keep functions and modules focused.
- Keep business logic, I/O, and logging separate.
- Use logging rather than print except in CLI-only scripts.
- Do not swallow exceptions; re-raise or log them with useful context.
- Omit obvious docstrings; use Google-style docstrings for non-obvious business rules.
- Avoid speculative abstractions and unjustified dependencies.
- Update only the documentation artifact that owns the changed information.
- Bump the semantic version after significant application changes.

## Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## Verification

Run the aggregate repository check:

```text
make check
```

Run `git diff --check` once on the final diff before handoff.
