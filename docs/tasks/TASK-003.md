# TASK-003: Render completed fox outcomes without authority

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `01b8e9e1dc153b849beb1ed0a6441eebfe7012ef`

**Depends on:** None

**Write scope:** `src/npc/experiments/fox_outcome_rendering.py`,
`scenarios/fox_outcome_rendering.yaml`,
`tests/test_fox_outcome_rendering.py`,
`docs/evidence/2026-07-25-fox-outcome-rendering.md`,
`docs/requirements.md`, and `docs/architecture.md`

**Parallel-safe with:** None — the task adds an experiment and updates its
canonical behavior, mechanism, and evidence records.

**Durable information changed:** observed accepted behavior ->
`docs/requirements.md` under a new fox outcome-rendering section; verified
mechanism -> `docs/architecture.md` under a new fox outcome-rendering section;
experiment result -> `docs/evidence/2026-07-25-fox-outcome-rendering.md`.

**Simplifier review:** Required — the task adds an LLM-facing presentation
module and a cross-module completed-event boundary. Reject a general renderer,
dialogue system, or presentation framework.

## Outcome

Provide fixture-backed player-facing rendering after a completed fox distance
turn. The renderer sees only the finalized action and may produce only that
action's exact approved sentence; invalid, mismatched, or unavailable output
uses `The fox's response cannot be rendered.` while canonical state remains
unchanged.

## Experiment evidence

- **Evidence record:** `docs/evidence/2026-07-25-fox-outcome-rendering.md`.
- **Hypothesis and decision unlocked:** use its Hypothesis and Decision
  unlocked sections unchanged; complete Result at Review whether supporting,
  rejected, or inconclusive.
- **Result handoff:** include fixture traces, renderer call counts, and exact
  test/check commands. Do not claim a reusable presentation or dialogue system.

## Vision alignment

- **Vision behavior made observable:** a completed deterministic fox outcome
  gains a non-authoritative player-facing presentation after action and feedback
  have already finalized.
- **Classification:** `Disposable experiment scaffolding`.
- **Reuse pressure:** `Not in scope — scaffolding only`.
- **Boundary rejection signal:** useful rendering requires raw player input,
  inferred facts, action/state authority, feedback mutation, or general
  presentation infrastructure.

## Canonical context

- [Roadmap: Render a completed fox outcome as a player-facing text message](../roadmap.md#1-render-a-completed-fox-outcome-as-a-player-facing-text-message).
- [Decision: Keep shared LLM perception separate from creature authority](../decisions.md#2026-07-25-keep-shared-llm-perception-separate-from-creature-authority).
- [Architecture: Bounded fox distance feedback](../architecture.md#bounded-fox-distance-feedback).
- [Evidence: bounded fox distance-feedback loop](../evidence/2026-07-25-fox-distance-feedback.md).
- Initial entry points: `src/npc/experiments/fox_distance_feedback.py` and
  `tests/test_fox_distance_feedback.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer guide, and only
the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Add one fox-only rendering module. It may import the completed `TurnTrace`
  type from `npc.experiments.fox_distance_feedback`, but must not modify the
  distance-feedback module, its corpus, completed action, distance, or feedback
  state. Do not add a generic renderer, dialogue, state, or event framework.
- Render only an already completed action. The renderer prompt must receive no
  raw player message, perception candidate, certainty, distance, or mutable
  state; it may receive only `flee` or `do_nothing` and must say it is not
  choosing an action or asserting a world fact.
- Define a closed JSON response contract with exactly `action` and `message`.
  Accept only an action exactly equal to the completed `executed_action` and its
  exact sentence: `flee` -> `The fox flees.`; `do_nothing` -> `The fox does
  nothing.`. Mark every malformed, extra-field, action-mismatched,
  message-mismatched, or renderer-exception result invalid and return the fixed
  fallback `The fox's response cannot be rendered.` as non-authoritative text.
- The rendering trace must retain the complete canonical `TurnTrace`, prompt,
  raw renderer output (or null on exception), validation result, rendered text,
  and an explicit non-authoritative marker. Do not use rendered text to create
  or modify choice, executed action, distance, feedback, or later perception.
- Add fixed fixtures based on completed fox turns for: accepted in-range threat
  yielding `flee`; in-range non-action; initially out-of-range non-action;
  malformed or action-mismatched renderer output; and renderer failure. Use
  fixture completions, never a live model.
- Add failing behavioral tests before application logic for prompt data
  minimization, exactly one renderer call after a completed turn, both accepted
  action sentences, invalid/mismatched/failed fallback, trace completeness, and
  canonical trace equality before versus after every renderer outcome.
- At Review, update only the three named canonical records with observed,
  accepted results. Do not modify the roadmap, decisions, README, dependencies,
  distance-feedback module/corpus/tests, or project-wide abstractions.

## Acceptance and verification

- A JSON-safe rendering trace exposes the unmodified completed canonical turn,
  prompt, raw renderer output or null, validation result, rendered text, and a
  non-authoritative marker.
- Valid fixture output for a completed `flee` renders exactly `The fox flees.`;
  valid fixture output for a completed `do_nothing` renders exactly `The fox
  does nothing.` No completed non-action may render a fleeing sentence.
- Malformed, extra-field, mismatched-action, mismatched-message, or unavailable
  rendering returns `The fox's response cannot be rendered.` and leaves every
  field of the canonical turn—including action, resulting distance, and feedback
  distance—unchanged.
- The rendering prompt includes only the completed action; it contains no player
  message, candidate/evidence/certainty, or distance value. Rendering occurs
  exactly once per requested completed turn and never calls a perception sensor.
- Add behavioral tests that fail before implementation. Run
  `.venv/bin/pytest tests/test_fox_outcome_rendering.py`, existing fox-distance
  and threat test modules, `make check`, and `git diff --check`.

## Stop conditions

- Stop if strict factual text cannot be validated without re-opening raw player
  input, perception, or mutable state, or if it needs the renderer to choose an
  action; return the smallest conflicting trace and authority question.
- Stop if the scope requires changing the distance-feedback experiment, shared
  sensor, dependencies, or introducing a generic renderer/dialogue/event
  abstraction; return minimal technical evidence instead.
- Stop for unrelated user-owned changes or any required write outside scope.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
