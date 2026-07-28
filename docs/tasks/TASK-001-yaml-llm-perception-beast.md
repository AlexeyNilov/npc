# TASK-001: YAML-declared LLM perception changes beast rule selection

**Status:** Ready

**Owner:** Technical Lead

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `3d134c78ce4039aa82006046c821f20a49b4a62e`

**Depends on:** None — roadmap outcome 1 is completed.

**Write scope:** `src/npc/`, `actors/`, `scenarios/`, `tests/`,
`docs/evidence/`, `docs/requirements.md`, `docs/architecture.md`, and the
status of roadmap outcome 2 in `docs/roadmap.md` at completion only.

**Parallel-safe with:** None — this packet changes the current proof's shared
runtime path and its only behavioural test module.

**Durable information changed:**

- What did the bounded mediated-perception experiment demonstrate? →
  `docs/evidence/2026-07-28-yaml-llm-perception-beast.md`
- What must the system do? → `docs/requirements.md`, `LLM-backed perception`
  after accepted verification only.
- How does the system work now? → `docs/architecture.md` after accepted
  verification only.
- What should happen next? → mark only roadmap outcome 2 `Completed` after
  all completion reconciliation; do not add, remove, or reorder any other
  outcome.

**Simplifier review:** Required: the packet adds an LLM-mediated execution
boundary and changes the CLI's cross-module control flow.

## Outcome

An observer can run one YAML beast scenario whose profile declares two binary
perception questions. Before each selection, the engine supplies the LLM one
request containing those questions and the YAML-declared actor-accessible view.
The parsed answers may choose an existing profile rule, but only `resolve`
changes canonical state. This proves mediated perception without promoting the
proof format into a reusable platform.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Actor-accessible view | Roadmap outcome 2, visibility decision; glossary | The engine projects actor identity/location and entities named by the scenario's visible-entity declaration before every model request. It excludes all other canonical entities. | Scenario declares the subset; engine derives and serializes it. | Ephemeral per-turn request input; never canonical state. | Milestone-local visibility declaration; no general sensing model. |
| Actor-owned binary question | Roadmap outcome 2; requirements; glossary | Profile YAML declares question text. A request includes every declared text once. | Actor profile owns question meaning; engine batches it. | Static profile input; no mutation. | The proof's exact YAML list and prompt wording are disposable. |
| Perception answer | Roadmap outcome 2, failure decision | The response must be a JSON object with exactly the declared question texts as keys and JSON booleans as values. A missing, extra, malformed, or non-boolean entry is a perception error. | LLM proposes untrusted answers; engine parser accepts or rejects them. | Ephemeral per-turn selection input; never persisted or copied into `State`. | Strict JSON mapping is a bounded proof contract, not a general percept format. |
| `perception_answer` condition | Roadmap outcome 2 acceptance evidence 1 and 3 | A rule condition compares one declared question's parsed boolean answer to `is: true` or `is: false`; it composes with existing `all` and `not` conditions. | Profile YAML selects its policy; matching code only evaluates the bounded comparison. | Used only during that turn's selection. | Disposable rule predicate; it introduces no new canonical state or action type. |
| Perception error | Roadmap outcome 2 failure decision; requirements | A diagnostic failure raised before rule selection or resolution when request or contract validation fails. | Engine perception boundary. | Terminates the current CLI run; does not mutate state. | Error text is implementation detail, but it must identify perception as the cause. |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| Actor-accessible view | Existing glossary entry | Canonical name for the engine-to-LLM information boundary. |
| Actor-owned question | Existing glossary entry | Canonical name for YAML questions sent in the single request. |
| Action proposal | Existing glossary entry | Confirms that parsed answers cannot be an action or outcome. |
| Perception answer / perception error | Packet-local proof terms | They name only the bounded response contract and failure path; do not add glossary entries unless accepted work establishes a shared meaning beyond this outcome. |

## Experiment evidence

- **Evidence record:** `docs/evidence/2026-07-28-yaml-llm-perception-beast.md`.
- **Hypothesis and decision unlocked:** The record tests whether a YAML profile
  can use LLM-derived binary perception through an engine-enforced information
  boundary while preserving authoritative action resolution. Its result informs
  whether later work can inspect mediated perception (roadmap outcome 3), not
  whether this proof format is reusable.
- **Result handoff:** At Review, fill every Result field, set the record to
  `Review`, and provide fixtures and exact commands. The Technical Lead
  finalizes the record after Simplifier review and roadmap closure.

## Vision alignment

- **Vision behavior made observable:** actor-specific cognition receives only
  actor-permitted world data, asks actor-owned questions, and influences only
  a bounded action proposal.
- **Classification:** `Disposable experiment scaffolding`.
- **Reuse pressure:** Not in scope — the proof intentionally tests one beast,
  one entity-list visibility declaration, and JSON booleans only.
