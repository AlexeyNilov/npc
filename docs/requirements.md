# Requirements

This document owns observable system behavior.

## Actual requirements

### Autonomous observer clearing session

- **When** an observer launches the supplied autonomous clearing session from
  its normal terminal entry point, **the system shall** present the premise
  that a fox is looking for food while a hunter may prepare a trap, then begin
  from a canonical state in which food is unavailable, the hunter has no trap
  materials, no trap is set, and the fox has neither reached food nor been
  caught. A developer or launcher shall supply the session turn limit `N` at
  start as a non-boolean integer from `1` through `10`; the system shall record
  it by value as an authoritative initial input. For any other value, it shall
  raise `ValueError` before event selection or actor reaction. The session
  shall advance to its ending without waiting for observer input; the observer
  shall supply no causal input.
- **When** a nonterminal clearing turn begins, **the simulation shall** select
  exactly one event uniformly from this scenario's event vocabulary and record
  its ordinal and selected name before applying its effect. An event may be
  selected more than once:

  - `food_scent` makes food available, exposes a food scent to the fox, and
    exposes fresh fox tracks to the hunter;
  - `trap_materials_arrive` makes trap materials available and exposes their
    arrival to the hunter, while exposing neither the materials nor their
    arrival to the fox.

  The selected event is controlled variation. Its selection policy, name,
  ordinal, and effect are authoritative history, rather than observer input or
  presentation data.
- **When** the supplied actors react to an event, **the system shall** make one
  real-LLM, actor-local cognition call for each actor using only that actor's
  filtered observation and own retained feedback context. Its fixed prompt
  shall require a JSON object with nonblank `question` and `sensemaking`
  strings based only on those supplied facts. The returned cognition is untrusted,
  non-authoritative, and shall not select or alter a proposal, state,
  resolution, event, or feedback. The system shall retain the prompt, raw
  response or null, validation status, and accepted cognition or fixed
  actor-local fallback in the causal record. Blank, malformed, unavailable, or
  exceptional output shall use that fallback without preventing the turn.
  The system shall then use deterministic scenario-local policies. The fox shall propose
  `approach_food` when its observation contains a food scent and otherwise
  `wait`. The hunter shall propose `set_trap` when its observation says trap
  materials are available and no trap is set, and otherwise `wait`. No model,
  network service, or observer message shall select or alter either proposal.
- **When** an actor is asked to react, **the system shall** provide only that
  actor's filtered observation and its own retained feedback context. The fox
  may receive its food-scent observation and its own previous feedback, but
  shall not receive trap-material availability, trap state, the hunter's
  observation, proposal, feedback, or the selected event name. The hunter may
  receive trap-material availability, fresh-track observation, trap state, and
  its own previous feedback, but shall not receive food availability, the
  fox's observation, proposal, or feedback, or the selected event name.
- **When** the simulation resolves reactions, **the system shall** resolve the
  hunter before the fox. A valid `set_trap` sets a trap only when materials are
  available and no trap is already set; otherwise it is rejected without a
  canonical transition. A valid `approach_food` ends the session with
  `caught` when a trap is set, and otherwise ends it with `fed` when food is
  available. `wait` makes no canonical transition. Only this simulation
  resolution may commit canonical state or select actor feedback.
- **When** the session has not ended through `caught` or `fed`, **the system
  shall** run the next turn until it has resolved `N` turns. It shall then end
  as `clearing_quiet`. Thus a run whose first selected event is `food_scent`
  ends `fed` on its first turn; after `trap_materials_arrive` enables the
  hunter to set a trap, any later `food_scent` ends `caught`; and a run with no
  `food_scent` in its `N` recorded events ends `clearing_quiet`. No event is
  selected after an ending.
- **When** a turn completes, **the system shall** append a JSON-safe,
  by-value causal record in this order: selected event and ordinal, event
  effect, each actor's filtered observation and retained context, its LLM
  cognition record, each deterministic policy result and proposal, resolution
  and feedback, resulting canonical state, and, where applicable, ending. The
  normal terminal surface shall make one real-LLM observer-narration call after
  each completed turn using only the completed causal record. Narration is
  untrusted, non-authoritative presentation; the surface shall print a concise
  current-turn account and every actor-cognition and narration prompt with its
  raw LLM response or explicit unavailable marker. It shall also allow an
  observer to inspect a readable account that distinguishes the recorded causal
  stages.
