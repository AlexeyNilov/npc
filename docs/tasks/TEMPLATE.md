# TASK-NNN: Observable outcome

**Status:** Planned | Ready | In progress | Review | Blocked | Done

**Owner:** Unassigned

**Delivery role:** [Explorer](../agent_roles/explorer.md) | [Implementer](../agent_roles/implementer.md) | [Simplifier](../agent_roles/simplifier.md)

**Agent profile:** `explorer` | `implementer` | `simplifier`

**Base commit:** commit hash

**Depends on:** task IDs or `None`

**Write scope:** `Read-only` or exact files/directories

**Parallel-safe with:** `None` or task IDs with read/write justification

**Durable information changed:** `None` or question -> owner and heading

**Simplifier review:** `Not required` or routing trigger

## Outcome

State one observable result and why it matters.

## Experiment evidence

Required only for a bounded experiment.

- **Evidence record:** exact path under `docs/evidence/`.
- **Hypothesis and decision unlocked:** link or restate the record's exact
  fields.
- **Result handoff:** complete the record at Review, including a negative or
  inconclusive result.

## Vision alignment

Required only when this task introduces or claims a reusable system boundary.

- **Vision behavior made observable:**
- **Classification:** `Disposable experiment scaffolding` | `Candidate durable system foundation`
- **Reuse pressure:** the smallest second scenario or action contract that
  tests the boundary, or `Not in scope — scaffolding only`.
- **Boundary rejection signal:** evidence that stops promotion of this boundary
  as reusable.

## Canonical context

- Exact requirement and decision IDs.
- Exact architecture or roadmap headings.
- Initial source and test entry points.

Read [AGENTS.md](../../AGENTS.md), this packet, its one role guide, and only the
context named above. Do not read the task registry, sibling packets, completed
tasks, or unrelated planning history.

## Task-specific scope

- Authorized behavior and files.
- Necessary task-local assumptions.
- Explicit exclusions.

## Acceptance and verification

- Externally verifiable outcomes and relevant failure behavior.
- Regression detected by each required test.
- Failing behavioral test before behavior-changing application logic.
- Applicable contract check for documentation or configuration changes.
- Task-specific commands followed by `make check` and `git diff --check`.

## Stop conditions

- Conflicting evidence or an unaccepted design or ownership choice.
- Required scope expansion or unexpected user-owned changes.
- Missing access, dependency, fixture, or specification required for correctness.
- External mutation not explicitly authorized.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
