# TASK-001: Demonstrate causal closure in village emergency-food rationing

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** Current working tree after the accepted village-rationing policy

**Depends on:** None

**Write scope:** `src/npc/experiments/village_rationing.py`,
`scenarios/village_rationing.yaml`, `tests/test_village_rationing.py`,
`docs/requirements.md`, `docs/architecture.md`, and
`docs/evidence/2026-07-26-village-rationing-portability.md`

**Parallel-safe with:** None — one shared worktree writer.

**Durable information changed:** Observable verified behavior ->
`docs/requirements.md`, current verified design -> `docs/architecture.md`, and
experiment result -> `docs/evidence/2026-07-26-village-rationing-portability.md`.

**Simplifier review:** Required — the experiment adds a module, corpus, tests,
and a cross-module scenario boundary.

## Outcome

Run a fixed village emergency-food rationing turn in which two household
claimants separately form claims from private views, a relief-organisation
actor proposes an allocation from the public ledger and reserve, and the
simulation core alone validates and commits the result. This tests whether the
established language-mediated causal boundary survives organisational-scale
scarcity allocation without creating a village-management system or shared
framework.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Emergency food reserve | [Accepted village-rationing policy](../decisions.md#2026-07-26-set-the-village-rationing-experiment-policy) | Initial canonical quantity is 6; controlled variation changes only it to 4. | Simulation core | Initial state, consumed by accepted allocations, recorded and replayed. | Accepted policy |
| Household claim | Same accepted policy | Each household requests 4 units; the public ledger exposes identifier, request, and priority only. | Simulation core records bounded submitted claim. | Submitted before organisation mediation; retained in trace. | Accepted policy |
| Priority allocation | Same accepted policy | Serve ascending tiers until reserve exhaustion: 6 yields 4/2 and 4 yields 4/0. | Simulation core | Validated proposal becomes committed allocation; invalid proposal changes nothing. | Accepted policy |
| Private household view | Same accepted policy | Actor-local input excluded from the other household and organisation requests and feedback. | Simulation core filtering | Mediation-only trace field; never canonical allocation authority. | Accepted policy |
| Allocation proposal | [Glossary: Action proposal](../glossary.md#action-proposal) and accepted policy | Organisation's bounded request for allocations; it is not a committed allocation. | Relief-organisation actor submits; simulation core validates. | Trace input, then accepted or rejected during resolution. | Accepted policy |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| Actor-accessible substate, epistemic profile, subjective percept, action proposal, replayable | Existing [Glossary](../glossary.md) entries | Existing causal-boundary contract. |
| Emergency food reserve, household claim, public claim ledger, priority tier, allocation | Packet-local, disposable scenario terms | Fixed experiment vocabulary; do not add glossary entries unless accepted for cross-scenario reuse. |

## Experiment evidence

- **Evidence record:** `docs/evidence/2026-07-26-village-rationing-portability.md`.
- **Hypothesis and decision unlocked:** The record tests whether natural
  language remains the default semantic interface or requires strategic
  reconsideration.
- **Result handoff:** At Review, complete the record for a supported, rejected,
  or inconclusive result and set it to `Review`; the Technical Lead finalizes
  it during completion reconciliation.

## Vision alignment

- **Vision behavior made observable:** Independently described actors interact
  through a shared authoritative simulation core while causality remains
  inspectable and replayable.
- **Classification:** Disposable experiment scaffolding.
- **Reuse pressure:** Not in scope — this is the second materially different
  scenario that tests the existing semantic contract, not a justification to
  extract a shared boundary.
- **Boundary rejection signal:** The scenario needs shared schema-specific
  sensemaking code, loses action-relevant precision, or cannot meet usable cost
  or latency.

## Canonical context

- [Village emergency-food rationing turn requirements](../requirements.md#village-emergency-food-rationing-turn).
- [Set the village-rationing experiment policy](../decisions.md#2026-07-26-set-the-village-rationing-experiment-policy).
- [Cross-scale portability roadmap outcome](../roadmap.md#1-test-cross-scale-portability-of-the-semantic-and-causal-contracts).
- [Fox and hunter shared-world turn architecture](../architecture.md#fox-and-hunter-shared-world-turn) and its source/test shape:
  `src/npc/experiments/fox_hunter_shared_world.py`,
  `tests/test_fox_hunter_shared_world.py`.

## Task-specific scope

- Add a separate village-rationing experiment module, fixture corpus, and
  behavioral tests; do not modify the fox experiment or extract common
  orchestration, actor, world, or resolver abstractions.
- Use one mediation request for each claimant and the organisation. Each
  request includes only that actor's derived substate, profile, and ordered
  questions; record percept evidence per answer.
- The corpus must contain: (1) six reserve units yielding accepted allocation
  4/2, (2) a reserve-only four-unit variation yielding 4/0, and (3) an invalid
  allocation proposal rejected with no canonical change.
- Update Requirements and Architecture only with verified behavior and current
  design; retain the scaffolding classification. Complete, but do not finalize,
  the experiment evidence at Review.
- Exclude persistent household state, eligibility/fairness policies beyond the
  accepted priority rule, unbounded claims or allocation proposals, live-model
  cost/latency measurement, and any general framework.

## Acceptance and verification

- Write failing behavioral tests before behavior-changing module logic.
- Test that each actor receives only its own allowed input and that private
  household facts never appear in the other claimant's or organisation's
  mediation request or feedback.
- Test valid six-unit allocation 4/2, reserve-only four-unit variation 4/0,
  invalid allocation rejection with unchanged canonical state, malformed or
  unsupported mediation failure for every actor, JSON-safe traces, and replay
  without mediation calls.
- Test that changing only the canonical reserve changes the organisation
  observation and authoritative result; a literal final-output assertion alone
  is insufficient.
- Run `make test`, `make check`, and `git diff --check`.

## Stop conditions

- A required fact, actor-visible field, allocation rule, threshold, or feedback
  meaning lacks accepted provenance.
- Implementing the slice requires shared schema-specific sensemaking code,
  a reusable framework, a live-model dependency, or a new village policy.
- The source-variation, non-leakage, or replay tests cannot demonstrate the
  required causal boundary.
- Unexpected user-owned changes overlap the write scope or a required external
  mutation is needed.

## Handoff

**Status and outcome:** Ready — implementation has not begun.

**Changed files and ownership impact:** This planning packet, a planned evidence
record, the task registry, and the new observable requirements section only.

**Verification:** Pending implementation; planning diff must pass Markdown-link
inspection, `make check`, and `git diff --check` before delivery begins.

**Assumptions, risks, and next action:** The accepted fixed policy is the sole
allocation policy. Assign one Implementer to this packet; obtain Simplifier
review at Review.