- **When** an observer inspects a completed session, replays it, or starts a
  fresh run after its ending, **the system shall** treat the control as
  noncausal. Inspection shall not modify history; exact replay shall consume
  the recorded event history without random selection, actor mediation, or
  model call; and a fresh run shall start a new history from the specified
  initial state and may select a different event sequence. The normal terminal
  surface shall make causal inspection, exact replay, and fresh run available
  without source edits or observer-supplied causal choices.
- **When** replay receives a history whose event name, ordinal, event effect,
  observation, proposal, resolution, feedback, resulting state, ending, or
  initial `N` is changed, missing, or reordered, **the system shall** reject
  it rather than choose a replacement event, mediate an actor again, or
  continue from an altered state.
- **When** actor cognition is unavailable, malformed, blank, or exceptional,
  **the system shall** retain and display a fixed, readable actor-local
  fallback. The fallback shall not prevent the deterministic policy from
  proposing its action or alter canonical state, event selection, actor policy,
  or replay. **When** observer prose rendering is unavailable, malformed,
  blank, or exceptional, **the system shall** display a fixed, readable
  structured fallback composed only from the already-recorded event, proposals,
  resolution, state, and ending. It shall not alter canonical state, event
  selection, actor policy, or replay.

### Builder-controlled clearing composition

- **When** a builder supplies a readable declaration naming one simulation
  component and named fox and hunter actor components, **the system shall**
  validate every actor proposal pairing before observation, mediation, or
  resolution. Validation shall be structural: each actor-declared proposal
  must be paired with a proposal accepted for that actor by the selected
  simulation; it shall not claim semantic compatibility or domain validity.
- **When** the validated baseline declaration runs, **the system shall** let
  the supplied clearing rules derive separate actor-visible inputs, let the
  supplied actors form their bounded proposals, and let those rules resolve
  the retained proposals. The baseline rules resolve hunter then fox; the
  supplied fox-first rules resolve fox then hunter. Replacing only the supplied
  fox component, or separately only the rules component, shall produce an
  inspectable causal difference while the unrelated component remains supplied
  unchanged.
- **When** a composed clearing turn completes, **the system shall** retain a
  JSON-safe trace by value containing the declaration and participating
  component names, proposal pairings, source state, actor-visible inputs,
  actor cognition and proposals, simulation resolution and feedback, and
  resulting state. Replay shall re-derive simulation-owned observations and
  resolution without actor mediation and reject a changed recorded declaration,
  pairing, input, proposal, resolution, feedback, or resulting state.
- **When** a builder runs the supplied stateful clearing declaration, **the
  system shall** execute exactly two ordinal authoritative steps. The second
  source state shall equal the first resulting state. Each step shall retain by
  value its source state, actor-visible input, actor-owned retained context,
  bounded proposal, resolution order, decisions, transitions, outcome,
  feedback, and resulting state.
- **When** the supplied clearing declaration starts, **the system shall** treat
  `trap_materials_ready` as a simulation-owned canonical source input: `true`
  means the hunter's trap materials are ready, and `false` means they are not
  ready. The simulation shall expose that readiness only in the hunter's
  actor-visible input and shall resolve `set_trap` into `trap_set` only when
  the input is `true`; the engine shall not interpret or alter that clearing
  meaning.
- **When** a stateful actor runs its next step, **the system shall** provide
  only that actor's simulation-filtered input and its own retained context.
  Its declared context reducer shall receive only its prior context and its
  own simulation-selected feedback. The supplied clearing declaration shall
  have the hunter set a trap while the fox waits in step one, then catch the
  approaching fox in step two.
- **When** a builder replays a two-step clearing timeline, **the system shall**
  re-derive simulation inputs and authoritative resolutions without mediation,
  and reject a changed ordinal, source or resulting state, retained context,
  actor-visible input, proposal, resolution order, decision, transition,
  outcome, or feedback.
- **When** a builder compares the supplied two-step clearing declaration with
  its fixed alternative, **the system shall** retain one JSON-safe record by
  value naming the initial-source parent point, the sole
  `trap_materials_ready: true -> false` variation, and both two-step
  authoritative timelines. The parent shall catch the fox; the alternative
  shall show unavailable materials only to the hunter, not set a trap, and let
  the fox reach food. Each timeline shall replay independently without actor
  mediation, and replay shall reject a changed parent point, source variation,
  parent timeline, or alternative timeline.

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
