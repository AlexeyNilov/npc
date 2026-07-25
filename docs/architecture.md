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

The model response may contain an untrusted extraction for only
`sell_to_trader`, one `healing_herb`, and a positive integer gold price. Before
constructing an `Offer`, `offer_from_candidate` requires the extraction's exact
player-message evidence to prove, in order, the seller/action/recipient,
quantity and canonical item, and `for <price> gold`. It rejects malformed,
invented, mismatched, zero, or negative values. `evaluate_offer` remains the
authority for acceptance, refusal, and the next state.

`compose_reply` is the sole player-visible response boundary. It maps flavor to
a fixed non-economic atmospheric clause, renders no extraction as that clause
alone, and renders rejected extraction, refusal, or acceptance only from the
validation result and evaluator result. History retains that rendered reply, not
model prose. Only evidence-validated offers emit a `TRADE_TRACE` JSON record
with the untrusted extraction, engine reason, and pre/post states. State and
history are lost when the process exits.
