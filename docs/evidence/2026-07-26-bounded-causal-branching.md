# Experiment: Bounded causal branching of the clearing timeline

**Status:** Complete

**Date:** 2026-07-26

**Roadmap outcome:** Completed; see the [current roadmap](../roadmap.md).

## Decision unlocked

Whether the recorded two-step composition boundary can support one explicit,
comparable alternative while preserving lineage, simulation authority,
actor-channel isolation, and independent causal replay.

## Hypothesis

The supplied clearing scenario can compare its recorded initial-source parent
with one alternative whose only source difference is
`trap_materials_ready: true -> false`, while both two-step authoritative
histories remain inspectable and replayable without actor mediation.

Assumptions: the accepted clearing meaning of trap-material readiness is
sufficient; the fixed initial source state is the sole parent point; no general
branch or temporal representation is needed.

## Observable behavior

A developer can inspect one JSON-safe comparison record containing the fixed
initial-source parent point, its declared readiness difference, and parent and
alternative two-step histories. The parent has the hunter set a trap and later
catches the fox; the alternative gives the hunter unavailable-material input,
does not set a trap, and lets the fox reach food. Each history independently
replays its simulation-owned observations and resolutions without actor
mediation.

## Design

- **Authoritative inputs and initial state:** the parent uses the supplied
  `TWO_STEP_DECLARATION` and its canonical initial state; the alternative uses
  a separate declaration with only its simulation-owned
  `trap_materials_ready` source value set to `false`.
- **Scenario timeline or action contracts:** run the existing exact-two-step
  path once for each declaration; retain both complete timelines by value.
- **Expected trace or outputs:** a clearing-local comparison record exposes the
  fixed parent point, declared source difference, and both histories; replay
  verifies each with `replay_timeline`.
- **Deliberate exclusions:** no after-step branch, scheduler, persistence,
  general branch/temporal model, generic variation API, controlled generation,
  or engine-interpreted clearing policy.
- **Candidate durable elements and disposable scaffolding:** the existing
  fixed-two-step composition boundary remains the candidate engine extension;
  the comparison record, alternative declaration, and clearing-specific
  assertions are disposable experiment scaffolding.

## Signals and stop rule

- **Support signal:** the comparison makes the parent point and sole source
  difference explicit, each timeline is independently replayable without
  mediation, readiness remains hunter-only, and lineage/variation/history
  mutations are rejected.
- **Rejection signal:** the comparison needs engine clearing interpretation,
  lets the alternative inherit or overwrite parent authority, leaks actor
  channels, or cannot replay either history independently.
- **Inconclusive condition:** two outputs exist but the record cannot expose
  provenance or demonstrate that the alternative is independently authoritative.
- **Stop rule:** stop before generalizing if the fixed source variation requires
  a scheduler, persistence, universal temporal/branch schema, or a new domain
  or authority decision.

## Result

- **Observed result:** Supported. The comparison records the fixed
  initial-source parent point, the sole `trap_materials_ready: true -> false`
  variation, and two separate two-step timelines. The parent sets a trap and
  catches the fox; the alternative shows the hunter unavailable materials,
  does not set a trap, and lets the fox reach food.
- **Reproducibility evidence:** `.venv/bin/pytest tests/test_composition.py`
  passed 11 tests. The focused tests serialize the comparison, prove that
  readiness is its only source difference, preserve hunter-only readiness and
  actor-local context, replay both histories without additional mediation, and
  reject one-field parent-point, variation, parent-history, and
  alternative-history mutations.
- **Interpretation and limits:** The fixed comparison demonstrates one
  independently authoritative initial-source alternative without changing the
  engine or establishing branch semantics. It does not establish an after-step
  branch, generic variation API, scheduler, persistence, universal temporal
  model, or clearing lifecycle policy.
- **Decision or unresolved question created:** The bounded comparison supports
  evaluating whether further causal alternatives merit design work; generic
  temporal or branch semantics remain untested.
- **Canonical follow-up:** None.
