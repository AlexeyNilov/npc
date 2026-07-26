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

**Decision:** Assess whether the supported deterministic utility loop recurs
under a contrasting fox decision before considering reuse, behavioural
randomness, or portability to another actor.
**Confidence:** Medium.

The completed utility experiment supports the authoritative loop for a genuine
safety-versus-food trade-off rather than only a fixed threat-first priority.
The next assessment determines whether its candidate durable boundary recurs,
as recorded in [the experiment evidence](evidence/2026-07-26-fox-deterministic-utility.md).
The accepted utility rationale is in
[Decisions](decisions.md#2026-07-26-test-deterministic-utility-selection-before-behavioural-randomness).

## Capability path

| Order | Outcome | Establishes / unlocks |
| --- | --- | --- |
| 1 | [Recurrence assessment](roadmap.md#ordered-future-outcomes) | Which elements of the perception-to-feedback loop survive a contrasting decision. |
| 2 | Reuse decision | Whether the recurring elements warrant a small reusable loop boundary. |
| 3 | Portability test | Whether the evidenced boundary transfers to another decision or actor. |

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
