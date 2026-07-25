# Contributing

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

## Verification

Run the aggregate repository check:

```text
make check
```

Run `git diff --check` once on the final diff before handoff.
