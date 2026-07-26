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

### Fox and hunter shared-world turn

- **When** a developer runs the checked-in shared-world scenario, **the
  system shall** start one authoritative turn with the fox at a clearing edge,
  food available in the clearing, a hunter concealed beside it, fresh fox
  tracks leading to the food, an unset trap, and trap materials ready. The fox
  is not caught and the food is not consumed. The simulation core alone owns
  the fox and hunter locations, concealment, tracks, trap state, material
  readiness, food state, and all later transitions.
- **When** observation begins, **the system shall** derive each actor's
  actor-accessible substate from that same initial canonical state before either
  actor's mediation request or proposal is resolved. The fox shall receive:
  `You are at the edge of a clearing. You smell food in the clearing. The
  clearing appears quiet.` The hunter shall receive: `You are concealed beside
  a clearing. Fresh fox tracks lead toward food. Your trap materials are
  ready.` The fox shall not receive the hunter, tracks, trap state, or material
  readiness; the hunter shall not receive the fox's exact location, percept,
  questions, or eventual proposal.
- **When** the fox forms its actor-local percept, **the system shall** supply
  this actor-owned profile: `You are hungry and cautious. You cannot see a
  concealed hunter or a hidden trap. Treat smells and apparent quiet as clues,
  not facts.` Its ordered binary questions shall be: `Do I believe an immediate
  threat is present?` and `Do I believe the food is reachable by approaching?`
  Its bounded proposal vocabulary shall be `approach_food` and `wait`.
- **When** the hunter forms its actor-local percept, **the system shall**
  supply this actor-owned profile: `You are a patient hunter. Fresh tracks are
  clues to likely movement, not proof of the fox's current position.` Its
  ordered binary questions shall be: `Do I believe a fox is likely to approach
  the food this turn?` and `Do I believe I can set the trap now?` Its bounded
  proposal vocabulary shall be `set_trap` and `wait`.
- **When** each actor is mediated, **the system shall** make one request per
  actor using only that actor's accessible substate, profile, and ordered
  questions. It shall record one subjective percept per actor and retain each
  answer with its own supporting reference to content in that actor's percept.
  The fox shall propose `approach_food` only when it believes no immediate
  threat is present and believes food is reachable; otherwise it shall propose
  `wait`. The hunter shall propose `set_trap` only when it believes a fox is
  likely to approach and believes it can set the trap; otherwise it shall
  propose `wait`.
- **When** either actor's percept or answer is malformed, lacks valid percept
  evidence, or yields a proposal outside that actor's vocabulary, **the system
  shall** fail closed to that actor's `wait` proposal. Neither actor's model
  output shall directly change canonical state.
- **When** both actors have submitted proposals, **the simulation core shall**
  resolve the hunter proposal first and the fox proposal second, after both
  actors have observed the initial state. A valid `set_trap` with ready
  materials changes the trap from unset to set. A later `approach_food` meets a
  set trap, changes the fox to caught, leaves the food unconsumed, and commits
  the authoritative outcome `fox_caught_by_trap`. The fox shall receive
  `A hidden trap catches you as you reach the food.` and the hunter shall
  receive `Your trap catches the fox.`
- **When** the same source state instead has trap materials unavailable,
  **the system shall** derive the hunter observation `Your trap materials are
  not ready.` in place of `Your trap materials are ready.` If the hunter does
  not set a trap and the fox validly proposes `approach_food`, the simulation
  core shall move the fox to the food, mark the food consumed, and commit
  `fox_reaches_food`. The fox shall receive `You reach the food.` and the
  hunter shall receive `The fox reaches the food.` This alternate authoritative
  result is the required source-state variation.
- **When** the shared-world turn completes, **the system shall** retain a
  JSON-safe trace containing the initial canonical state; both actor-accessible
  substates, profiles, percepts, ordered questions, answers and percept
  evidence; both proposals; the authoritative resolution order and decisions;
  resulting canonical transitions; and actor-specific feedback. Replaying the
  trace shall reproduce the authoritative sequence without making mediation
  requests.

### Village emergency-food rationing turn

- **When** a developer runs the checked-in village-rationing corpus, **the
  system shall** start from canonical state containing a six-unit emergency
  food reserve and no committed household allocations. The fixed corpus shall
  give household one a four-unit claim at priority tier one and household two a
  four-unit claim at priority tier two. The simulation core alone owns the
  reserve, the claim ledger, allocation rule, and committed allocations.
- **When** the household claimants form their actor-local percepts, **the
  system shall** provide each one only its own private household view and its
  own profile and ordered question set. Each claimant may submit only its own
  four-unit claim or `wait`. Neither claimant shall receive the other
  claimant's private view, profile, questions, percept, or proposal.
- **When** a claimant submits its valid four-unit claim, **the simulation core
  shall** record the claimant's household identifier, requested units, and
  priority tier in the public claim ledger before relief-organisation
  mediation. A failed-closed `wait` claim shall not add a ledger entry.
- **When** the relief-organisation actor forms its actor-local percept, **the
  system shall** provide only the canonical reserve and the public claim
  ledger, whose entries contain household identifier, requested units, and
  priority tier. The request shall contain neither household's private view,
  food situation, dependants, profile, questions, percept, nor proposal. The
  organisation may submit only one bounded allocation proposal for the two
  public claims; it cannot directly commit an allocation.
- **When** each actor is mediated, **the system shall** make one request per
  actor using only that actor's accessible substate, profile, and ordered
  questions. It shall record one subjective percept per actor and retain each
  answer with its own supporting reference to that actor's percept. A
  malformed percept or answer, missing or invalid percept evidence, or a
  proposal outside that actor's vocabulary shall fail closed and make no
  unauthorized canonical change.
- **When** both four-unit claims are present and the organisation proposes the
  priority allocation, **the simulation core shall** validate and commit four
  units for household one and two units for household two, leaving no reserve.
  It shall return actor-specific allocation feedback without exposing either
  household's private view to another actor.
- **When** only the canonical reserve changes from six to four units, **the
  system shall** derive an organisation observation that states four available
  units in place of six, while retaining the same public claims and withholding
  the same private household facts. The same priority rule shall commit four
  units for household one and zero for household two, leaving no reserve.
- **When** an allocation exceeds a public claim or the reserve, or differs
  from the priority rule, **the simulation core shall** reject it without
  changing the reserve or committed allocations. A submitted proposal is not
  itself an allocation.
- **When** a village-rationing turn completes, **the system shall** retain a
  JSON-safe trace containing the initial canonical state; each actor's
  accessible substate, profile, percept, ordered questions, answers and
  percept evidence; submitted claims and allocation proposal; authoritative
  validation decision and transitions; resulting canonical state; and
  actor-specific feedback. Replaying that trace shall reproduce the committed
  or rejected authoritative outcome without making another mediation request.

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
