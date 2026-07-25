# Roadmap

This document owns incomplete future outcomes. It orders evidence-bearing
outcomes, not coding activities or speculative engine abstractions.

## Product frame

**Target user:** the project's developer, learning how a deterministic actor
can use an LLM as a narrow perception sensor without granting it authority over
the actor's actions.

**Current learning boundary:** the verified shared threat-detection capability
is intentionally small. It accepts one evidence-grounded binary perception for
a named creature; deterministic creature-local policy maps it to wolf `attack`,
fox `flee`, or `do_nothing`. It has no state, dialogue, world model, certainty
authority, registry, or actor framework.

## Ordered future outcomes

### Test deterministic sensemaking from two grounded wolf perceptions

**Evidence:** The completed shared target-aware threat-detection delivery shows
that one evidence-grounded binary perception can be reused by two creatures
with different deterministic policies. It does not establish whether one actor
can combine independent validated perceptions into an explainable choice, so
the current implementation still bypasses the intended sensemaking and intent
parts of the target actor loop. See [shared threat-detection evidence](evidence/2026-07-25-shared-threat-detection.md).

**Target user and problem:** The project's developer needs to learn whether a
small deterministic seam for combining multiple perception facts is warranted,
without prematurely creating a general actor framework.

**Desired observable outcome:** For one wolf player-message turn, a trace shows
two separate untrusted, evidence-grounded binary perceptions: whether the
message credibly threatens the wolf, and whether it explicitly offers food to
the wolf. Deterministic policy selects `attack` for an accepted threat,
`approach` for an accepted food offer, and `do_nothing` otherwise. If both are
accepted, the trace shows the documented threat-priority choice of `attack`.
Malformed, invalid, or ungrounded candidates cannot cause an action.

**Decision unlocked:** Whether two independent validated perception results can
be combined by an explicit deterministic priority policy without a general
actor framework, and whether that policy boundary should become a candidate
durable sensemaking/intent seam.

**Constraints:** Keep the LLM limited to one binary, player-text-grounded fact
per sensor; retain deterministic action authority and exact-evidence
validation; use no world facts, dialogue, persistent state, registry, or
certainty-based authority. The food-offer behavior is a bounded experimental
assumption, not a general wolf model.

**Support signals:** Every action is attributable solely to accepted evidence
and the documented fixed priority; independent threat-only, offer-only,
neither, and both cases have inspectable traces; malformed and ungrounded
candidates yield `do_nothing`; and changing certainty alone changes no action.

**Rejection signals:** The scenario needs inferred world facts, LLM-selected
actions, ambiguous conflict resolution, or a general actor framework to remain
understandable and safe.

**Stop rule:** Complete a bounded corpus and deterministic fixtures covering
each individual fact, their conflict, malformed and ungrounded candidates, and
certainty invariance. Record the result in experiment evidence. Do not add
memory, dialogue, outcome handling, or broader world machinery to compensate.
