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
receive only its approved factual player-facing sentence or a deterministic
fallback; this rendering is non-authoritative. The verified scope has no
dialogue, inferred world facts, open-ended memory, certainty authority,
model-selected state transitions, registry, or actor framework.

## Ordered future outcomes

### 1. Invoke an LLM as a non-authoritative fox outcome narrator

**Why next / evidence:** The completed rendering experiment establishes that a
presentation call can follow a completed fox turn without changing canonical
state, but it uses only fixture renderers and accepts two prewritten exact
sentences. It therefore does not yet provide the player-facing LLM narration
selected for this text-based reality.

**Target user and problem:** The project's developer needs a real, inspectable
LLM narration of a completed fox action without allowing generated prose to
become an alternate route to authority over the actor or world.

**Delivery boundary:** After a fox turn's deterministic action and feedback
distance are finalized, invoke the configured LLM once with only the completed
action information needed for narration. Store its concise player-facing text
as non-authoritative presentation data. The narrator cannot receive raw player
text, perception candidates, certainty, distance, or mutable state, and its
output is never consumed by a later turn. Unavailable or unusable narration
uses a deterministic fallback.

**Observable outcome:** A developer can run fixed fox cases with the configured
model adapter and inspect the canonical completed turn, narration prompt, raw
model response or failure, rendered player-facing text or fallback, and an
explicit non-authoritative marker. The cases include a completed `flee`, a
completed `do_nothing`, and an unavailable or unusable narrator response. The
canonical action and feedback distance are identical before and after narration.

**Decision unlocked:** Whether actual non-authoritative LLM narration is useful
enough to retain as a presentation boundary, and whether a later outcome needs
stronger factual constraints before allowing flavour beyond the completed
action.

**Constraints:** The model may narrate only after the actor loop has finalized
the event. Do not use narration as evidence, world state, action selection,
feedback, memory, dialogue history, or a player-input interpretation. Do not
introduce a generic event, dialogue, or renderer framework.

**Acceptance evidence:** A configured LLM invocation occurs exactly once after
each completed fixture turn; its response is exposed only as non-authoritative
text; and a failed or unusable invocation yields the fallback without changing
the canonical trace. Tests demonstrate that the renderer cannot access or
mutate data beyond the completed action, and a captured configured-model run
shows the live boundary.

**Stop rule:** Record fixture and configured-model evidence for completed
`flee`, completed `do_nothing`, and narrator failure, then stop. Do not add
flavour world facts, conversational replies, or stateful narration.

**Unresolved questions:** What makes a narration "unusable" while still
permitting natural language? Should a later narrator be allowed clearly
noncanonical flavour beyond a direct description of the completed action?
