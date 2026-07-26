# Strategy

This document owns the answer to: **How do we reach the product vision
coherently?** It records the current vision-to-capability path: the product
model, strategic constraints, capability dependencies, and the few material
unknowns that could change that path.

It is not a task backlog or an implementation design. The [README](../README.md)
owns the vision, the [roadmap](roadmap.md) owns ordered incomplete next outcomes,
and [decisions](decisions.md) owns the rationale for accepted consequential
choices. Link to those owners rather than copying their contents.

## Current direction

**Decision:** Establish whether deterministic policy can balance competing fox
motives before testing behavioural randomness or portability to another actor.
**Confidence:** Medium.

This tests whether the existing authoritative-loop boundary remains useful when
the actor has a genuine safety-versus-food trade-off, rather than a fixed
threat-first priority. The accepted rationale is in
[Decisions](decisions.md#2026-07-26-test-deterministic-utility-selection-before-behavioural-randomness).

## Capability path

| Order | Outcome | Establishes / unlocks |
| --- | --- | --- |
| 1 | [Deterministic fox utility experiment](roadmap.md#ordered-future-outcomes) | Whether a fox-local authoritative policy can make explainable, replayable competing-motive choices. |
| 2 | Recurrence assessment | Which elements of the perception-to-feedback loop survive a contrasting decision. |
| 3 | Reuse decision | Whether the recurring elements warrant a small reusable loop boundary. |
| 4 | Portability test | Whether the evidenced boundary transfers to another decision or actor. |

## Strategic constraints

- The LLM may not score or select actions, alter authoritative state, or
  determine reachability.
- Rejected perceptions fail closed.
- Policy inputs, selection, and transitions remain explainable and replayable.
- Work remains fox-local until contrasting evidence justifies a broader
  boundary.
- Randomness is out of scope for the current direction.

## Reconsideration

| Alternative not chosen now | Reconsider when |
| --- | --- |
| Random action selection | Deterministic scenarios are explainable and replayable, and a defined learning question requires controlled variation. |
| A different actor or system | The recurrence assessment identifies a candidate boundary whose portability is the next material uncertainty. |
