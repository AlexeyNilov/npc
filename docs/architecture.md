# Architecture

This document owns the current verified system design. It describes the first
reboot proof as implemented, not a target reusable simulation platform.

For project-specific vocabulary, see the [Glossary](glossary.md). Observable
behaviour is owned by [Requirements](requirements.md).

## Runtime shape

```text
scenario YAML ──┐
                ├── load_scenario ──> canonical State + profile rules
actor-profile ──┘                              │
                                                ▼
CLI (`python -m npc <scenario>`) ──> turn loop ──> select proposal
                                                │             │
                                                │             ▼
                                                └──── resolve proposal
                                                             │
                                                             ▼
                                                      Outcome narration ──> stdout
```

`src/npc/__main__.py` is the command-line adapter. It takes the scenario path
from its first argument, obtains the state and rules, reads the scenario's
`turn_limit`, and runs at most that many turns. It prints the narration from
each resolved proposal. A turn with no matching rule ends the run.

`src/npc/simulation.py` contains the complete proof simulation: YAML loading,
rule selection, proposal construction, and authoritative resolution. No code
on this execution path imports or invokes the LLM infrastructure.

## Input boundary

The command accepts a scenario YAML document. That document supplies:

- `actor_profile`: a path resolved relative to the scenario file;
- one actor's identifier and initial integer location;
- entities with identifiers, integer locations, tags, and optional
  `consumable` status; and
- `turn_limit`.

The referenced actor-profile YAML supplies capabilities, motivations,
`perception_questions`, and an ordered rule list. Rules contain a condition, a
proposal specification, a motivation label, and an observer-facing label.
Motivations are currently profile-local labels only: the selection algorithm
does not inspect, compare, or otherwise evaluate them.

This is a local proof format, not a published schema. The loader directly
indexes the expected YAML fields and does not perform schema validation or
recover from malformed input.

## Canonical runtime model

| Value | Held data | Role |
| --- | --- | --- |
| `State` | actor identifier, actor location, capabilities, entities | The mutable canonical state for one run. |
| `Entity` | identifier, location, tags, consumable/consumed state | A scenario object that may participate in conditions or consumption. |
| `Proposal` | action kind, actor identifier, destination or target, label | A bounded attempted action; it has no authority to update state. |
| `Outcome` | accepted flag and narration | The result returned by authoritative resolution and printed by the CLI. |

Locations are unbounded integers on a disposable one-dimensional line. Entity
lookup selects the first unconsumed entity with the requested tag in scenario
input order. These choices are proof scaffolding, not a spatial or targeting
model for later milestones.

## Turn processing and authority

For each turn, the following happens in order:

1. `select_proposal` scans the actor profile's rules in YAML order and selects
   the first matching rule.
2. `_matches` evaluates only the proof predicates: conjunction (`all`),
   negation (`not`), tag presence, tag co-location, and maximum distance to a
   tagged entity.
3. `_proposal_from_rule` turns the selected rule into a `Proposal`. A movement
   proposal moves one location toward or away from its tagged reference; a
   consumption proposal names the matching tagged entity.
4. `resolve` validates the proposed actor and action form. It is the only
   function that changes `State`.
5. The CLI prints the resulting `Outcome.narration` after the resolution has
   accepted or rejected the proposal.

The profile owns policy: rule order, conditions, motivation labels, tags used
for selection, and the label shown to the observer. Rule order, not motivation
semantics, resolves this proof's choice conflicts. The simulation core owns
mechanism: capability checks, movement transition, consumption preconditions,
state mutation, and rejection. Therefore a profile may describe fleeing by
selecting a move-away proposal, while the core has no beast-, threat-, or
food-specific branch.

## Resolution contracts

`resolve` supports exactly two accepted proposal kinds:

- `move` requires the declared `move` capability and an explicit destination;
  acceptance replaces the actor location.
- `consume` requires the declared `consume` capability, an existing consumable
  target at the actor's location, and an unconsumed target; acceptance marks
  that entity consumed.

An unknown actor, missing capability or required data, invalid consumption
precondition, or unsupported action returns a rejected `Outcome`. Rejection
does not mutate canonical state.

## Deliberate absences

The current implementation has no perception evaluation, LLM call, subjective
state, persistence, replay mechanism, public schema, multi-actor scheduling,
map topology, or general action registry. Future work must add these only when
an accepted roadmap outcome requires them; none is implied by the proof
scaffold.
