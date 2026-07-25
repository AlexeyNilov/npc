# Requirements

This document owns observable system behavior.

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

### Grounded primary-intent experiment

- **When** a developer submits one player message with explicit trader and
  player state, **the system shall** expose the model's raw candidate, parsed
  intent, player-text evidence, route, validation result, and authoritative
  outcome when one exists.
- **When** a candidate offer to sell one healing herb for a stated gold price
  has exact player-text evidence and the complete player message passes the
  supported offer contract, **the system shall** evaluate its deterministically
  parsed fields through the trader policy.
- **When** a candidate is malformed, unsupported, ungrounded, unclear, or
  multi-intent, **the system shall** return an unresolved result and leave
  authoritative trader and player state unchanged.
- **When** a player message is routed as expressive, **the system shall** make
  no authoritative state or durable-memory change and block a generated reply
  that contains a detected canonical fact, commitment, or completed action.
