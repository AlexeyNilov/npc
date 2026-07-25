# Architecture

This document owns the current verified system design.

## System context

## Conversational trader playtest

`python -m npc.trader_playtest` runs one terminal-only process with in-memory
`TraderSession` state and conversation history. For each player message, the
session supplies the authoritative trader/player states and previous turns to
`LocalTraderModel`. That boundary uses the configured local LLM transport and
returns narration plus an untrusted JSON candidate. The transport disables the
model's optional thinking mode so a concise playtest response does not generate
an unbounded hidden rationale first.

Only a candidate for one `healing_herb` and an integer `unit_price_gold` becomes
an `Offer`. `evaluate_offer` remains the authority for acceptance, refusal, and
the next state; malformed or unsupported candidates produce narration only.
History retains each valid candidate's deterministic reason alongside its
narration, so later turns receive the authoritative outcome rather than relying
on model wording.
For every valid candidate, the terminal prints a `TRADE_TRACE` JSON record with
the candidate, engine reason, and pre/post states. State and history are lost
when the process exits.
