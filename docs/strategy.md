# Strategy

This document owns the answer to: **How do we reach the product vision
coherently?** It records the current vision-to-capability path: the product
model, strategic constraints, capability dependencies, and the few material
unknowns that could change that path.

It is not a task backlog or an implementation design. The [README](../README.md)
owns the vision, the [roadmap](roadmap.md) owns ordered incomplete next outcomes,
and [decisions](decisions.md) owns the rationale for accepted consequential
choices. Link to those owners rather than copying their contents.

## Current strategic frame

The product vision and current demonstrated boundary are defined in the
[README](../README.md). The next strategic bet is to test whether the existing
authoritative-loop pattern remains coherent when the fox must balance safety
against food-seeking, rather than follow a fixed threat-first priority.

**Recommended direction — confidence: medium.** Add a fox-local,
deterministic utility decision experiment with one persistent authoritative
need state. It should evaluate the existing validated perceptions and
authoritative state into explainable utilities for the existing candidate
actions, then preserve the closed action, outcome, and feedback boundary. This
is the smallest capability that tests an explicit intent stage and a real
conflict between motives without claiming a general actor framework.

The target user value is a clearer, evidence-led lesson for the project's
developer: whether narrow LLM perception can remain safely useful when a
deterministic actor has competing goals, not merely a fixed action priority.
The causal rationale is the verified fox boundary: perception already remains
untrusted and action/outcome authority already remains deterministic. A
persistent need is necessary for food-seeking to be a genuine motive rather
than another name for a fixed message branch.

### Capability sequence and strategic constraints

1. Define and trace one fox-local, authoritative persistent need state.
2. Define deterministic, explainable utilities for safety and food-seeking
   from that state, the current authoritative distance, and accepted
   perceptions.
3. Select and execute the existing actions deterministically, carrying the
   resulting authoritative feedback and need state into the following turn.
4. Use fixed scenarios to determine whether the trade-offs are explainable and
   replayable; only then assess whether the pattern transfers to another
   decision or actor.

The experiment must retain these cross-outcome constraints: the LLM does not
score or select actions, alter state, or determine reachability; rejected
perceptions fail closed; all policy inputs and resulting transitions are
traceable; and the work stays fox-local until contrasting evidence justifies a
general abstraction. Randomness is explicitly out of scope for this phase: it
would add behavioural variation without answering the utility-policy learning
question. The accepted rationale is in
[Decisions](decisions.md#2026-07-26-test-deterministic-utility-selection-before-behavioural-randomness).

The alternative not chosen now is to introduce randomness into action
selection. Reconsider it only after deterministic utility scenarios establish
that the policy is explainable and replayable, and there is a specific learning
question about controlled variation that deterministic selection cannot answer.

## Updating strategy

Update this document only when a strategic fact changes: a capability
dependency, a cross-outcome constraint, the target product model, a strategic
bet, or the sequence needed to reach the vision. Record the rationale for an
accepted consequential strategic choice in [decisions](decisions.md), and route
specific next outcomes to the [roadmap](roadmap.md). Do not use this document
for routine priority changes, task detail, implementation mechanism, or
experiment results.

A strategy update must state a recommended direction, its causal rationale, the
dependency-ordered capability sequence it creates, the strategic constraints it
preserves, and the evidence that would cause reconsideration. It must also name
the plausible alternative not chosen now and its trigger for reconsideration.
Do not replace these with a recap of existing documents, a generic research
sequence, or an unranked question that defers the strategic choice.
