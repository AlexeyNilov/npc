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

`AuthorityFlow` is the common authority flow: it passes the untrusted model
reply and player message to a capability dispatch, renders that capability's
`AuthorityOutcome`, records the rendered reply in history, and emits a trace
only when the outcome supplies one. `TraderCapabilityDispatch` registers two
concrete contracts. `HealingHerbPurchaseCapability` validates and evaluates the
bounded healing-herb purchase through `evaluate_offer`, and supplies its trade
trace. `TraderIdentityCapability` owns the immutable trader name and supplies
the state-preserving identity outcome. State and history are lost when the
process exits.
