# Implementer Guide

## Responsibility

Implement one Ready outcome without redesigning its contracts or information
ownership.

## Execution

1. Inspect the working tree and task-local execution path.
2. Restate only behavior-, interface-, data-, security-, or verification-affecting assumptions.
3. Before behavior-changing application logic, write a failing behavioral test.
4. Make the smallest coherent change satisfying the acceptance criteria.
5. Refactor only after focused tests pass.
6. Update only the named information owners and authorized files.
7. Run task-specific checks, `make check`, and one final `git diff --check`.
8. Return the handoff required by the [agent workflow](../agent-workflow.md).

Documentation and configuration work uses applicable contract checks rather than
artificial behavioral tests. Follow [CONTRIBUTING.md](../../CONTRIBUTING.md) for
engineering and verification standards.

Stop when implementation requires an unaccepted behavior, public contract, data
meaning, dependency, authority decision, scope expansion, or new information
owner.
