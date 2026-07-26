# TASK-001: Bounded causal branching of the clearing timeline

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `02b7677fc0e312a21fba9574909f465c49e6f791`

**Depends on:** None

**Write scope:** `src/npc/experiments/composed_clearing.py`,
`tests/test_composition.py`,
`docs/evidence/2026-07-26-bounded-causal-branching.md`,
`docs/requirements.md`, and `docs/architecture.md` only.

**Parallel-safe with:** None — the task updates the shared clearing experiment
and its focused test file.

**Durable information changed:**

- observable bounded-comparison behavior ->
  [Requirements](../requirements.md#builder-controlled-clearing-composition)
- verified comparison mechanism -> [Architecture](../architecture.md#builder-controlled-clearing-composition)
- experiment result and limits ->
  `docs/evidence/2026-07-26-bounded-causal-branching.md`

**Simplifier review:** Required: the task adds a comparison record/helper to
the existing composition experiment. Review must reject any abstraction beyond
the fixed initial-source comparison.

## Outcome

A builder can inspect a parent two-step clearing timeline and one alternative
two-step timeline together. Both record their own initial source state; the
only difference is `trap_materials_ready: true -> false` before ordinal step
one. Each timeline replays independently without actor mediation. This tests
the smallest causal comparison without giving generic engine code clearing or
branch semantics.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Parent point | [Roadmap outcome](../roadmap.md#1-bounded-causal-branching-of-a-recorded-shared-world-scenario) | The recorded initial source state before ordinal step one | Recorded declaration/timeline | Fixed two-step comparison only | Not new |
| Source variation | [Roadmap outcome](../roadmap.md#1-bounded-causal-branching-of-a-recorded-shared-world-scenario); [requirement](../requirements.md#builder-controlled-clearing-composition) | `trap_materials_ready` is `true` in the parent and `false` in the alternative | Supplied clearing rules | Applied only before the alternative's ordinal step one | Not new |
| Trap-material readiness | [requirement](../requirements.md#builder-controlled-clearing-composition) | `true` permits `set_trap`; `false` does not; its observation is hunter-only | Supplied clearing rules | Canonical source input for each timeline | Not new |
| Comparison record | Roadmap observable outcome | By-value record exposing the fixed parent point, declared difference, and both independently authoritative timelines | Experiment wrapper; it does not resolve clearing state | Disposable experiment scaffolding | Not a new domain concept |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| Parent point | Packet-local, fixed initial-source position | Required only to label this bounded comparison; do not promote it to a reusable temporal term. |
| Comparison record | Packet-local disposable scaffolding | Provides inspection for this experiment only. |

## Experiment evidence

- **Evidence record:** `docs/evidence/2026-07-26-bounded-causal-branching.md`.
- **Hypothesis and decision unlocked:** the record's `Hypothesis` and
  `Decision unlocked` sections.
- **Result handoff:** At Review, complete the record, including a negative or
  inconclusive result, and set its status to `Review`. The Technical Lead
  finalizes its status during completion reconciliation.

## Vision alignment

- **Vision behavior made observable:** a builder can inspect a bounded
  alternative to a recorded shared-world scenario while keeping authoritative
  causality replayable.
- **Classification:** `Disposable experiment scaffolding`.
- **Reuse pressure:** Not in scope — this fixed clearing comparison must not
  establish a generic branch representation.
- **Boundary rejection signal:** satisfying the outcome requires engine code to
  interpret readiness, a scheduler, persistence, a universal temporal/branch
  schema, or a new clearing transition.

## Canonical context

- [Roadmap: Bounded causal branching](../roadmap.md#1-bounded-causal-branching-of-a-recorded-shared-world-scenario).
- [Requirements: Builder-controlled clearing composition](../requirements.md#builder-controlled-clearing-composition).
- [Architecture: Builder-controlled clearing composition](../architecture.md#builder-controlled-clearing-composition).
- [Stateful shared-world execution evidence](../evidence/2026-07-26-stateful-shared-world-execution.md).
- Initial source and test entry points: `src/npc/composition.py`,
  `src/npc/experiments/composed_clearing.py`, and `tests/test_composition.py`.

## Task-specific scope

- Add only a clearing-local comparison wrapper/record around two calls to the
  existing fixed-two-step execution path: the existing declaration is the
  parent; an alternative declaration changes only its initial
  `trap_materials_ready` value to `false`.
- Record both declarations/timelines by value together with an explicit,
  fixed initial-source parent-point label and the declared source difference.
- Reuse `replay_timeline` to verify each history; do not invoke mediation
  during either replay.
- Preserve hunter-only readiness observation and actor-local context. The
  alternative must show the hunter's unavailable-material input and must not
  set a trap; its second-step resolution reaches food rather than catching the
  fox.
- Do not change `src/npc/composition.py`, add a CLI, persistence, scheduling,
  controlled generation, an after-step branch, a generic variation API, or a
  reusable branch/temporal model.
- Treat the accepted uncommitted roadmap and requirements updates as input;
  do not overwrite or broaden them.

## Acceptance and verification

- Write a failing focused behavioral test before the comparison wrapper.
- The test must serialize the comparison as JSON-safe and prove: parent point
  is the initial source state; parent readiness is `true`; alternative readiness
  is `false`; only that source value differs; both histories retain two
  authoritative steps; parent catches the fox; alternative reaches food.
- The test must prove independent actor-free replay for both histories by
  checking mediation-call counts do not increase.
- Add one-field mutation tests that reject a changed parent-point label,
  declared variation, parent timeline record, or alternative timeline record.
- Add a source-variation test showing `false` changes the hunter's visible
  readiness and resulting authoritative outcome, while the fox never receives
  hunter-only readiness or actor-local context.
- Update the experiment evidence design before implementation and its result
  at Review. Update Requirements and Architecture only with accepted,
  verified behavior and mechanism; preserve their separate ownership.
- Run `.venv/bin/pytest tests/test_composition.py`, then `make check` and
  `git diff --check`.

## Stop conditions

- A fixed comparison cannot make parent point, declared difference, or each
  independent history inspectable by value.
- The only way to vary readiness bypasses `ClearingRules`, changes its accepted
  meaning, or exposes readiness to the fox.
- The work requires engine interpretation of clearing meaning, a new domain or
  authority decision, scheduler, persistence, generic branch schema, or
  source variation beyond the accepted `true -> false` change.
- Conflicting evidence, missing fixture access, or user-owned changes within
  the write scope prevent safe implementation.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
