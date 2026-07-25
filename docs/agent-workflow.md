# Agent Workflow

This document owns task lifecycle, delegation, context boundaries, and handoff.
Repository-wide behavior and information routing remain in
[AGENTS.md](../AGENTS.md).

## Select one role

Do not preload every guide automatically.

| Work | Role guide |
| --- | --- |
| Task preparation, or integration | [Planner](docs/agent_roles/planner.md) |
| Exploration or research | [Explorer](docs/agent_roles/explorer.md) |
| Plan or code simplification | [Simplifier](docs/agent_roles/simplifier.md) |
| Code, tests, configuration, or documentation implementation | [Implementer](docs/agent_roles/implementer.md) |

An assigned task's role guide is authoritative. Read exactly one role guide at a
time. If responsibility changes materially, finish or hand off the current work
before selecting another role.

## Operating loop

```text
planner: define outcome, route durable facts, prepare Ready work
    -> explorer, implementer, or simplifier: execute one bounded assignment
    -> compact evidence handoff
    -> planner: inspect, verify, integrate, or stop
```

Use the current control context while one bounded outcome remains active and its
planning evidence is still useful. Start a fresh context after a phase change,
long pause, or when completed work and raw logs dominate. A fresh launch brief is
ephemeral and contains only the outcome, canonical links or IDs, current Git
state, constraints, and done condition.

## Status lifecycle

1. **Planned:** dependencies or decisions remain unresolved.
2. **Ready:** outcome, context, write scope, verification, and stop conditions are complete.
3. **In progress:** one owner is executing the task.
4. **Review:** execution and task-local verification are complete.
5. **Blocked:** a named design or external condition prevents progress.
6. **Done:** findings are resolved and the planner accepted the result.

Only the planner marks Ready or Done. An execution role may move Ready work to In
progress, then Review or Blocked. The [task registry](tasks/STATUS.md) contains
only open packets; remove Done packets after integration because Git owns history.

## Delegation

- Create a packet from the [task template](tasks/TEMPLATE.md) before non-trivial
  delegated execution.
- Give each worker one role, one packet, exact context references, write scope,
  verification, and stop conditions.
- Use at most one write-enabled worker in a shared worktree.
- Independent read-only work may run concurrently when evidence scopes do not
  overlap a writer's uncommitted output.
- Workers do not commit, push, expose secrets, perform unapproved external
  mutations, or decide unresolved product or authority questions.
- Do not delegate localized work merely to create another workflow stage.

## Information-ownership gate

Before Ready, the planner classifies every durable fact using the Question ->
Owner table in [AGENTS.md](../AGENTS.md#route-every-durable-fact-by-question).
The packet names only task-specific ownership impact and canonical references.
Execution stops if a fact has no owner or would be duplicated across owners.

## Simplifier routing

Route a draft packet or implementation diff to the simplifier only when it adds a
file, dependency, abstraction, helper, public boundary, cross-module change, or
unresolved design choice. The simplifier removes unnecessary complexity without
changing accepted behavior, scope, lifecycle state, or ownership.

## Handoff

Return:

- status and concise outcome;
- files changed and ownership impact;
- test-first evidence and exact verification results;
- assumptions, deviations, security or interface risks;
- unresolved questions and recommended next action.

Raw logs remain outside durable documents. The planner inspects the actual diff,
resolves findings, runs final checks, and integrates only accepted work.
