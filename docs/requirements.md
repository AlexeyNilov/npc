# Requirements

This document owns observable system behavior.

## Actual requirements

### Bounded fox distance feedback

- **When** a caller starts a fox turn, **the system shall** accept its
  authoritative distance only as a non-boolean integer greater than or equal to
  `1`. For any other value, it shall raise `ValueError` before hearing, sensor
  invocation, action execution, or feedback processing.
- **When** a developer runs the checked-in fox distance-feedback corpus, **the
  system shall** print one JSON-safe trace per turn containing the player
  message, starting distance, hearing result, separate threat and food-offer
  sensor-call statuses, their raw/parsed/validated candidate fields when
  called, deterministic choice, executed action, resulting distance, and
  feedback distance.
- **When** a turn starts at distance `<= 10`, **the system shall** call the
  threat and food-offer sensors exactly once each. An accepted grounded
  `threat: true` shall select and execute `flee`, which increases distance by
  `5`; otherwise an accepted grounded `food_offer: true` shall select and
  execute `approach`, which decreases distance by `3` but never below `1`.
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
  validation/failure status, rendered text, and an explicit non-authoritative
  marker.
- **When** a completed action is `flee`, `approach`, or `do_nothing`, **the
  system shall** call the selected narrator exactly once after completion. The
  configured narrator shall receive an action-derived prompt; for a completed
  fox utility turn whose resulting hunger is greater than `50`, it shall also
  receive that exact `0` through `100` numeric presentation fact. Its fixed
  instruction shall require an expressive, non-authoritative food-seeking
  interpretation of supplied hunger while otherwise best-effort narrating only
  the completed action. Narration shall not select an action or change world
  state.
- **When** a narrator returns nonblank text of at most 280 Unicode characters,
  **the system shall** use that arbitrary text as non-authoritative narration.
  Blank, oversized, unavailable, or exceptional responses shall return
  `The fox's response cannot be rendered.` and leave every canonical-turn
  field, including action and feedback distance, unchanged.

### Interactive deterministic fox utility turns

- **When** a developer runs `python sample/fox_chat.py`, **the system shall**
  accept one player message at a time, run the deterministic fox utility turn,
  print its action and candidate utilities, print its completed-outcome
  narration under a label containing `Narration` and `non-authoritative`, and
  use only its canonical feedback distance and resulting hunger as the next
  turn's authoritative state. It shall accept `--starting-distance` and
  `--starting-hunger` arguments.
- **When** the player exits the loop, **the system shall** end without retaining
  dialogue history. The loop shall not generate a roleplayed fox reply or use
  narration as input to a later turn.
