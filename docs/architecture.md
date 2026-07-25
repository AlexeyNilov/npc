# Architecture

This document owns the current verified system design.

## System context

## Conversational trader playtest

`python -m npc.trader_playtest` runs one terminal-only process with in-memory
`TraderSession` state and conversation history. For each player message, the
session supplies the authoritative trader/player states and previous turns to
`LocalTraderModel`. That boundary uses the configured local LLM transport and
returns one closed flavor value plus an untrusted JSON candidate. Unknown,
malformed, and omitted flavor becomes `neutral`; model-authored free text is
discarded. The transport disables the model's optional thinking mode so a
concise playtest response does not generate an unbounded hidden rationale first.

## Deterministic actor-loop experiment

`ActorLoop` is a terminal-independent sequencing boundary. It accepts reality,
the untrusted model output, and a scenario-owned contract; returns the next
reality; and records reality, perception, sensemaking, intent, action, outcome,
and feedback. It has no trader-, item-, gold-, identity-, or terminal-specific
branches.

`TraderSession` adapts its authoritative states and player message into
`TraderReality`, then uses `AuthorityFlow` as the trader contract for the
loop. The flow normalizes closed model flavor and deterministically validates
the candidate against the player message before it becomes recorded perception.
Its intent is always `resolve_validated_perception`; its action is the matching
deterministic capability resolution, so model output cannot authoritatively
select an intent, action, state change, or final choice.

`TraderCapabilityDispatch` registers two concrete contracts.
`HealingHerbPurchaseCapability` evaluates the bounded, validated healing-herb
purchase through `evaluate_offer`; `TraderIdentityCapability` owns the
immutable trader name and supplies the validated, state-preserving identity
outcome. Each contract returns its deterministic states in `AuthorityOutcome`;
the session applies those states, records the rendered reply in history, and
emits a trace only when the outcome supplies one. State and history are lost
when the process exits.
