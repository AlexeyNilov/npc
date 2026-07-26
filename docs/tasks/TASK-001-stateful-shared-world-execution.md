# TASK-001: Run and replay a composed clearing scenario through two authoritative steps

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `8806c8e`

**Depends on:** `None`

**Write scope:** `src/npc/composition.py`, `src/npc/experiments/composed_clearing.py`, `tests/test_composition.py`, `docs/requirements.md`, `docs/architecture.md`, `docs/evidence/2026-07-26-stateful-shared-world-execution.md`, `docs/tasks/TASK-001-stateful-shared-world-execution.md`, and `docs/tasks/STATUS.md`

**Parallel-safe with:** `None` — the composition contract, its experiment, and its canonical records change together.

**Durable information changed:** Observable behavior -> [Requirements](../requirements.md); verified mechanism -> [Architecture](../architecture.md); experiment result -> [Experiment evidence](../evidence/2026-07-26-stateful-shared-world-execution.md); task lifecycle -> [Task registry](STATUS.md)

**Simplifier review:** Required — this changes the public composition execution boundary across modules.

## Outcome

A builder can execute one existing composed clearing declaration through exactly
two committed authoritative steps, inspect the resulting causal timeline, and
replay it without actor mediation.  This tests whether the completed
composition boundary survives one committed state change and a new actor
exchange without the engine acquiring world meaning.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Ordinal two-step timeline | [Roadmap outcome](../roadmap.md#1-stateful-shared-world-execution) | Exactly two sequential authoritative steps, numbered one then two | Engine sequences and records; simulation commits each state | Trace-only history; no branch or persistence model | Not new — roadmap authorizes the bounded slice |
| Retained context | [Glossary](../glossary.md#actor-loop-terms) and [Strategy target model](../strategy.md#target-modular-composition-model) | Actor-owned value supplied with that actor's next mediation input; its reducer receives only prior context and that actor's feedback | Actor owns context meaning and reduction; engine carries and records it | Initial actor value, then next-step input; retained in trace | Not new — accepted target term; no shared schema added |
| Resolution order and conflict rule | [Roadmap outcome](../roadmap.md#1-stateful-shared-world-execution) | Existing selected simulation declares and records them separately for each step | Simulation | Per-step authoritative resolution record | Not new — no universal representation |
| Clearing continuation | Existing [builder-controlled clearing requirement](../requirements.md#builder-controlled-clearing-composition) plus roadmap's non-binding fox/hunter example | The supplied rules accept their own previously committed clearing state for the one second step | Supplied clearing simulation | Disposable fixture state progression | No new shared domain meaning |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| Retained context | [Glossary](../glossary.md#actor-loop-terms) | Shared actor/engine execution contract |
| Timeline, step record, context reducer | Packet-local code names | Bounded trace and actor adapter details; no new durable meaning proposed |

## Experiment evidence

- **Evidence record:** `docs/evidence/2026-07-26-stateful-shared-world-execution.md`
- **Hypothesis and decision unlocked:** Whether a two-step recorded causal history is stable enough for causal branching; see the evidence record.
- **Result handoff:** Complete the record at Review and set it to `Review`; Technical Lead completes reconciliation and final status.

## Vision alignment

- **Vision behavior made observable:** A builder can run and inspect a composed shared-world scenario through a committed state change while preserving causal replay and actor isolation.
- **Classification:** `Candidate durable system foundation`
- **Reuse pressure:** A later causal-branching outcome must replay a selected state from this history; no second temporal scenario is in this slice.
- **Boundary rejection signal:** The engine must interpret clearing state/proposals or a reusable scheduler, clock, conflict model, or branch representation becomes necessary to complete two steps.

## Canonical context

- [Roadmap: Stateful shared-world execution](../roadmap.md#1-stateful-shared-world-execution).
- [Strategy: Current focus](../strategy.md#current-focus) and [target modular composition model](../strategy.md#target-modular-composition-model).
- [Requirements: Builder-controlled clearing composition](../requirements.md#builder-controlled-clearing-composition).
- [Architecture: Builder-controlled clearing composition](../architecture.md#builder-controlled-clearing-composition).
- Initial source and test entry points: `src/npc/composition.py`, `src/npc/experiments/composed_clearing.py`, and `tests/test_composition.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer guide, and only
the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Extend the existing domain-opaque composition boundary with a fixed,
  exact-two-step execution and replay path. Preserve the existing one-step API
  and tests.
- Record two ordinal step records by value. Each record includes its source
  state, every actor's simulation-derived input and retained context, bounded
  proposal, simulation resolution (including order, decisions, transitions,
  outcome, and feedback), and resulting state.
- Add an actor-declared deterministic context-reduction contract. It may use
  only the actor's previous context and its own simulation-selected feedback;
  it must not receive another actor's data or canonical state.
- Reuse the supplied clearing simulation and actors only as bounded fixture
  components. Permit exactly the continuation needed after its own step-one
  committed state; do not create a general clearing lifecycle.
- Update Requirements and Architecture only with accepted, verified behavior
  and mechanism; complete the evidence record only at Review.
- Exclude branch lineage, a third step, asynchronous scheduling, external
  storage, model calls, and changes to unrelated experiments.

## Acceptance and verification

- Write failing behavioral tests before execution logic for a two-step
  hunter/fox run: ordinals are explicit; step two's source equals step one's
  result; step one sets the trap while the fox waits; step two receives only
  each actor's retained context and new filtered view, then catches the fox;
  both steps retain declared resolution order, decisions, transitions,
  feedback, and resulting state.
- Test that changing the canonical source state changes the appropriate
  simulation-filtered input and authoritative outcome while prohibited facts
  and another actor's input, context, proposal, cognition, and feedback never
  cross an actor channel.
- Test that the full timeline is JSON-safe and replay performs zero mediation
  calls.  One-field mutations of each recorded source/resulting state, ordinal,
  retained context, actor-visible input, proposal, resolution order, decision,
  transition, outcome, and feedback must raise `CompositionError`.
- Preserve existing one-step composition tests and run `.venv/bin/pytest
  tests/test_composition.py`, then `make check` and `git diff --check`.
- For changed Markdown, run the repository's available Markdown-link check; if
  none exists, manually verify every changed relative link.

## Stop conditions

- The selected simulation or actors cannot supply a context lifecycle, order,
  conflict rule, or second-step transition without engine interpretation of
  clearing meaning.
- A context update requires another actor's channel, raw canonical state, or
  unrecorded mediation.
- Completing replay requires a general scheduler, persistence layer, branch
  model, or a new public domain contract.
- Conflicting evidence, unexpected user-owned changes, or a required new
  product/authority decision appears.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
