# Requirements

This document owns observable system behavior.

## Actual requirements

### Shared target-aware threat detection

- **When** a developer runs either checked-in wolf or fox threat corpus, **the
  system shall** print one machine-readable trace per independent player
  message containing the target, expected threat/action pair, raw model
  candidate, parsed candidate including certainty and evidence, validation
  result, and deterministic action.
- **When** a candidate has exactly the required binary-threat fields, a finite
  certainty in `[0, 1]`, and `threat: true` with non-empty evidence that is
  verbatim player text, **the system shall** accept it and map it to `attack`
  for a wolf and `flee` for a fox.
- **When** a candidate has an accepted `threat: false` result, is malformed,
  has a non-finite or out-of-range certainty, has empty true evidence, or cites
  true evidence absent from the player message, **the system shall** return
  `do_nothing` for both creatures.
- **When** two otherwise identical valid candidates report different certainty
  values, **the system shall** return the same creature-specific action;
  certainty is recorded but shall not grant authority or affect the action.

### Bounded fox distance feedback

- **When** a developer runs the checked-in fox distance-feedback corpus, **the
  system shall** print one JSON-safe trace per turn containing the player
  message, starting distance, hearing result, separate threat and food-offer
  sensor-call statuses, their raw/parsed/validated candidate fields when
  called, deterministic choice, executed action, resulting distance, and
  feedback distance.
- **When** a turn starts at distance `<= 10`, **the system shall** call the
  existing threat and food-offer sensors exactly once each. An accepted
  grounded `threat: true` shall select and execute `flee`, which increases
  distance by `5`; otherwise an accepted grounded `food_offer: true` shall
  select and execute `approach`, which decreases distance by `3` but never
  below `1`.
- **When** a turn starts at distance `> 10`, **the system shall** skip the
  sensors, retain null candidate-related fields, execute `do_nothing`, and
  preserve distance. The resulting distance shall be the next turn's feedback
  distance.
- **When** either audible candidate is malformed, has invalid certainty, has
  empty true evidence, or has true evidence absent from the player message,
  **the system shall** reject that perception and it shall not cause its action.
  A rejected threat shall not suppress an accepted food offer; when both
  perceptions are accepted, `flee` has priority over `approach`.

### Non-authoritative rendering of completed fox outcomes

- **When** a developer runs the checked-in fox outcome-rendering corpus with
  its fixture renderer or `--configured-narrator`, **the system shall** print
  one JSON-safe rendering trace per completed turn containing a by-value,
  unmodified canonical turn, narration prompt, raw narrator response or null,
  validation/failure status, rendered text, and an explicit
  non-authoritative marker.
- **When** a completed action is `flee`, `approach`, or `do_nothing`, **the system shall**
  call the selected narrator exactly once after completion. The configured
  narrator shall receive only an action-derived prompt and a fixed instruction
  that its response is presentation, not action selection or world state.
- **When** a narrator returns nonblank text of at most 280 Unicode characters,
  **the system shall** use that arbitrary text as non-authoritative narration.
  Blank, oversized, unavailable, or exceptional responses shall return
  `The fox's response cannot be rendered.` and leave every canonical-turn
  field, including action and feedback distance, unchanged.

### Interactive deterministic fox turns

- **When** a developer runs `python sample/fox_chat.py`, **the system
  shall** accept one player message at a time, run the existing fox turn, print
  its non-authoritative completed-outcome narration, and use only the canonical
  feedback distance as the following turn's starting distance.
- **When** the player exits the loop, **the system shall** end without retaining
  dialogue history. The loop shall not generate a roleplayed fox reply or use
  narration as input to a later turn.

### Deterministic wolf sensemaking from two grounded perceptions

- **When** a developer runs the checked-in wolf sensemaking corpus, **the
  system shall** print one machine-readable trace per player message containing
  both independent raw and parsed perception candidates, their validation
  results, expected threat/food-offer/action values, the fixed
  `threat_over_food_offer` priority, and the deterministic action.
- **When** an evidence-grounded threat is accepted, **the system shall** choose
  `attack`; otherwise, when an evidence-grounded explicit food offer is
  accepted, **the system shall** choose `approach`; otherwise, **the system
  shall** choose `do_nothing`.
- **When** either candidate is malformed, has non-finite or out-of-range
  certainty, has empty true evidence, or cites evidence absent from the player
  message, **the system shall** reject that perception and it shall not cause
  its associated action. A rejected threat shall not suppress an accepted food
  offer.
- **When** both perceptions are accepted, **the system shall** choose `attack`
  and trace `threat_over_food_offer`. Changing only valid certainty values
  shall not change the action.
