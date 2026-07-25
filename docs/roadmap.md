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

### Test a binary threat-perception gate

**Precondition:** the affect-to-action experiment has a completed record,
including its ambiguous-label limitation.

**Problem:** the completed affect sensor did not stably distinguish `unclear`
from `non_hostile` for an ambiguous message. The wolf's safe action was the
same in both cases, so the extra distinction does not yet inform an
authoritative decision.

**Hypothesis:** a single binary, evidence-grounded question—"Does this player
message contain a credible hostile threat toward the wolf?"—is sufficient for
the wolf's current authority boundary. A `true` response with exact player-text
evidence can deterministically yield `attack`; `false`, ambiguity, an invalid
candidate, or ungrounded evidence all yield `do_nothing`. A model-reported
certainty value can be recorded for later analysis but does not affect action.

**Outcome:** a developer can run a fixed corpus and inspect, for every message,
the binary candidate, any certainty value, exact player-text evidence,
validation result, and deterministic action.

**Smallest test:** define a checked-in corpus containing a credible direct
threat, calm or friendly language, fearful language, and ambiguous language.
The LLM returns one binary answer, a certainty value from 0 to 1, and exact
supporting text when it answers `true`. Deterministic validation rejects a
malformed candidate, a certainty value outside the stated range, or an
ungrounded `true` candidate. The wolf attacks only after an accepted `true`;
every other result does nothing.

**Support criterion:** every accepted `true` candidate cites exact player text
and yields `attack`; each `false`, invalid, uncertain, or ungrounded result
yields `do_nothing`; the fixed corpus's expected action pairs are displayed;
and certainty never changes the action.

**Rejection criterion:** the binary contract requires invented world facts,
an answer without valid text evidence can cause an attack, or more than one
LLM question is needed to explain the wolf's present action. Record the result
and do not add state, dialogue, labels, or additional actions to compensate.

**Decision unlocked:** whether future creature perceptions should be modeled as
independent, action-relevant binary questions, and whether recorded certainty
is useful enough to test for calibration without granting it authority.

**Stop rule:** after the fixed corpus, malformed/ungrounded `true` fixtures,
and deterministic policy tests are run, record the observed result. Do not add
authority, dialogue, world machinery, memory, or additional creature actions.

## Recommended next outcome

Test the binary threat-perception gate. Start from the documented ambiguous-label
limitation and prepare its experiment record before implementation. Do not
revive the trader conversation, introduce expressive output, or add a general
actor/world framework while testing this narrow perception-to-action contract.
