# TASK-001: Invoke an LLM as a non-authoritative fox outcome narrator

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `6b1d47a61844a1261678a37855bd95a698a11465`

**Depends on:** None

**Write scope:** `src/npc/experiments/fox_outcome_rendering.py`,
`tests/test_fox_outcome_rendering.py`, `scenarios/fox_outcome_rendering.yaml`,
`README.md`, `docs/requirements.md`, `docs/architecture.md`, and new
`docs/evidence/2026-07-25-fox-llm-outcome-narration.md`

**Parallel-safe with:** None — the narration trace, fixture contract, and their
canonical documentation are changed together.

**Durable information changed:**

- What must the system do? -> [Requirements](../requirements.md),
  `Non-authoritative rendering of completed fox outcomes`.
- How does the system work now? -> [Architecture](../architecture.md),
  `Non-authoritative rendering of completed fox outcomes`.
- What is this project, and how do I use it? -> [README](../../README.md),
  current-demonstration summary.
- What did a bounded experiment demonstrate or refute? -> new experiment
  evidence record.

**Simplifier review:** Required — the configured adapter becomes a new
cross-module boundary between the fox experiment and infrastructure.

## Outcome

After each completed fixture fox turn, call the configured LLM exactly once to
produce arbitrary concise player-facing narration, while retaining an
inspectable, immutable canonical turn and deterministic fallback. This lets the
developer observe actual model narration without allowing it to influence the
actor or world.

**Task-local usability contract:** narration is usable when the configured
adapter returns nonblank text of at most 280 Unicode characters. It is
intentionally not semantically validated: ungrounded flavour is permitted as
non-authoritative presentation. Unavailable, exceptional, blank, or oversized
responses use the existing deterministic fallback.

## Experiment evidence

- **Evidence record:**
  `docs/evidence/2026-07-25-fox-llm-outcome-narration.md`.
- **Hypothesis and decision unlocked:** A configured LLM can narrate the one
  completed fox action in arbitrary concise text without changing canonical
  action or feedback. The record evaluates whether this presentation boundary
  is useful enough to retain and whether later work needs factual constraints.
- **Result handoff:** At Review, complete the record with fixture results and a
  captured configured-model run for `flee`, `do_nothing`, and narrator
  failure/unusability.

## Canonical context

- [Roadmap: Invoke an LLM as a non-authoritative fox outcome narrator](../roadmap.md)
- [Decision: Render completed actor outcomes with a non-authoritative LLM narrator](../decisions.md)
- [Requirements: Non-authoritative rendering of completed fox outcomes](../requirements.md)
- [Architecture: Non-authoritative rendering of completed fox outcomes](../architecture.md)
- Initial entry points:
  `src/npc/experiments/fox_outcome_rendering.py`,
  `src/npc/infrastructure/language_model.py`,
  `tests/test_fox_outcome_rendering.py`, and
  `scenarios/fox_outcome_rendering.yaml`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer guide, and only
the context named above.

## Task-specific scope

- Keep `render_completed_turn` after `run_turn`; build its prompt from only
  `executed_action` and preserve the current frozen canonical turn by value.
- Add a fox-local adapter over `complete_text` and use it for the configured
  narrator path. It receives only the action-derived narration prompt and a
  fixed instruction that narration is presentation, not action selection or
  world state. Do not add a shared renderer or event abstraction.
- Replace the closed `action`/exact-message JSON acceptance rule with the
  task-local usability contract. Store the raw configured response or null,
  validation/failure status, rendered text, and `non_authoritative=True` in
  the JSON-safe rendering trace.
- Retain injectable fixture renderers for deterministic tests. Add fixed cases
  for free-form `flee`, free-form `do_nothing`, blank/oversized unusable output,
  and adapter failure.
- Add a runnable configured-narration fixture path that uses fixture canonical
  turns but the configured narrator, making one narrator call per completed
  case and printing the inspectable trace.
- Update the named canonical documents and create the experiment record. Do
  not modify the roadmap; completion reconciliation is the Technical Lead's
  responsibility after acceptance.

**Explicit exclusions:** narration as evidence, action selection, distance or
feedback input, state, dialogue history, player-input interpretation, semantic
fact checking, flavour restrictions, generic renderer/event/dialogue
frameworks, and changes to the completed canonical turn.

## Acceptance and verification

- A test first demonstrates the new configured-adapter seam: exactly one
  narrator call occurs after a completed turn and its prompt exposes only the
  completed action, never player text, perception candidates, certainty,
  distance, or mutable state.
- Fixture tests accept arbitrary nonblank narration for completed `flee` and
  `do_nothing`; blank, oversized, and exceptional responses return the
  deterministic fallback; every canonical-turn field remains byte-for-byte
  equivalent before and after narration.
- The configured fixture command prints canonical turn, narration prompt, raw
  response or failure, validation result, rendered text/fallback, and the
  explicit non-authoritative marker. Capture one configured-model run for each
  action and an unavailable or unusable path in the evidence record.
- Run the focused tests, then `make check` and `git diff --check`.

## Stop conditions

- The configured adapter or model endpoint is unavailable when the required
  live evidence is due; record the condition and move the task to Blocked
  rather than fabricating it.
- Any implementation path requires semantic fact checking, a second LLM call,
  player text, perception data, distance, mutable state, or a generic
  abstraction.
- A required document contradicts the selected free-form presentation policy
  or a pre-existing user change overlaps this write scope.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
