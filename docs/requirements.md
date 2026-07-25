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
