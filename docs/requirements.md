# Requirements

This document owns observable system behavior.

## Actual requirements

### Fox language-mediated causal turn

- **When** a developer runs the checked-in fox causal-turn scenario, **the
  system shall** start its authoritative simulation core from canonical state
  in which the fox is in a clearing, food can be smelled nearby, leaves are
  rustling, and the path to the food is blocked. The simulation core alone
  owns these facts; the blocked path is not actor-accessible before resolution.
- **When** that turn begins, **the system shall** deterministically derive the
  fox's actor-accessible substate before mediation as: `You are in a clearing.
  You smell food nearby. You hear leaves rustling.` It shall provide no
  canonical field or generated text that reveals whether the path to the food
  is blocked.
- **When** the fox forms its subjective percept, **the system shall** supply
  the fox-owned epistemic profile: `You are hungry and cautious. You cannot
  see beyond the clearing or through obstacles. Treat smells and sounds as
  clues, not facts.` The sole mediation request shall use only that profile,
  the actor-accessible substate, and these ordered fox-owned binary questions:
  `Do I believe an immediate threat is present?` followed by `Do I believe the
  food is reachable by approaching?` The request shall record one subjective
  percept and retain each answer with its own supporting reference to content
  in that percept.
- **When** valid answers say that the fox does not believe an immediate threat
  is present and does believe the food is reachable, **the system shall** have
  the fox submit the bounded proposal `approach_food`. The fox shall otherwise
  submit `wait`. A malformed percept or answer, missing or invalid percept
  evidence, or any proposal outside `approach_food` and `wait` shall fail
  closed as `wait`; it shall not directly change canonical state.
- **When** the simulation core resolves `approach_food` against this
  scenario's blocked canonical path, **the system shall** commit the
  authoritative outcome `food_path_blocked`, leave the fox in the clearing,
  and return the feedback `The path to the food is blocked.` The model's belief
  that food appeared reachable shall remain actor-local and shall not override
  the blocked-path fact. Resolving `wait` shall leave the fox in the clearing
  and return feedback that it waited.
- **When** a causal turn completes, **the system shall** retain a JSON-safe
  trace containing the initial canonical state, actor-accessible substate,
  epistemic profile, subjective percept, ordered questions, answers and
  percept evidence, submitted proposal, authoritative resolution, resulting
  canonical state, and feedback. Replaying that trace shall reproduce the
  committed canonical outcome without making another mediation request.

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

### Deterministic fox utility turns

- **When** a caller starts a deterministic fox utility turn, **the system
  shall** accept hunger only as a non-boolean integer from `0` through `100`.
  For any other value, it shall raise `ValueError` before hearing or sensor
  invocation.
- **When** the fox hears a player message, **the system shall** derive
  candidate utilities only from accepted threat and food-offer perceptions and
  authoritative starting hunger: `flee` scores `60` for an accepted threat,
  `approach` scores starting hunger for an accepted food offer, and
  `do_nothing` scores `1`. It shall select the highest score, resolving equal
  scores in the order `flee`, `approach`, then `do_nothing`.
- **When** the utility turn completes, **the system shall** apply the selected
  action's existing distance transition, increase hunger by `10` without
  exceeding `100`, and retain the resulting distance and hunger as feedback.
  Its trace shall retain the authoritative starting and resulting hunger,
  accepted-perception results, candidate utilities, selected score, tie order,
  action, and distance feedback.

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
