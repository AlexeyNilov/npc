# Experiment: bounded fox distance-feedback loop

**Status:** Planned

**Date:** 2026-07-25

**Roadmap outcome:** [Demonstrate a bounded fox distance-feedback loop](../roadmap.md#1-demonstrate-a-bounded-fox-distance-feedback-loop).

## Decision unlocked

Whether an authoritative distance, deterministic hearing gate, and fixed
`flee` displacement form a legible outcome/feedback boundary before a
contrasting movement action is explored.

## Hypothesis

In a fixed two-turn fox scenario, a deterministic hearing check can gate the
existing untrusted threat sensor, and an accepted threat can deterministically
increase authoritative distance so that the recorded outcome prevents the same
message reaching perception on the next turn.

Assumptions: distance uses disposable integer units; a message is audible when
distance is at most 10; and `flee` increases distance by 5. The model receives
only an audible player message and target, and has no authority over distance,
hearing, action selection, or execution.

## Observable behavior

A developer can run checked-in fixtures and inspect each fox turn's player
message, starting distance, hearing result, threat-sensor call status,
raw/parsed/validated candidate when called, deterministic choice, executed
action, resulting distance, and feedback distance.

- **Goal:** demonstrate one authoritative world fact constraining perception
  and changing through a deterministic fox action.
- **Perception:** the existing grounded threat sensor, called only after the
  deterministic hearing check passes.
- **Intent or choice:** accepted threat selects `flee`; all other turns select
  `do_nothing`.
- **Action:** execute only `flee`; `do_nothing` leaves distance unchanged.
- **Outcome:** `flee` adds 5 distance units.
- **Feedback or retained history:** resulting distance is the following turn's
  starting distance.
- **Later decision affected:** whether this bounded boundary is understandable
  without a general actor or world framework.

## Design

- **Authoritative inputs and initial state:** fixed scenario distance, hearing
  range 10, flee displacement 5, and player messages. Model candidates are
  untrusted.
- **Scenario timeline or action contracts:** an in-range direct threat at 10
  produces `flee` and distance 15; its repeated message is then inaudible and
  makes no sensor call. Separate fixtures cover an in-range rejected candidate
  and an initially inaudible threat.
- **Expected trace or outputs:** one JSON-safe trace per turn with the named
  observable fields, including null candidate-related fields when no sensor is
  called.
- **Deliberate exclusions:** dialogue, inferred world facts, open-ended memory,
  certainty thresholds, model-selected state transitions, wolf approach,
  registry, generic actor loop, and generic movement/world framework.
- **Candidate durable elements and disposable scaffolding:** the narrow
  distance -> hearing -> threat perception -> fox policy -> distance feedback
  sequence is under test; its wrapper, corpus, and trace types are disposable
  experiment scaffolding.

## Signals and stop rule

- **Support signal:** fixtures expose `10 -> 15`, gate the repeated threat
  before any second sensor call, and show rejected or initially inaudible turns
  leave distance unchanged.
- **Rejection signal:** a clear trace requires the model to decide reachability
  or state change, inferred world facts, or a generic actor/world abstraction.
- **Inconclusive condition:** the corpus cannot distinguish a skipped sensor
  call from a rejected candidate, or cannot carry a resulting distance into the
  next turn.
- **Stop rule:** record the fixed valid, rejected-perception, and initially
  out-of-range fixtures, then stop. Do not add a second creature, movement
  action, dialogue, memory, or reusable framework.

## Result

Complete at Review.

- **Observed result:**
- **Reproducibility evidence:**
- **Interpretation and limits:**
- **Decision or unresolved question created:**
- **Canonical follow-up:**
