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
  initial trader state and print the proposal, deterministic decision reason,
  and resulting trader state.
- **When** the trader has fewer than three healing herbs, an offer to sell one
  healing herb for at most five gold, and at least ten gold remains after the
  purchase, **the system shall** accept the offer and add one herb to its
  inventory while subtracting the offered gold from its funds.
- **When** the offered price exceeds five gold, **the system shall** refuse the
  offer with the `price_above_limit` reason and leave the trader state
  unchanged.
