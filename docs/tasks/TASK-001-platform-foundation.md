# TASK-001: General simulation-platform foundation

**Status:** Review

**Owner:** Technical Lead

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `895cb6c656b6c664f1a7023df953e805af70e02b`

**Depends on:** `None`

**Write scope:** `src/npc/`, `tests/`, `actors/`, `scenarios/`, `docs/tasks/`, `docs/architecture.md`, `docs/glossary.md`, `docs/roadmap.md`

**Parallel-safe with:** `None` — this replaces the current execution path and tests.

**Durable information changed:** how does the system work now? -> `docs/architecture.md`; shared component terminology -> `docs/glossary.md`; ordered incomplete outcomes -> `docs/roadmap.md` after acceptance.

**Simplifier review:** Required: new public, cross-module platform contracts.

## Outcome

A builder composes a domain-neutral simulation from a shared authoritative world,
participant profiles, and domain modules. The engine schedules participants,
mediates validated actor-owned binary questions over an actor-accessible view,
commits or rejects a bounded proposal through a supplied resolver, and retains
an inspectable canonical record for every completed turn.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Actor-accessible view | `docs/glossary.md#actor-loop-terms` | Supplied access policy filters authoritative state for one participant observation. | Access policy | Per observation; retained in turn record | None |
| Actor-owned question and validated answer | `docs/glossary.md#actor-loop-terms`, `docs/requirements.md#language-mediated-actor-decisions` | Decision policy supplies questions; mediator validates exact boolean answers before policy consumes them. | Actor decision policy and mediator | Per turn; retained in turn record | None |
| Action proposal and authoritative outcome | `docs/glossary.md#actor-loop-terms`, `docs/decisions.md#2026-07-26-use-natural-language-as-the-default-interface-between-actors-and-the-world` | A supplied resolver accepts or rejects an opaque proposal and alone returns the next canonical state. | Domain resolver | Per turn; retained in turn record | None |
| Scheduler | Packet-local implementation term | Selects the next participant; it creates no domain state or rule. | Supplied scheduler | Per engine step | None |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| Simulation Engine, actor-accessible view, actor-owned question, action proposal | Existing glossary entries | Public platform contracts use their preferred names. |
| Scheduler, access policy, decision policy, resolver, presenter | Add glossary entries after accepted implementation | Shared composition contracts. |

## Vision alignment

- **Vision behavior made observable:** the actor loop runs against shared authoritative reality while language mediation and presentation cannot mutate canonical state.
- **Classification:** `Candidate durable system foundation`
- **Reuse pressure:** a two-participant, shared-state test domain exercises scheduling, distinct access policies, accepted and rejected transitions, and post-resolution presentation.
- **Boundary rejection signal:** implementation needs a domain state field or rule in the engine to complete this test.

## Canonical context

- `docs/requirements.md`: all sections.
- `docs/decisions.md`: both accepted decisions.
- `docs/roadmap.md`: outcome 1.
- `README.md`: Vision and Simulation loop.
- `src/npc/simulation.py`, `src/npc/experiments/trader_offers.py`, and their tests.

## Task-specific scope

- Supply typed Python composition contracts and a builder; do not create a universal YAML schema.
- Keep profile and scenario parsing application-owned. Test-only fixture data may be Python.
- Delete the beast and trader proof implementation, YAML fixtures, tests, and obsolete CLI path.
- Exclude persistence, replay APIs, maps, property-game rules, and new dependencies.

## Acceptance and verification

- A test-only domain composes two distinct participants in one shared world.
- Each participant receives only its own permitted view; model answers are exact boolean mappings and invalid answers stop before resolution.
- A resolver alone changes canonical world state; both acceptance and rejection have immutable inspectable turn records.
- The next scheduled participant observes the committed preceding state.
- A presentation failure after commit leaves history and state intact.
- `make check` passes after removal of obsolete proof paths.

## Stop conditions

- A generic contract requires domain mechanics, a public YAML DSL, persistence, replay, map topology, or an unaccepted data meaning.
- A contract cannot express the acceptance behavior without the engine interpreting domain state.
- Unexpected user-owned changes overlap the write scope.

## Handoff

**Status and outcome:** Review — the platform foundation replaces the retired
proof paths and satisfies the packet's focused behavioral checks.

**Changed files and ownership impact:** `src/npc/platform.py` and
`tests/test_platform.py` add the platform and its test-only domain. The retired
beast/trader implementation, fixtures, tests, experiment package, and CLI were
removed. `docs/architecture.md` now owns the verified execution design.

**Verification:** `make check` — passed: Ruff format/lint, mypy, and 4 pytest
tests. `git diff --check` — passed.

**Assumptions, risks, and next action:** YAML source schemas remain
application-owned, consistent with the no-universal-DSL boundary. Obtain the
required Simplifier review; if accepted, add shared contract terms to the
glossary, mark roadmap outcome 1 completed, and remove this Done packet from
the registry.
