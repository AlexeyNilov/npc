# Roadmap

This document owns incomplete future outcomes. It orders evidence-bearing
outcomes, not coding activities or speculative engine abstractions.

## Product frame

**Target user:** the project's developer, learning how a deterministic actor
can use an LLM as a narrow perception sensor without granting it authority over
the actor's actions.

**Problem:** the trader experiment combines language interpretation,
authoritative facts, commitments, and free expressive dialogue. That is too
much uncertainty for the current learning step. The project needs a smaller
language-facing actor whose behavior can be inspected without a world model or
generated dialogue.

**Evidence milestone:** a developer can give a territorial wolf one player
message and inspect an LLM-proposed binary threat perception, its certainty and
exact text evidence, validation result, and the wolf's deterministic action.

**Confirmed scope:** the first creature is a territorial wolf. It does not
understand speech or converse. It answers one grounded binary threat question
and has exactly two authoritative actions: `attack` and `do_nothing`.

**Constraints:** no trader facts, transactions, world simulation, free-form NPC
replies, multi-intent handling, persistent memory, or additional creature
actions. The LLM proposes a sensor reading; it does not select an action or
alter state.

## Ordered future outcomes

### Reuse threat detection for a fleeing fox

**Problem:** the completed binary threat gate is implemented for the wolf only.
The project needs the same bounded perception capability available to a fox
without coupling it to the wolf's `attack` policy.

**Delivery outcome:** a reusable, target-aware threat-detection skill supplies
the same grounded binary perception to both creatures. It remains an untrusted
perception source; it does not select either creature's action.

**Observable behavior:** a developer can run a fixed threat corpus for both a
territorial wolf and a fox, inspect the common candidate, certainty, evidence,
validation result, and each creature's distinct deterministic action.

**Smallest delivery slice:** extract the completed binary threat contract into one
target-aware skill that asks whether a player message contains a credible
hostile threat toward the named creature. Run the existing wolf cases and a
checked-in fox corpus containing direct-threat, calm or friendly, fearful, and
ambiguous messages. The wolf attacks only after an accepted `true`; the fox
flees only after an accepted `true`; every `false` or rejected candidate yields
`do_nothing` for both creatures. Certainty remains trace-only.

**Acceptance criteria:** both creatures use the same candidate shape, grounding
rules, and validation result; the same accepted threat perception deterministically
maps to `attack` for the wolf and `flee` for the fox; no invalid or ungrounded
candidate can cause either action; and certainty does not alter either policy.

**Constraints:** do not add creature-specific LLM output fields or validation,
let an LLM response select an action, or build a general registry/framework
merely to support these two creatures.

**Completion evidence:** record the executed corpus traces and deterministic
policy tests. Update the architecture if the shared capability becomes current
verified design; record an architectural decision only if a broader capability
structure is accepted.

**Boundary:** stop after both fixed corpora, malformed/ungrounded `true`
fixtures, and the two deterministic policy tests. Do not add memory, dialogue,
world simulation, certainty-based authority, or a general skill registry.

## Recommended next outcome

Reuse threat detection for a fleeing fox.
