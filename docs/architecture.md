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
