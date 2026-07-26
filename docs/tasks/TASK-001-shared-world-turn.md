# TASK-001: Resolve one shared fox-and-hunter world turn

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `27e9af5bb56a3c3fa6049cbff125dea85aa6174e` plus the accepted, user-owned uncommitted shared-world requirement in `docs/requirements.md`

**Depends on:** None

**Write scope:** `src/npc/experiments/fox_hunter_shared_world.py`, `tests/test_fox_hunter_shared_world.py`, `scenarios/fox_hunter_shared_world.yaml`

**Parallel-safe with:** None — this task creates the one new scenario, module, fixture corpus, and its focused test.

**Durable information changed:** None. The Technical Lead reconciles the verified current design with Architecture at integration; this task must not edit `docs/requirements.md`, which contains user-owned accepted behavior.

**Simplifier review:** Not required — this is bounded direct delivery with ordinary completion evidence; no reusable boundary is claimed.

## Outcome

A developer can run one deterministic, checked-in fox-and-hunter shared-world
turn in which both actors observe the same initial canonical state through
different permitted substates, submit actor-local proposals before either is
resolved, and the simulation core resolves hunter then fox. The ready-materials
case catches the fox; the unavailable-materials source variation lets it reach
and consume the food. A JSON-safe trace and replay make both authoritative
sequences inspectable without re-mediating.

This is the smallest verifiable implementation of the first roadmap outcome's
shared-world composition claim.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Shared initial clearing state: actor locations, hunter concealment, fox tracks, food, unset trap, material readiness, fox uncaught, food unconsumed | [Requirements — Fox and hunter shared-world turn](../requirements.md#fox-and-hunter-shared-world-turn) | The core initializes and alone owns these facts; it derives both observations before resolution. | Simulation core | Initial state → trace → replay | PM accepted in Requirements. |
| Fox and hunter accessible substates | Same requirement | Deterministically render the exact required observation text from the same canonical source; omit the facts forbidden to that actor. | Simulation core | Initial state → mediation input → trace/replay validation | PM accepted in Requirements. |
| Actor profiles, ordered questions, and proposal vocabularies | Same requirement | Retain each actor's specified actor-owned description; mediate each actor only from its own substate, profile, and questions. | Actor description / actor-local mediation | Immutable turn input → trace/replay validation | PM accepted in Requirements. |
| `approach_food`, `set_trap`, and `wait` proposals | Same requirement | Derive each proposal only from that actor's valid answers; malformed or out-of-vocabulary mediation yields that actor's `wait`. | Actor-local mediation proposes; simulation core accepts and resolves | Mediation result → proposal → trace/replay validation | PM accepted in Requirements. |
| Hunter-first then fox-second resolution order | Same requirement | Resolve only after both proposals are recorded; apply the hunter decision before the fox decision. | Simulation core | Recorded order → decisions → resulting state → replay | PM accepted in Requirements. |
| Trap/material and food transitions; `fox_caught_by_trap` and `fox_reaches_food` | Same requirement | Ready materials plus `set_trap` sets the trap; a later approach meets it and catches the fox. Unavailable materials prevent that trap path; a later approach moves the fox to food and consumes it. | Simulation core | Canonical transition → actor-specific feedback → trace/replay | PM accepted in Requirements. |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| actor-accessible substate, actor description, subjective percept, action proposal, authoritative simulation core, trace, replay | Existing [Glossary](../glossary.md) entries | Shared actor/simulation boundary terminology used by the requirement and implementation. |
| fox/hunter, clearing, tracks, trap materials, `set_trap`, `fox_caught_by_trap`, `fox_reaches_food` | Packet-local disposable scenario labels | They name this one bounded scenario and do not claim a reusable domain model. |

## Experiment evidence

Not applicable. The roadmap explicitly calls for ordinary completion evidence;
this packet is direct delivery, not a decision-selecting experiment.

## Vision alignment

Not applicable — no reusable system boundary is claimed. The new module,
fixtures, trace types, and deterministic resolver are disposable bounded-scenario
scaffolding.

## Canonical context

- [Requirements — Fox and hunter shared-world turn](../requirements.md#fox-and-hunter-shared-world-turn).
- [Roadmap — Compose a shared authoritative world for heterogeneous actors](../roadmap.md#1-compose-a-shared-authoritative-world-for-heterogeneous-actors).
- [Architecture — Fox language-mediated causal turn](../architecture.md#fox-language-mediated-causal-turn), as an existing causal-trace and mediation-validation reference only; do not generalize or modify it.
- Initial source and test entry points: `src/npc/experiments/fox_causal_turn.py`, `tests/test_fox_causal_turn.py`, and `scenarios/fox_causal_turn.yaml`.

Read `AGENTS.md`, this packet, the Implementer guide, and only the context
named above. Do not read the task registry, sibling packets, completed tasks,
or unrelated planning history.

## Task-specific scope

- Add a new, scenario-local module, test, and YAML fixture corpus. Do not alter
  the existing fox causal-turn module or its contract.
- Use injected deterministic mediation fixtures; no configured model call,
  dependency, generic actor/world/scheduler/conflict framework, narration,
  memory, or additional turns is authorized.
- Derive both observation strings from canonical state before invoking either
  mediator. Keep the two requests and all actor-local records separated.
- Retain both proposals before applying the fixed hunter-then-fox resolution;
  do not let one actor's percept, answers, or proposal reach the other actor.
- Implement only the accepted ready-materials and unavailable-materials paths,
  their fixed transitions, feedback, trace serialization, and replay checks.
- Preserve the user-owned uncommitted requirements change. Stop rather than
  editing it or adding new state, actions, observations, outcomes, or rules.

## Acceptance and verification

- Start with failing behavioral tests in `tests/test_fox_hunter_shared_world.py`
  for the ready-materials path, then implement application behavior.
- The checked-in corpus covers both required source states with valid fixture
  percepts/answers: ready materials records distinct exact substates, both
  proposals, resolution order `hunter` then `fox`, a set trap, caught fox,
  unconsumed food, `fox_caught_by_trap`, and exact actor feedback; unavailable
  materials changes the hunter substate and records `fox_reaches_food`, the fox
  at food, and consumed food.
- A source-variation test changes only canonical material readiness and proves
  the hunter observation and authoritative outcome change accordingly.
- Boundary tests capture both mediation inputs and prove the fox receives none
  of the hunter/trap/track/material facts, while the hunter receives none of
  the fox's exact location, percept, questions, or proposal.
- A malformed, missing-evidence, or out-of-vocabulary response for either
  actor fails closed only for that actor and cannot make an unauthorized
  canonical transition.
- Trace tests JSON-serialize the full two-actor trace. Replay reproduces both
  canonical transitions without invoking either mediator and rejects a changed
  recorded ordering, decision, transition, or feedback.
- Run `.venv/bin/pytest tests/test_fox_hunter_shared_world.py`, the module's
  checked-in corpus command, `make check`, and `git diff --check`.

## Stop conditions

- The accepted requirements conflict with an existing contract or need any new
  state meaning, observation, action, outcome, transition, feedback, ordering,
  or public interface.
- The scenario cannot meet the required boundary and source-variation tests
  without a generic actor/world/scheduling/conflict abstraction or changes to
  the existing fox causal-turn slice.
- User-owned changes outside the authorized files conflict with the work,
  required fixtures are missing, or verification exposes a requirement
  ambiguity.
- A real-model call, external mutation, new dependency, or scope expansion is
  needed.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
