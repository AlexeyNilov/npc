# Implementer Guide

## Responsibility

Implement one Ready outcome without redesigning its accepted contracts.

## Execution

1. Inspect the working tree and task-local execution path.
2. Write a failing behavioral test before behavior-changing application logic.
3. Make the smallest change that satisfies the acceptance criteria; refactor
   only after focused tests pass.
4. Update only authorized files and named information owners.
5. Run task-specific checks, `make check` then return
   the [workflow handoff](../agent-workflow.md#handoff).

Documentation and configuration work uses applicable contract checks rather than
artificial behavioral tests. Follow [CONTRIBUTING.md](../../CONTRIBUTING.md) for
engineering and verification standards.

Stop when implementation requires an unaccepted behavior, public contract, data
meaning, dependency, authority decision, or scope expansion.
