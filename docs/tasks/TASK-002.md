# TASK-002: Demonstrate bounded fox distance feedback

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `01b8e9e1dc153b849beb1ed0a6441eebfe7012ef`

**Depends on:** None

**Write scope:** `src/npc/experiments/fox_distance_feedback.py`,
`scenarios/fox_distance_feedback.yaml`,
`tests/test_fox_distance_feedback.py`,
`docs/evidence/2026-07-25-fox-distance-feedback.md`,
`docs/requirements.md`, and `docs/architecture.md`

**Parallel-safe with:** None — the task creates the experiment and updates its
canonical behavior, mechanism, and evidence records.

**Durable information changed:** observed accepted behavior ->
`docs/requirements.md` under a new fox distance-feedback section; verified
mechanism -> `docs/architecture.md` under a new fox distance-feedback section;
experiment result -> `docs/evidence/2026-07-25-fox-distance-feedback.md`.

**Simplifier review:** Required — the task adds a new module and a cross-module
sensor/policy/outcome boundary. Reject generic actor, movement, or world-state
abstractions.

## Outcome

Provide a fixed two-turn fox fixture in which authoritative distance determines
whether a player message reaches the existing threat sensor, a valid accepted
threat deterministically executes `flee`, and the resulting distance gates the
same message on the next turn. This tests whether the smallest outcome and
feedback boundary is inspectable without a framework.

## Experiment evidence

- **Evidence record:** `docs/evidence/2026-07-25-fox-distance-feedback.md`.
- **Hypothesis and decision unlocked:** use its Hypothesis and Decision
  unlocked sections unchanged; complete Result at Review whether supporting,
  rejected, or inconclusive.
- **Result handoff:** include fixture traces, sensor call counts, and exact test
  and check commands. Do not claim reusable actor or movement infrastructure.

## Vision alignment

- **Vision behavior made observable:** one deterministic fox turn gains an
  authoritative perception constraint, action outcome, and next-turn feedback.
- **Classification:** `Disposable experiment scaffolding`.
- **Reuse pressure:** `Not in scope — scaffolding only`.
- **Boundary rejection signal:** a readable implementation needs inferred world
  facts, model-selected reachability/state changes, or generic actor, movement,
  or world machinery.

## Canonical context

- [Roadmap: Demonstrate a bounded fox distance-feedback loop](../roadmap.md#1-demonstrate-a-bounded-fox-distance-feedback-loop).
- [Decision: Keep shared LLM perception separate from creature authority](../decisions.md#2026-07-25-keep-shared-llm-perception-separate-from-creature-authority).
- [Architecture: Binary perception pattern](../architecture.md#binary-perception-pattern) and [Shared target-aware threat detection](../architecture.md#shared-target-aware-threat-detection).
- [Evidence: shared target-aware threat detection](../evidence/2026-07-25-shared-threat-detection.md).
- Initial entry points: `src/npc/experiments/threat_detection.py`,
  `src/npc/experiments/fox_threat.py`, and `tests/test_fox_threat.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer guide, and only
the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Add one fox-only experiment wrapper. It may import and call the established
  `perceive_threat` sensor but must not modify that sensor or the existing fox
  threat wrapper. It must use local explicit functions/types only; do not add a
  shared actor, state, movement, or world model.
- Use integer distance units, a hearing range of 10, audible-at-boundary
  convention `distance <= 10`, and a flee displacement of 5. Treat all three
  as fixed deterministic experiment rules. The model must not receive or alter
  them.
- Before calling the sensor on every turn, determine hearing from the starting
  distance. For an inaudible turn, make zero sensor calls; retain null
  candidate-related fields; select and execute `do_nothing`; and preserve
  distance.
- For an audible turn, call the sensor exactly once, retain raw candidate,
  parsed candidate, and validation result, and reuse the existing fox policy:
  only an accepted `threat: true` selects and executes `flee`; every other
  result selects and executes `do_nothing`. `flee` alone increases distance by
  5. Record the resulting distance as feedback for the following turn.
- Add one YAML corpus with: (1) a two-turn direct threat beginning at 10, whose
  first valid candidate causes `10 -> 15` and whose identical second message is
  inaudible with no sensor call; (2) an audible malformed or ungrounded true
  candidate that leaves distance unchanged; and (3) an initially out-of-range
  direct threat that makes no sensor call or movement. Use fixture completions,
  never a live model.
- Add failing behavioral tests before application logic for boundary hearing,
  the two-turn feedback handoff, exactly one call for each audible turn and zero
  for each inaudible turn, accepted/rejected branches, malformed, invalid-
  certainty, empty-evidence, and ungrounded true candidates, no movement on
  every failure path, trace completeness, and corpus expectations.
- At Review, update only the three named canonical records with observed,
  accepted results. Do not change the roadmap, decisions, README, dependencies,
  existing sensors/wrappers/corpora, or project-wide abstractions.

## Acceptance and verification

- Each JSON-safe turn trace has the player message, starting distance, hearing
  result, sensor-call status, raw/parsed/validation perception fields when
  called, deterministic choice, executed action, resulting distance, and
  feedback distance.
- The boundary fixture confirms `10` is audible. An accepted grounded threat
  then executes `flee`, produces distance `15`, and causes the repeated direct
  threat to be inaudible, skipped before perception, and unchanged at `15`.
- Initially out-of-range messages make zero sensor calls, retain null
  candidate-related fields, execute `do_nothing`, and preserve distance.
  Malformed, invalid-certainty, empty-evidence, and ungrounded true audible
  candidates likewise execute `do_nothing` and preserve distance.
- Add behavioral tests that fail before implementation. Run
  `.venv/bin/pytest tests/test_fox_distance_feedback.py`, existing threat test
  modules, `make check`, and `git diff --check`.

## Stop conditions

- Stop if a two-turn trace cannot distinguish a hearing-gated skipped sensor
  call from a sensor rejection, or if authoritative distance must be inferred
  from player or model text; return the smallest conflicting trace and choice.
- Stop if the scope requires changing the threat detector, existing wrappers,
  dependencies, or introducing a generic actor/movement/world abstraction;
  return the minimal technical evidence instead.
- Stop for unrelated user-owned changes or any required write outside scope.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
