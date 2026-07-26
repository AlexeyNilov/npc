# Experiment: Stateful shared-world execution

**Status:** Complete

**Date:** 2026-07-26

**Roadmap outcome:** Completed; see the [current roadmap](../roadmap.md).

## Decision unlocked

Whether a recorded two-step causal history is stable enough to support causal
branching, or whether time, ordering, conflict resolution, feedback, or
retained context require a strategic revision first.

## Hypothesis

An already composed clearing scenario can advance through exactly two committed
authoritative steps while preserving component ownership, actor-channel
isolation, and actor-free causal replay.

Assumptions: the completed composition declaration and clearing components are
the starting boundary; the supplied clearing rules can author the limited
second-step continuation without generic engine policy.

## Observable behavior

A developer can run a builder declaration for exactly two ordinal steps and
inspect one JSON-safe timeline.  Each record shows the source state,
simulation-filtered input, actor-owned retained context, bounded proposal,
simulation-declared resolution order and decisions, canonical transitions,
actor-specific feedback, and resulting state.  The second step starts from the
first step's resulting state.  The supplied actors receive only their own
input, context, and feedback; the simulation alone resolves and commits both
steps.  Replay reproduces the timeline without mediation and rejects a changed
recorded state, context, input, proposal, decision, transition, feedback, or
result.

## Design

- **Authoritative inputs and initial state:** An existing
  `CompositionDeclaration`, its selected simulation, actor membership and
  proposal pairings, and the declaration's initial canonical clearing state.
- **Scenario timeline or action contracts:** The engine runs exactly two
  sequential steps.  Before each step it asks the simulation to derive each
  actor's current input, then invokes each actor with only that input and the
  actor's retained context.  The simulation resolves the collected proposals
  under its supplied order and conflict rule, commits state, and selects
  feedback.  Each actor's supplied deterministic context reducer receives only
  its prior context and own feedback to produce the next context.  The supplied
  clearing fixture has the hunter set the trap while the fox waits in step one;
  in step two the fox's retained context and the committed trap state lead to
  an approach that is caught.
- **Expected trace or outputs:** A frozen timeline with ordinals one and two,
  per-step source and resulting state, actor records, resolution, feedback, and
  the retained contexts used at each exchange.  Replay re-derives simulation
  inputs and resolutions and re-applies actor-supplied deterministic context
  reduction; it does not invoke mediation.
- **Deliberate exclusions:** No unbounded loop, scheduler, persistence layer,
  universal clock, conflict representation, branch model, domain schema, or
  engine-interpreted clearing policy.
- **Candidate durable elements and disposable scaffolding:** The minimal
  fixed-two-step composition contract is a candidate durable engine extension;
  the clearing continuation, actors, fixture behavior, and corpus remain
  disposable experiment scaffolding.

## Signals and stop rule

- **Support signal:** The two-step fixture produces the expected distinct
  committed outcomes, stays JSON-safe, preserves actor isolation, and rejects
  every required one-field trace mutation without further mediation.
- **Rejection signal:** Completing the slice requires engine code to interpret
  clearing fields or proposal meaning, leaks another actor's channel, cannot
  replay a changed-state second step, or needs a general scheduling or branch
  abstraction.
- **Inconclusive condition:** The bounded fixture works but cannot establish
  whether the added temporal contract remains component-owned and replayable.
- **Stop rule:** Stop before implementation if a required context lifecycle,
  ordering rule, conflict rule, or public contract cannot be supplied by the
  selected actors or simulation without a new product or authority decision.

## Result

- **Observed result:** Supported. The supplied clearing declaration completed
  two recorded steps: the hunter set the trap while the fox waited, then the
  fox approached and was caught from the committed trap state.
- **Reproducibility evidence:** `.venv/bin/pytest tests/test_composition.py`
  passed 8 tests. The focused tests serialize the timeline, verify actor-free
  replay, verify state-derived changed input/outcome, ensure each step derives
  every observation before mediation, and reject the required one-field trace
  mutations.
- **Interpretation and limits:** The bounded contract preserves state,
  actor-specific context, resolution records, and replay across one committed
  change. It does not establish an unbounded scheduler, persistence, branch
  model, universal clock, conflict representation, or clearing lifecycle.
- **Decision or unresolved question created:** The result supports Product
  Strategy's evaluation of causal branching; general temporal semantics remain
  untested.
- **Canonical follow-up:** [Strategy: Current focus](../strategy.md#current-focus).
