# Architecture

This document owns the current verified system design. It describes the first
reboot proof as implemented, not a target reusable simulation platform.

For project-specific vocabulary, see the [Glossary](glossary.md). Observable
behaviour is owned by [Requirements](requirements.md).

## Runtime shape

```text
scenario YAML ──┐
                ├── load_scenario ──> canonical State + profile rules + PerceptionConfig
actor-profile ──┘                                                  │
                                                ▼
CLI (`python -m npc <scenario>`) ──> turn loop ──> perceive ──> select proposal
                                                │                  │
                                                │                  ▼
                                                └────────── resolve proposal
                                                                    │
                                                                    ▼
                                                             Outcome narration ──> stdout
```

`src/npc/__main__.py` is the command-line adapter. It takes the scenario path
from its first argument, obtains the state and rules, reads the scenario's
`turn_limit`, and runs at most that many turns. It prints the narration from
each resolved proposal. A turn with no matching rule ends the run.

`src/npc/simulation.py` contains the complete proof simulation: YAML loading,
perception input derivation and validation, rule selection, proposal
construction, and authoritative resolution. Questioned turns call the existing
non-streaming LLM completion adapter once; profiles with no questions skip it.

## Input boundary

The command accepts a scenario YAML document. That document supplies:

- `actor_profile`: a path resolved relative to the scenario file;
- one actor's identifier and initial integer location;
- entities with identifiers, integer locations, tags, and optional
  `consumable` status; and
- for the perception fixture only, `visible_entities`: the explicit entity IDs
  permitted in the actor-accessible view; and
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
| `PerceptionConfig` | profile questions and visible entity IDs | Immutable load input passed to `perceive`; it is not canonical state and is used only to derive an ephemeral request. |
| `Entity` | identifier, location, tags, consumable/consumed state | A scenario object that may participate in conditions or consumption. |
| `Proposal` | action kind, actor identifier, destination or target, label | A bounded attempted action; it has no authority to update state. |
| `Outcome` | accepted flag and narration | The result returned by authoritative resolution and printed by the CLI. |

Locations are unbounded integers on a disposable one-dimensional line. Entity
lookup selects the first unconsumed entity with the requested tag in scenario
input order. These choices are proof scaffolding, not a spatial or targeting
model for later milestones.

## Turn processing and authority

For each turn, the following happens in order:

1. For a profile with questions, `perceive` derives an actor-accessible view
   containing only the actor identity/location and scenario-declared visible
   entities, then makes one completion request containing that view and all
   question texts. It accepts only a JSON object whose keys exactly match the
   questions and whose values are booleans. A request or validation failure is
   a diagnostic perception error: the CLI exits non-zero before selection or
   resolution. Profiles without questions use an empty answer mapping and make
   no request.
2. `select_proposal` scans the actor profile's rules in YAML order and selects
   the first matching rule.
3. `_matches` evaluates only the proof predicates: conjunction (`all`),
   negation (`not`), `perception_answer`, tag presence, tag co-location, and
   maximum distance to a tagged entity.
4. `_proposal_from_rule` turns the selected rule into a `Proposal`. A movement
   proposal moves one location toward or away from its tagged reference; a
   consumption proposal names the matching tagged entity.
5. `resolve` validates the proposed actor and action form. It is the only
   function that changes `State`.
6. The CLI prints the resulting `Outcome.narration` after the resolution has
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

The current implementation has no subjective state, persistence, replay
mechanism, public schema, multi-actor scheduling, map topology, or general
action registry. The entity-list visibility declaration, prompt wording,
strict binary JSON mapping, and `perception_answer` predicate are bounded
proof scaffolding, not a general sensing or perception platform.
