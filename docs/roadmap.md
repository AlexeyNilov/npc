# Roadmap

This document owns incomplete future outcomes. It orders evidence-bearing
outcomes, not coding activities or speculative engine abstractions.

## Product frame

**Target user:** the project's developer, learning how a deterministic actor
can use an LLM as a narrow perception sensor without granting it authority over
the actor's actions.

**Current learning boundary:** the verified scope is intentionally small: one
fox turn consumes independently validated, evidence-grounded threat and
explicit-food-offer perceptions, then applies a fixed threat-first choice to
produce `flee`, `approach`, or `do_nothing`. Authoritative distance gates
hearing, records execution, and becomes the following turn's feedback. A
completed fox action can then receive one arbitrary concise player-facing
narration from the configured LLM or a deterministic fallback; this rendering
is non-authoritative. The verified scope has no dialogue, inferred world facts,
open-ended memory, certainty authority, model-selected state transitions,
registry, or actor framework.

## Ordered future outcomes

1. **Evidence-bearing deterministic fox utility experiment.** Demonstrate or
   refute that a fox-local persistent need state and deterministic utility
   selection can explainably balance safety against food-seeking while
   preserving the existing LLM-authority boundary and replayable feedback.
   The strategic rationale and constraints are owned by
   [Strategy](strategy.md#current-direction).
