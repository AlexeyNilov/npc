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
and feeds that distance into the following turn. It has no dialogue, inferred
world facts, open-ended memory, certainty authority, model-selected state
transitions, registry, or actor framework.

## Ordered future outcomes

### 1. Render a completed fox outcome as a player-facing text message

**Why next / dependency:** The distance-feedback milestone establishes the
authoritative event that occurred: whether the fox fled and its resulting
distance. In a text-message reality, the player also needs a textual outcome.
This follow-up tests an LLM as a bounded renderer after—not participant in—the
authoritative actor loop.

**Target user and problem:** The project's developer needs to see whether the
same deterministic fox outcome can be presented as useful player-facing text
without allowing narrative generation to choose an action, change distance, or
create canonical world facts.

**Delivery boundary:** After a completed fox turn, pass the LLM only the
authoritative, completed event needed to describe it (for example, `flee` or
`do_nothing` and the applicable observable context). Ask it for one concise
message describing what the fox does in response to the player. Store the
result as a non-authoritative rendering. The deterministic outcome and feedback
state are finalized before this call and cannot be modified by its text.

**Observable outcome:** A developer can run fixed fox turn fixtures and inspect
the canonical perception, choice, action, and distance outcome alongside the
rendering prompt and returned player-facing message. The fixtures cover an
accepted in-range threat that causes `flee`, an in-range non-action, an
out-of-range message, and malformed renderer output or renderer failure. Each
case retains the same authoritative trace and feedback state regardless of the
rendered text; a renderer failure returns a deterministic bounded fallback
message.

**Decision unlocked:** Whether non-authoritative LLM outcome rendering is a
useful durable presentation boundary, and what factual constraints or fallback
are required before the text can be exposed to a player.

**Constraints:** The renderer receives completed canonical event data, never
raw authority to alter it. Its text must not be treated as evidence of a world
fact, a commitment, a new action, or feedback for a later turn. Do not add
dialogue history, player intent extraction, generated state changes, or
multi-turn conversation.

**Acceptance evidence:** An identical completed event yields the same
authoritative state regardless of renderer output; only a completed `flee` is
presented as a fleeing response; and malformed or unavailable renderer output
cannot prevent, change, or invent an authoritative outcome. The trace makes the
boundary between canonical event and non-authoritative text explicit.

**Stop rule:** Record fixture-backed rendering behavior and failure handling,
then stop. Do not use the generated text as input to perception or state, and do
not broaden it into a general dialogue system.

**Unresolved questions:** Should player-facing text be constrained to a small
set of observable event facts, or may it include clearly noncanonical flavour?
What deterministic fallback wording is adequate when rendering fails?
