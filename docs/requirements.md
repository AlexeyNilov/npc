# Requirements

This document owns observable system behavior. 

## EARS (Easy Approach to Requirements Syntax)

Use the EARS structure for precise requirements:

> **While** `<optional precondition>`, **when** `<optional trigger>`, **the system shall** `<system response>`.

This helps ensure requirements are:

* Context-aware
* Trigger-based
* Action-specific

## Actual requirements

### Trader decision experiment

- **When** a developer runs the checked-in trader experiment scenario, **the
  system shall** evaluate each proposal independently from the same explicit
  trader and player states and print the proposal, deterministic decision
  reason, and resulting states.
- **When** the trader has fewer than three healing herbs, an offer to sell one
  healing herb for at most five gold, the player has one healing herb to sell,
  and at least ten gold remains after the purchase, **the system shall** accept
  the offer, transfer one herb from the player to the trader, and transfer the
  offered gold from the trader to the player.
- **When** the offered price exceeds five gold, **the system shall** refuse the
  offer with the `price_above_limit` reason and leave both parties' states
  unchanged.
- **When** the system accepts an offer, **the system shall** conserve the total
  healing herbs and gold across the trader and player.

### Stateful conversational trader playtest

- **When** a developer runs `python -m npc.trader_playtest` with a configured
  local LLM, **the system shall** provide a terminal conversation with one
  trader for the lifetime of that process.
- **When** the developer sends a natural-language message, **the system shall**
  give the local LLM the current authoritative trader and player state plus the
  relevant in-session conversation history, and use its output only for
  narration or an untrusted structured extraction.
- **When** an LLM extraction proposes `sell_to_trader`, one `healing_herb`, and
  a positive decimal-integer `unit_price_gold`, **the system shall** evaluate
  it through the deterministic trader decision engine only if exact,
  ordered player-message evidence proves `I` before `sell` or `offer`, `you` or
  `the trader` after that action, `one`, `1`, or `a` immediately followed by
  `healing herb`, and `for <positive decimal digits> gold`.
- **When** an LLM extraction is malformed, unsupported, or lacks matching
  player-message evidence for every transaction field, **the system shall**
  leave authoritative state unchanged, return narration without a trade
  decision, and retain the conversational turn for subsequent context.
- **When** an evidence-validated trade is accepted or refused, **the system
  shall** show its untrusted extraction, deterministic reason, and
  before-and-after trader and player states in the terminal so the decision
  path can be reproduced.
- **When** a later message in the same session depends on an earlier exchange
  or trade, **the system shall** use the updated authoritative state and
  in-session history; state and history shall be discarded when the process
  exits.
