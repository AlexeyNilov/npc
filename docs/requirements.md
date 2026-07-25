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
  message, starting distance, hearing result, sensor-call status, raw/parsed/
  validated candidate fields when called, deterministic choice, executed
  action, resulting distance, and feedback distance.
- **When** a turn starts at distance `<= 10`, **the system shall** call the
  existing threat sensor exactly once; only an accepted grounded `threat: true`
  shall select and execute `flee`, which increases distance by `5`.
- **When** a turn starts at distance `> 10`, **the system shall** skip the
  threat sensor, retain null candidate-related fields, execute `do_nothing`,
  and preserve distance. The resulting distance shall be the next turn's
  feedback distance.
- **When** an audible candidate is malformed, has invalid certainty, has empty
  true evidence, or has true evidence absent from the player message, **the
  system shall** execute `do_nothing` and preserve distance.

### Non-authoritative rendering of completed fox outcomes

- **When** a developer runs the checked-in fox outcome-rendering corpus,
  **the system shall** print one JSON-safe rendering trace per completed turn
  containing the unmodified canonical turn, rendering prompt, raw renderer
  output or null, validation result, rendered text, and an explicit
  non-authoritative marker.
- **When** a completed action is `flee` or `do_nothing`, **the system shall**
  call the renderer exactly once with only that completed action and accept
  only a JSON object with exactly `action` and `message`, matching the action
  and its exact approved sentence: `The fox flees.` or `The fox does nothing.`
- **When** renderer output is malformed, has extra fields, mismatches the
  completed action or approved message, or is unavailable, **the system
  shall** return `The fox's response cannot be rendered.` and leave every
  canonical-turn field, including action and feedback distance, unchanged.

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
