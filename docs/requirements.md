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
