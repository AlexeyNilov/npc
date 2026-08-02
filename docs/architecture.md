# Architecture

This document owns the current verified system design. For project-specific
vocabulary, see the [Glossary](glossary.md). Observable behaviour is owned by
[Requirements](requirements.md).

## Simulation-platform foundation

`SimulationBuilder` in `npc.platform` composes an initial authoritative world,
participant profiles, and supplied scheduler, access policy, decision policy,
mediator, resolver, and optional presenter. The builder copies the profile
mapping and snapshots its initial world, then refuses an empty participant set.
It does not parse scenarios or profiles: an application owns those source
formats and its domain semantics.

For one `run_next` call, the scheduler selects a participant from the composed
profile IDs. The engine snapshots the canonical world before passing it to the
scheduler or access policy, so neither can mutate canonical state. It obtains
that participant's profile, asks the access policy to derive an
actor-accessible view, and asks the decision policy for that actor's questions.
The mediator receives only this view and the declared questions. It must return
exactly the same question keys with JSON booleans; malformed, missing, extra,
or non-boolean answers raise `MediationError` before proposal construction or
resolution.

The decision policy transforms the profile, view, and validated answers into a
bounded domain proposal. The resolver is the only component that receives a
world working copy and returns the next authoritative world and outcome. The
engine snapshots that returned world before committing it, then appends a
snapshot `TurnRecord` containing the participant, accessible view, validated
answers, proposal, and outcome. `history`, the public world property, turn
results, and presenter input each receive fresh snapshots; a caller cannot
change retained canonical state or history through a mutable value.

Presentation is deliberately outside this transition. If configured, a
presenter receives the completed record only after the record is appended. Its
text is returned alongside the turn result rather than stored as canonical
history. A presenter exception or blank response produces no presentation and
does not undo the committed world or record.

`LanguageModelMediator` is the supplied LLM implementation of the mediation
boundary. It makes one completion request containing the accessible view and
all questions for the observation, then applies the same exact boolean-map
validation. Applications may inject another mediator for deterministic or
non-LLM operation.

The foundation deliberately provides no YAML DSL, persistence, replay,
topology, action vocabulary, or domain module. The removed beast and trader
proofs are not compatibility paths.

## Two-player property-board application

`npc.property_board` is an application module that reads
`scenarios/property_board.yaml` and its separately authored actor profiles.
The application's loader owns this YAML format: its `platform` section names
the two participants, profile paths, and alternating scheduling, while its
`property_board` section supplies the accepted board fixture and only action.
The generic platform does not parse this file or import this module.

`build_game` composes the loaded profiles and an initial `BoardWorld` through
`SimulationBuilder`. `AlternatingScheduler` selects the next player;
`PublicBoardAccess` gives the active player the public game state and its
deterministic next landing; and `PurchaseDecisionPolicy` asks that player's
profile-owned binary question only for an unowned property. A true or false
answer becomes respectively the sole `buy_landed_property` proposal or no
proposal.

`PropertyBoardResolver` is the only component that changes board state. It
moves the selected player one space, records a purchase when its fixed price
is affordable, transfers fixed rent on another player's property, and ends the
world immediately on an unpaid rent or after the sixteenth completed turn.
Each platform `TurnRecord` retains the pre-resolution public view, question
and validated answer, attempted proposal, and authoritative board outcome.
The module entry point prints those canonical records as JSON after each turn.
