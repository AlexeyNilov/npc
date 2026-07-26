# Strategy

This document owns the answer to: **How do we reach the product vision
coherently?** It records the current vision-to-capability path: the product
model, strategic constraints, capability dependencies, and the few material
unknowns that could change that path.

It is not a task backlog or an implementation design. The [README](../README.md)
owns the vision, the [roadmap](roadmap.md) owns ordered incomplete next outcomes,
and [decisions](decisions.md) owns the rationale for accepted consequential
choices. Link to those owners rather than copying their contents.

## Strategic thesis

**Long-term capability:** A deterministic actor loop whose reusable elements
are evidenced across contrasting decisions before it is extended to other actor
types or scales.
**Confidence:** Medium.

The strategic proposition is that the project reaches its vision by proving
which authority-preserving loop elements recur, rather than by generalizing a
single successful fox scenario. This connects the current bounded fox work to
the README's longer-term actor model without claiming that its implementation
is already reusable.

## Strategic horizons

| Horizon | Capability established | Unlocks |
| --- | --- | --- |
| 1. Contrasting decisions | An authority-preserving loop survives more than one qualitatively different decision. | Assessment of which loop elements genuinely recur. |
| 2. Evidenced boundary | Recurring elements are separated from fox-local experiment scaffolding. | A bounded reuse decision. |
| 3. Portability | The evidenced boundary survives a different actor or system context. | Deliberate extension toward the broader actor model. |

## Current focus

**Strategic bet:** Assess whether the supported deterministic utility loop
recurs under a contrasting fox decision before considering reuse, behavioural
randomness, or portability to another actor.

This is Horizon 1's active evidence-bearing outcome. The completed utility
experiment supports the authoritative loop for a genuine safety-versus-food
trade-off rather than only a fixed threat-first priority. The next assessment
determines whether its candidate durable boundary recurs, as recorded in
[the experiment evidence](evidence/2026-07-26-fox-deterministic-utility.md).
The accepted utility rationale is in
[Decisions](decisions.md#2026-07-26-test-deterministic-utility-selection-before-behavioural-randomness).

The active outcome is the [recurrence assessment](roadmap.md#ordered-future-outcomes).
It is not the strategy itself: its role is to supply evidence for the first
strategic horizon.

## Strategic constraints

- The LLM may not score or select actions, alter authoritative state, or
  determine reachability.
- Rejected perceptions fail closed.
- Policy inputs, selection, and transitions remain explainable and replayable.
- Work remains fox-local until contrasting evidence justifies a broader
  boundary.
- Randomness is out of scope for the current focus.

## Reconsideration

| Alternative not chosen now | Reconsider when |
| --- | --- |
| Random action selection | Deterministic scenarios are explainable and replayable, and a defined learning question requires controlled variation. |
| A different actor or system | The recurrence assessment identifies a candidate boundary whose portability is the next material uncertainty. |
