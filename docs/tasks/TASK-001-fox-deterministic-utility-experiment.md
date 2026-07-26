# TASK-001: Reproducible fox safety-versus-food utility experiment

**Status:** Review

**Owner:** Implementer

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `fab73f6`

**Depends on:** None

**Write scope:**
`src/npc/experiments/fox_deterministic_utility.py`,
`tests/test_fox_deterministic_utility.py`,
`scenarios/fox_deterministic_utility.yaml`, and
`docs/evidence/2026-07-26-fox-deterministic-utility.md`.

**Parallel-safe with:** None — the experiment record is updated at Review and
the new module consumes the current fox sensors.

**Durable information changed:** Experiment result ->
`docs/evidence/2026-07-26-fox-deterministic-utility.md` at Review. Do not
change Requirements, Architecture, Strategy, Decisions, or Roadmap in this
task; route accepted findings to the Technical Lead.

**Simplifier review:** Required — this packet adds a module, fixture loader,
and trace boundary. Review the diff for any abstraction beyond fox-local
experiment scaffolding.

## Outcome

Provide a runnable checked-in corpus that proves or refutes the planned
deterministic hunger/utility hypothesis through JSON-safe, replayable fox turn
traces. It matters because the next capability-path decision depends on whether
one retained motive can alter an otherwise equivalent threat-and-food conflict
without expanding LLM authority.

## Experiment evidence

- **Evidence record:**
  `docs/evidence/2026-07-26-fox-deterministic-utility.md`.
- **Hypothesis and decision unlocked:** use the record's `Hypothesis`,
  `Decision unlocked`, and `Signals and stop rule` exactly; do not reinterpret
  its fixed scores, tie order, or state transition.
- **Result handoff:** at Review, complete every `Result` field with exact
  commands and outcomes, including a negative or inconclusive result.

## Canonical context

- `docs/evidence/2026-07-26-fox-deterministic-utility.md` — approved
  experiment contract.
- `docs/strategy.md#current-direction` and `docs/roadmap.md#ordered-future-outcomes`.
- `docs/decisions.md#2026-07-26-test-deterministic-utility-selection-before-behavioural-randomness`.
- `docs/architecture.md#bounded-fox-distance-feedback` — retain the current
  sensor and movement contracts, but do not modify that delivery.
- Initial source/test entry points:
  `src/npc/experiments/fox_distance_feedback.py`,
  `src/npc/experiments/threat_detection.py`,
  `src/npc/experiments/food_offer_detection.py`, and
  `tests/test_fox_distance_feedback.py`.

## Task-specific scope

- Create one new fox-local module. It may use the existing independent
  perception functions and their existing `Completion` type, but it must not
  call `fox_distance_feedback.run_turn`, because that function owns the
  supported fixed threat-first policy.
- Validate `starting_distance` with the existing non-boolean integer minimum
  contract and validate `starting_hunger` as a non-boolean integer in
  `[0, 100]`, before calling either sensor or executing any action.
- Preserve hearing gating, both independent sensor calls, candidate validation,
  action displacement, and distance feedback exactly as the existing fox
  delivery. An inaudible turn must score only `do_nothing` and must not call a
  sensor.
- Implement only the approved scores: accepted threat gives `flee=60`,
  accepted food offer gives `approach=starting_hunger`, `do_nothing=1`, and
  all unavailable candidates score `0`. Select the maximum with the fixed
  `flee`, `approach`, `do_nothing` tie order.
- Advance hunger once for every valid completed turn with
  `min(100, starting_hunger + 10)`; no perception or action changes hunger by
  any other mechanism.
- Expose an immutable JSON-safe trace sufficient to replay the record's
  required scenarios: starting/resulting hunger, per-action utilities,
  selected score and tie resolution, accepted/rejected perception status,
  action, and distance feedback. Keep raw/parsed perception trace data if
  needed to show existing validation; do not add model-generated state.
- Add the named YAML corpus and a command-line module entry point that prints
  one JSON trace per turn. Keep the fixture completion local and deterministic.
- Do not modify the current `fox_distance_feedback` module, its corpus, its
  requirements, or the interactive narrator. Do not introduce consumption,
  inventory, reachability, randomness, an actor/need/utility framework, a
  registry, another actor, dependencies, or public reuse claims.

## Acceptance and verification

- Before behavior-changing application code, add failing behavioral tests for:
  low- and high-hunger otherwise equivalent accepted conflicts; the safety
  tie; retained hunger across the required three turns; invalid hunger failing
  before model calls; rejected perceptions contributing no score; inaudible
  sensor skipping; and reproducible JSON-safe corpus traces.
- The corpus contains exactly the baseline, single-motive, two fixed-conflict,
  retained-state, and rejected-perception cases required by the evidence
  record. Assert its expected action, distance, and hunger transitions.
- Run `.venv/bin/pytest tests/test_fox_deterministic_utility.py`, then
  `.venv/bin/python -m npc.experiments.fox_deterministic_utility`, `make
  check`, and `git diff --check`.
- At Review, a Simplifier verifies that the implementation remains a single
  fox-local experiment and no generalized boundary was introduced.

## Stop conditions

- Any required behavior conflicts with the planned evidence record or current
  sensor/distance contract.
- The task requires a new data meaning, model-provided score/action/state,
  consumption/reachability fact, or a reusable abstraction.
- The PM evidence record changes materially while work is in progress.
- Missing fixture, dependency, or a user-owned working-tree change prevents
  safe implementation.

## Handoff

**Status and outcome:** Review — supported. The checked-in corpus produces
both low- and high-hunger conflict outcomes and the corrected retained-state
safety-tie-to-approach transition without expanding LLM authority.

**Changed files and ownership impact:** Added the fox-local experiment module,
its tests, and its deterministic YAML corpus. Recorded the observed experiment
result only in its canonical evidence record; no Requirements, Architecture,
Strategy, Decisions, or Roadmap facts changed.

**Verification:** Test-first failure was observed before implementation (the
then-unresolved retained-state contract selected `flee` at hunger 60). After
the approved correction, `.venv/bin/pytest
tests/test_fox_deterministic_utility.py` passed (9 tests), the module printed
9 JSON traces, `make check` passed (Ruff, mypy, 35 tests), and `git diff
--check` passed.

**Assumptions, risks, and next action:** The Product Manager-approved initial
hunger correction from `40` to `50` preserves the fixed scores and tie rule;
the final action is reachable at hunger `70`. Simplifier review remains
required before Technical Lead acceptance.
