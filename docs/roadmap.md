# Roadmap

This document owns incomplete future outcomes. The Product Manager adds and
orders those outcomes; during completion reconciliation, the Technical Lead may
remove only the exact outcome verified as complete. The Technical Lead does not
add, replace, or reorder outcomes. This document orders evidence-bearing
outcomes, not coding activities or speculative engine abstractions.

## Product frame

**Target user:** the project's developer, learning how a deterministic actor
can use an LLM as a narrow perception sensor without granting it authority over
the actor's actions.

**Current learning boundary:** the verified scope is intentionally small: one
fox utility turn consumes independently validated, evidence-grounded threat and
explicit-food-offer perceptions, then deterministically scores `flee`,
`approach`, and `do_nothing` from those perceptions and authoritative hunger.
Authoritative distance gates hearing; resulting distance and hunger become the
following turn's feedback. A completed fox action can then receive one
arbitrary concise player-facing narration from the configured LLM or a
deterministic fallback; this rendering is non-authoritative. The verified scope
has no dialogue, inferred world facts, open-ended memory, certainty authority,
model-selected state transitions, registry, or actor framework.

## Ordered future outcomes

1. **Recurrence assessment for a contrasting fox decision.** Define and run
   one bounded deterministic fox decision that can test whether the supported
   perception-to-intent-to-outcome-to-feedback boundary recurs without
   introducing a reusable abstraction, another actor, or randomness. Record
   whether that evidence warrants a later reuse decision. The strategic path
   and constraints are owned by [Strategy](strategy.md#current-direction).
