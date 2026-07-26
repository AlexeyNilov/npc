# TASK-002: Record and derive the fox's canonical observations

**Status:** Ready

**Owner:** Technical Lead

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `d73b851`

**Depends on:** None

**Write scope:** `src/npc/experiments/fox_causal_turn.py`,
`tests/test_fox_causal_turn.py`, `scenarios/fox_causal_turn.yaml`, and
`docs/architecture.md`.

**Parallel-safe with:** `None` — this corrects the authoritative input and
trace for the open causal-turn outcome.

**Durable information changed:** How does the system work now? ->
[Architecture](../architecture.md), fox causal-turn design heading.

**Simplifier review:** Required before acceptance because this corrects the
cross-module authority boundary introduced by the causal turn.

## Outcome

The fox causal-turn trace records the accepted canonical facts that food can be
smelled nearby and leaves are rustling. The simulation core derives the exact
actor-accessible sentence from those recorded facts before the sole mediation
request, while continuing to withhold the canonical blocked-path fact.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Food-scent and rustling facts | [Requirements: Fox language-mediated causal turn](../requirements.md#fox-language-mediated-causal-turn) | Canonical scenario facts from which the simulation derives `You smell food nearby.` and `You hear leaves rustling.` | Simulation core | Initial and resulting canonical state; retained in trace | No new decision. |
| Actor-accessible substate | Same requirement; [Glossary](../glossary.md#actor-loop-terms) | Deterministic rendering of permitted canonical observations; it excludes `food_path_blocked`. | Simulation core | Per turn, retained in trace | No new decision. |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| canonical reality, actor-accessible substate | Existing [Glossary](../glossary.md) entries | Required distinction between recorded facts and the actor's permitted observation. |
| canonical food-scent/rustling fields | Fox-scenario-local code labels | Concrete names implement accepted facts only; they are not reusable world-schema terminology. |

## Experiment evidence

Not applicable. This is a delivery correction against the existing requirement.

## Vision alignment

- **Vision behavior made observable:** Every actor-visible observation in the
  slice has a recorded canonical source and a deterministic filtering path.
- **Classification:** `Disposable experiment scaffolding`
- **Reuse pressure:** Not in scope — scaffolding only.
- **Boundary rejection signal:** Any need for the actor to inspect canonical
  state directly, or for generic world-schema machinery, stops the task.

## Canonical context

- [Requirements: Fox language-mediated causal turn](../requirements.md#fox-language-mediated-causal-turn).
- [Roadmap: Establish one language-mediated causally closed actor turn](../roadmap.md#1-establish-one-language-mediated-causally-closed-actor-turn).
- [Strategy: Strategic constraints](../strategy.md#strategic-constraints).
- `src/npc/experiments/fox_causal_turn.py` and
  `tests/test_fox_causal_turn.py`.

## Task-specific scope

- Add fox-scenario-local canonical state fields for the accepted nearby food
  scent and rustling leaves, and retain them in initial and resulting trace
  state.
- Derive the existing exact actor-accessible text from canonical state rather
  than a hard-coded complete string. Keep `food_path_blocked` absent from the
  mediation input and actor-local records.
- Add focused behavioral coverage that changes either source fact and proves
  the derived observation follows it, while the blocked path remains withheld.
- Do not change the accepted scenario semantics, proposal policy, mediation
  contract, replay contract, requirements, or introduce a generic state/schema
  abstraction.

## Acceptance and verification

- A trace's initial and resulting canonical state contain the accepted scent,
  rustling, and blocked-path facts.
- Tests prove the accessible substate is deterministically derived from the
  recorded scent/rustling facts and that the blocked-path fact is not passed to
  mediation.
- The checked-in scenario still resolves the fox's `approach_food` proposal as
  `food_path_blocked`; replay remains mediation-free and reproducible.
- Write failing behavioral tests before application changes; run focused tests,
  `make check`, and `git diff --check`.

## Stop conditions

- A requested field has no source, transformation, authority, or lifecycle in
  the accepted requirement.
- The correction needs a reusable world model, new dependency, changed actor
  behavior, external mutation, or a requirements change.

## Handoff

**Status and outcome:** Ready; this reopens milestone 1 after PM review found
that the source of two actor-visible observations was absent from canonical
state.

**Changed files and ownership impact:** Packet and task registry only. The
roadmap restores its exact still-incomplete outcome.

**Verification:** PM evidence confirms the current gap; no implementation
verification applies to this planning packet.

**Assumptions, risks, and next action:** The requirement already accepts the
observation facts; this task selects only their fox-local code representation.
Assign one Implementer and obtain a fresh Simplifier review before closure.
