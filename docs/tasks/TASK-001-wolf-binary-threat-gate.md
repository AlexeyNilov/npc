# TASK-001: Run an inspectable binary wolf threat gate

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `2b97e5b92aebe461f1a4f7abb16fb381d5ee9f3b`

**Depends on:** None

**Write scope:** `src/npc/experiments/wolf_threat.py`,
`scenarios/wolf_threat.yaml`, `tests/test_wolf_threat.py`, and
`docs/evidence/2026-07-25-wolf-binary-threat-gate.md`

**Parallel-safe with:** None — one writer owns the experiment and its result
record.

**Durable information changed:** Experiment result ->
`docs/evidence/2026-07-25-wolf-binary-threat-gate.md` at Review. Do not update
requirements or architecture until the Technical Lead accepts the result.

**Simplifier review:** Required — this task adds a new experiment module,
scenario, and test module. Review for an unnecessary reusable abstraction or
scope expansion.

## Outcome

A developer can run a fixed corpus through one untrusted LLM binary-threat
question and inspect its candidate, certainty, evidence, validation, expected
threat/action pair, and deterministic action. An attack is possible only after
an accepted grounded `true` candidate.

## Experiment evidence

- **Evidence record:**
  `docs/evidence/2026-07-25-wolf-binary-threat-gate.md`.
- **Hypothesis and decision unlocked:** use the record's stated binary,
  one-question hypothesis and its future perception/calibration decision.
- **Result handoff:** complete every Result field at Review, including a
  negative or inconclusive live-run result. Fixture results alone do not claim
  general model accuracy.

## Vision alignment

- **Vision behavior made observable:** an LLM operates as a narrow perception
  sensor while deterministic code retains action authority.
- **Classification:** `Disposable experiment scaffolding`.
- **Reuse pressure:** Not in scope — scaffolding only.
- **Boundary rejection signal:** needing state, dialogue, a second model call,
  world facts, a certainty threshold, or a reusable actor/perception framework
  to explain the current wolf action.

## Canonical context

- [Roadmap: Test a binary threat-perception gate](../roadmap.md#test-a-binary-threat-perception-gate).
- [Prior experiment record](../evidence/2026-07-25-wolf-affect-to-action.md),
  especially its ambiguous-label limitation.
- [Architecture: Wolf affect-to-action experiment](../architecture.md#wolf-affect-to-action-experiment).
- Initial source/test references:
  `src/npc/experiments/wolf_affect.py`, `scenarios/wolf_affect.yaml`, and
  `tests/test_wolf_affect.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer guide, and only
the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Create a separate `wolf_threat` experiment; preserve the completed
  `wolf_affect` experiment and its reproducibility record.
- Make exactly one completion call per corpus case. Its prompt asks only whether
  the message contains a credible hostile threat toward the wolf; it must not
  ask the model for an action or introduce world facts.
- Parse only a JSON object with exact keys `threat`, `certainty`, and
  `evidence`. Permit the existing transport-only JSON-fence normalization if
  copied locally; do not extract a shared helper.
- Require `threat` to be a JSON boolean, `certainty` a finite non-boolean JSON
  number in `[0, 1]`, and `evidence` a string for `true` or `null` for `false`.
  Accept `true` only when its evidence is non-empty and occurs verbatim in the
  player message. Map accepted `true` to `attack`; all other inputs map to
  `do_nothing`.
- Record certainty in the parsed candidate and trace but do not branch on it,
  impose a confidence threshold, or otherwise let it affect action.
- Check in four independent corpus cases: credible direct threat (`true`,
  `attack`), calm/friendly (`false`, `do_nothing`), fearful (`false`,
  `do_nothing`), and ambiguous (`false`, `do_nothing`). Display expected binary
  threat/action pairs in every trace.
- Add fixture tests before behavior-changing logic for accepted grounded true,
  false, malformed shapes/types, empty and ungrounded true evidence,
  out-of-range/non-finite certainty, deterministic policy, corpus coverage,
  one-call behavior, and certainty-invariance of action.
- Complete only the evidence record at Review. Explicitly exclude changes to
  trader code, persistent state, dialogue, additional actions, the existing
  affect experiment, shared abstractions, and requirement/architecture updates.

## Acceptance and verification

- Running `python -m npc.experiments.wolf_threat` prints one JSON trace per
  checked-in case with expected threat/action, raw candidate, parsed candidate,
  validation result, and deterministic action.
- Grounded accepted `true` is the sole route to `attack`; all malformed,
  out-of-range-certainty, false, and ungrounded candidates yield `do_nothing`.
- Changing only a valid candidate's certainty leaves its action unchanged.
- `tests/test_wolf_threat.py` contains failing behavior tests before the
  behavior-changing implementation and passes after it; the legacy wolf-affect
  tests continue to pass.
- Run `.venv/bin/pytest tests/test_wolf_threat.py`,
  `.venv/bin/pytest tests/test_wolf_affect.py`, `make check`, and
  `git diff --check`. Include exact results and any live-run limitation in the
  evidence record/handoff.

## Stop conditions

- Stop if "credible hostile threat toward the wolf" cannot be evaluated from
  player text alone, requires a definition beyond the roadmap, or produces a
  disputed corpus expectation.
- Stop if accepting a false candidate with `null` evidence, or rejecting
  non-null false evidence, conflicts with the required trace interpretation;
  return the alternatives to the Technical Lead rather than silently changing
  the contract.
- Stop for required scope expansion, unexpected user-owned changes, unavailable
  completion access needed for a claimed live result, or any need for an
  external mutation.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
