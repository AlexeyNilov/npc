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

## Concept provenance

Required when the task adds or changes a domain label, predicate, state field,
event, transition, threshold, or other semantic information. Otherwise state
`Not applicable`.

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Every concept must trace to accepted canonical context. A convenient label does
not establish a new fact: if its source, transformation, authority, or lifecycle
is missing, omit it or mark the packet Blocked and route the data-meaning
decision to the Product Manager.

## Terminology

Required when the task introduces, changes, or reuses an ambiguous
project-specific term across a code or documentation boundary. Otherwise state
`Not applicable`.

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| | | |

Use the [glossary](../glossary.md) preferred name for shared terms. If a new
term needs one stable meaning across packets or durable documents, include the
glossary in write scope and add its entry after the underlying meaning is
accepted. Do not add disposable experiment names merely because they appear in
a packet.

## Experiment evidence

Required only for a bounded experiment.

- **Evidence record:** exact path under `docs/evidence/`.
- **Hypothesis and decision unlocked:** link or restate the record's exact
  fields.
- **Result handoff:** complete the record at Review, including a negative or
  inconclusive result, and set its evidence status to `Review`. The Technical
  Lead finalizes the evidence status during completion reconciliation.

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