- **Boundary rejection signal:** Any need for sensing inference, retained
  subjective state, alternate response types, multi-actor batching, or replay
  requires a later product decision rather than extension of this packet.

## Canonical context

- [Roadmap outcome 2](../roadmap.md): `YAML-declared LLM perception for the beast`.
- [Requirements](../requirements.md): `LLM-backed perception`.
- [Decision](../decisions.md): `2026-07-26: Use Natural Language as the Default Interface Between Actors and the World`.
- [Architecture](../architecture.md): `Runtime shape`, `Canonical runtime model`,
  and `Turn processing and authority`.
- Initial entry points: `src/npc/__main__.py`, `src/npc/simulation.py`,
  `src/npc/infrastructure/language_model.py`, and
  `tests/test_yaml_beast_proof.py`.

Read `AGENTS.md`, this packet, the Implementer guide, and only the context
listed above. Do not read the task registry, sibling packets, completed tasks,
or unrelated planning history.

## Task-specific scope

- Add a narrowly scoped perception step to the CLI turn loop. It must derive
  the visible view, make exactly one non-streaming LLM request per turn for all
  declared questions, validate the strict JSON boolean mapping, then pass the
  accepted mapping into rule selection. The existing no-question profiles may
  retain their current deterministic path without a model call.
- Add a scenario fixture with two visible entities and at least one inaccessible
  entity, plus a profile containing at least two questions and rules whose
  outcomes differ for mocked true/false answers. Use a captured mocked request
  in tests; tests must not require a running LLM.
- Extend matching only with the `perception_answer` comparison described in
  Concept provenance. Existing proposal construction and `resolve` contracts
  remain unchanged.
- Make unavailable, malformed JSON, missing/extra answer, and non-boolean
  responses terminate with a diagnostic perception error before selection or
  resolution. The CLI must return non-zero on this failure.
- Keep the LLM request limited to an explicit instruction, the full declared
  question list, and the derived accessible view. Do not include a proposal
  schema, rule order, action target, destination, resolver result, whole
  scenario YAML, or hidden entity data in that request.
- At Review only, update requirements and architecture with verified behavior,
  complete the evidence record, and complete the narrowly allowed roadmap
  status change.

Explicit exclusions: fallback or retry policy; natural sensing or spatial
visibility; subjective-state persistence; LLM-produced action proposals or
narration; replay; public schemas; modifying the resolver; and any change to
outcomes 3 or later.

## Acceptance and verification

Write failing tests before application behavior. Verification must establish:

1. One captured request contains both YAML-declared questions and an accessible
   serialization containing the designated visible entities but not the hidden
   fixture entity.
2. A mocked valid binary mapping selects a `perception_answer` rule and changes
   the resolved beast trace; changing only a declared question or its
   perception-dependent rule changes selected behavior without engine edits.
3. The captured prompt cannot contain action kinds, proposal labels, targets,
   destinations, rules, resolver outcomes, or hidden content. The model-facing
   return value is only the validated boolean mapping.
4. A perception-informed proposal still reaches the existing resolver, which
   can reject it without a state transition. Retain the existing unsupported
   proposal rejection coverage.
5. Simulated request failure, malformed JSON, missing answer, extra answer,
   and non-boolean answer each produce a diagnostic perception error; spies or
   state assertions prove neither selection nor `resolve` occurs for the
   failed turn.
6. Existing no-question scenario traces and all outcome-1 behavioural tests
   remain unchanged.
7. Run the focused test module, then `make check` and `git diff --check`.
   Verify changed Markdown links. Record any pre-existing repository-wide link
   failure as an issue rather than ignoring it.

## Stop conditions

- The request needs a visibility rule beyond YAML entity inclusion, a nonbinary
  answer, retained subjective state, an action-return contract, or multi-actor
  behaviour: stop and route the product/data-meaning decision to the Product
  Manager.
- Existing accepted context conflicts with the strict one-request boundary or
  makes the proposed prompt expose inaccessible data: stop for Technical Lead
  resolution.
- Required LLM client behavior cannot be mocked without live external access,
  or a dependency/API change is necessary: stop and report the technical
  constraint; do not add a dependency or external service.
- Any unrelated user-owned change overlaps this write scope, required test
  fixture, or canonical document.

## Handoff

**Status and outcome:** Ready — implementation has not begun.

**Changed files and ownership impact:** Planning only:
`docs/tasks/TASK-001-yaml-llm-perception-beast.md` and
`docs/tasks/STATUS.md`; they own the open delivery assignment and its registry
row. No system behavior or durable system facts changed.

**Verification:** Packet context and current entry points inspected; no
application behavior changed.

**Assumptions, risks, and next action:** The strict response mapping and
entity-list declaration are deliberately local scaffolding justified by outcome
2. Assign one Implementer to this Ready packet, then obtain Simplifier review
at Review before completing the evidence and roadmap reconciliation.
