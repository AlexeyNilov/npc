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

## Next decision

The binary threat gate is complete. Decide whether observed product behavior
warrants a second independent, action-relevant binary perception question or a
separate experiment on certainty calibration. Do not select an experiment until
the developer identifies the limitation or decision it must address.
