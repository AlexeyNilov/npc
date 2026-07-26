# Roadmap

This document owns incomplete future outcomes. It orders evidence-bearing
outcomes, not coding activities or speculative engine abstractions.

## Product frame

**Target user:** the project's developer, learning how a deterministic actor
can use an LLM as a narrow perception sensor without granting it authority over
the actor's actions.

**Current learning boundary:** the verified scope is intentionally small:
stateless wolf and fox policies consume independently validated,
evidence-grounded threat perceptions; the wolf also combines an explicit
food-offer perception with a fixed threat-first choice to produce `attack`,
`approach`, or `do_nothing`. One fixed two-turn fox experiment applies
authoritative distance to hearing, executes `flee` as a fixed distance increase,
and feeds that distance into the following turn. A completed fox action can then
receive one arbitrary concise player-facing narration from the configured LLM
or a deterministic fallback; this rendering is non-authoritative. The verified
scope has no dialogue, inferred world facts, open-ended memory, certainty
authority, model-selected state transitions, registry, or actor framework.

## Ordered future outcomes
