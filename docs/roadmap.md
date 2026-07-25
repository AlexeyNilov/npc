# Roadmap

This document owns incomplete future outcomes.

## Product frame

**Target user:** the project's developer, initially playing with a D&D/RPG
trader through a simple chat interface.

**Problem:** the current playtest has a safe, deterministic authority boundary,
but it does not yet demonstrate a reusable actor model or engaging,
state-grounded social interaction.

**Desired outcome:** a developer can run repeatable sessions with an autonomous
actor whose state, goals, relevant history, and choices visibly affect its
conversation and actions.

**Constraints:** authoritative decisions and state changes remain deterministic;
LLMs may assist but cannot authoritatively change state or choose the final
action.

## Ordered future outcomes

### 1. Test a minimal reusable actor-loop model

**Outcome:** make reality, perception, sensemaking, intent, action, outcome,
and feedback explicit in a small model that is independent of terminal chat
and one trader's actions.

**Smallest test:** run two bounded scenarios with different action contracts
through the same loop and retain an inspectable record from perception through
feedback.

**Pass criterion:** both authoritative state transitions are reproducible, and
adding the second scenario does not require trader-specific branches in the
shared loop.

### 2. Re-run the bounded trader playtest

**Outcome:** conduct a repeatable chat session where the trader gives distinct,
correct responses to basic social questions while its trade and visible state
remain consistent.

**Smallest test:** run and repeat a scripted greeting, name or fact question,
accepted offer, follow-up refusal, and unsupported demand.

**Pass criterion:** social responses are meaningfully distinct; no
player-visible claim conflicts with state or trace; no unsolicited trade occurs;
and both runs have the same authoritative state transitions.

### 3. Select the next actor experiment from play evidence

**Outcome:** decide whether to deepen the actor loop, repeat the trader
experiment with a changed hypothesis, or explore a second actor scale.

**Smallest test:** review the recorded play sessions against Outcomes 1 and 2,
then state the observed limitation and one minimal experiment.

**Pass criterion:** the next experiment has evidence, a falsifiable success
signal, and no scope expansion justified only by prior effort.

### 4. Evaluate LangExtract for grounded trade extraction

**Outcome:** determine whether LangExtract improves varied trade extraction
without weakening the authority boundary.

**Smallest test:** compare it with the current extractor on a fixed corpus;
pass only normalized candidates through the existing deterministic validator.

**Pass criterion:** it recognizes at least the baseline's valid offers,
introduces no accepted non-offer, and supports every accepted field with a
valid source span. Otherwise retain the current extractor.

## Recommended next outcome

Start with **Outcome 1**. Do not extend trader-specific dialogue until the
actor-loop experiment either demonstrates a reusable boundary or establishes
that a narrower trader-only learning goal is the deliberate choice.
