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
message and inspect an LLM-proposed affect perception, its exact text evidence,
validation result, and the wolf's deterministic action.

**Confirmed scope:** the first creature is a territorial wolf. It does not
understand speech or converse. It senses emotional tone only and has exactly
two authoritative actions: `attack` and `do_nothing`.

**Constraints:** no trader facts, transactions, world simulation, free-form NPC
replies, multi-intent handling, persistent memory, or additional creature
actions. The LLM proposes a sensor reading; it does not select an action or
alter state.

## Ordered future outcomes

### 1. Establish the affect-to-action boundary

**Hypothesis:** an LLM can act as a bounded affect sensor for a player message:
it proposes `hostile`, `non_hostile`, or `unclear` plus exact supporting text.
Deterministic validation and wolf policy can then make the creature's action
inspectable and replayable from that accepted perception.

**Outcome:** a developer can run a fixed corpus and inspect, for every message:
the raw model candidate, affect label, player-text evidence, validation result,
and either `attack` or `do_nothing`.

**Smallest test:** define a checked-in corpus containing hostile, calm or
friendly, fearful, and ambiguous player messages. The LLM returns one candidate
affect label and exact evidence. Deterministic code rejects malformed or
ungrounded candidates. The wolf attacks only after an accepted `hostile`
perception; it does nothing for accepted `non_hostile` or `unclear` perceptions
and for every rejected candidate.

**Support criterion:** the corpus records the expected affect/action pairs;
each accepted sensor reading cites exact player text; malformed or ungrounded
readings cannot cause an attack; and the same accepted perception always yields
the same wolf action.

**Rejection criterion:** an LLM candidate can cause an action without valid
text evidence, the action depends on invented world or trader facts, or the
experiment needs language understanding beyond affect to explain its result.
Record the result and do not add authority, conversation, or world machinery to
compensate.

**Decision unlocked:** whether the next experiment should deepen affect
perception, add a small relevant creature state, or change the perception model.

### 2. Select the next pressure on the creature model

**Precondition:** Outcome 1 has a completed experiment record, including a
negative or inconclusive result where applicable.

**Outcome:** choose one smallest question that follows from observed evidence:
whether a later reaction should use retained creature state, whether a new
affect category is useful, or whether the current sensor contract should be
revised.

**Smallest test:** state the observed limitation, one falsifiable hypothesis,
and a stop rule in a new experiment record. Do not add features simply because
the territorial wolf implementation exists.

**Pass criterion:** the next experiment addresses a documented limitation of
the affect-to-action result and retains the same deterministic authority
boundary unless new evidence justifies a change.

## Recommended next outcome

Start with **Outcome 1**. Prepare its experiment record before implementation.
Do not revive the trader conversation, introduce expressive output, or add a
general actor/world framework while testing this narrow perception-to-action
contract.
